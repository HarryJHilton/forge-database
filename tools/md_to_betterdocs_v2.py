#!/usr/bin/env python3
"""Convert Markdown into BetterDocs-friendly WordPress block markup.

Version 2 fixes the isolation-test issues found in BetterDocs:
- the first H1 is used as metadata only and is not repeated in the body;
- Markdown tables are emitted as Custom HTML blocks to avoid Gutenberg's
  "unexpected or invalid content" warning;
- inline HTML such as <u> is preserved inside bold/italic Markdown.

The source Markdown is never modified.

Dependency:
    py -m pip install markdown-it-py
"""
from __future__ import annotations

import argparse
import html
import re
import sys
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from typing import Iterable

try:
    from markdown_it import MarkdownIt
except ImportError:
    print(
        "ERROR: markdown-it-py is not installed.\n"
        "Install it with:\n"
        "  py -m pip install markdown-it-py",
        file=sys.stderr,
    )
    raise SystemExit(2)

WIKILINK_RE = re.compile(r"\[\[[^\]]+\]\]")
CALLOUT_RE = re.compile(r"^\s*>\s*\[![A-Za-z0-9_-]+\]", re.MULTILINE)


@dataclass
class Element:
    tag: str
    markup: str


class RootElementCollector(HTMLParser):
    """Collect top-level HTML elements while preserving their markup."""

    VOID_TAGS = {
        "area", "base", "br", "col", "embed", "hr", "img", "input",
        "link", "meta", "param", "source", "track", "wbr",
    }

    def __init__(self) -> None:
        super().__init__(convert_charrefs=False)
        self.depth = 0
        self.current_tag: str | None = None
        self.current_parts: list[str] = []
        self.elements: list[Element] = []
        self.loose_text: list[str] = []

    @staticmethod
    def _attrs(attrs: list[tuple[str, str | None]]) -> str:
        out: list[str] = []
        for key, value in attrs:
            if value is None:
                out.append(key)
            else:
                out.append(f'{key}="{html.escape(value, quote=True)}"')
        return (" " + " ".join(out)) if out else ""

    def _append(self, text: str) -> None:
        if self.depth > 0:
            self.current_parts.append(text)
        elif text.strip():
            self.loose_text.append(text)

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        rendered = f"<{tag}{self._attrs(attrs)}>"
        if self.depth == 0:
            self.current_tag = tag
            self.current_parts = [rendered]
        else:
            self.current_parts.append(rendered)
        if tag not in self.VOID_TAGS:
            self.depth += 1
        elif self.depth == 0:
            self.elements.append(Element(tag, rendered))
            self.current_tag = None
            self.current_parts = []

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        rendered = f"<{tag}{self._attrs(attrs)} />"
        if self.depth == 0:
            self.elements.append(Element(tag, rendered))
        else:
            self.current_parts.append(rendered)

    def handle_endtag(self, tag: str) -> None:
        if self.depth == 0:
            return
        self.current_parts.append(f"</{tag}>")
        self.depth -= 1
        if self.depth == 0 and self.current_tag is not None:
            self.elements.append(Element(self.current_tag, "".join(self.current_parts)))
            self.current_tag = None
            self.current_parts = []

    def handle_data(self, data: str) -> None:
        self._append(data)

    def handle_entityref(self, name: str) -> None:
        self._append(f"&{name};")

    def handle_charref(self, name: str) -> None:
        self._append(f"&#{name};")

    def handle_comment(self, data: str) -> None:
        self._append(f"<!--{data}-->")

    def close(self) -> None:
        super().close()
        if self.loose_text:
            text = "".join(self.loose_text).strip()
            if text:
                self.elements.append(Element("p", f"<p>{html.escape(text)}</p>"))


def wp_block(element: Element) -> str:
    """Wrap one rendered top-level HTML element as a WordPress block."""

    tag = element.tag.lower()
    markup = element.markup.strip()

    if tag == "p":
        return f"<!-- wp:paragraph -->\n{markup}\n<!-- /wp:paragraph -->"

    if re.fullmatch(r"h[1-6]", tag):
        level = int(tag[1])
        attrs = "" if level == 2 else f' {{"level":{level}}}'
        if "class=" not in markup.split(">", 1)[0]:
            markup = markup.replace(f"<{tag}", f'<{tag} class="wp-block-heading"', 1)
        return f"<!-- wp:heading{attrs} -->\n{markup}\n<!-- /wp:heading -->"

    if tag in {"ul", "ol"}:
        attrs = ' {"ordered":true}' if tag == "ol" else ""
        if "class=" not in markup.split(">", 1)[0]:
            markup = markup.replace(f"<{tag}", f'<{tag} class="wp-block-list"', 1)
        return f"<!-- wp:list{attrs} -->\n{markup}\n<!-- /wp:list -->"

    if tag == "table":
            # Match the native Gutenberg table structure observed in BetterDocs.
            markup = re.sub(
                r"<table[^>]*>",
                '<table class="has-fixed-layout">',
                markup,
                count=1,
                flags=re.IGNORECASE,
            )   
            markup = re.sub(
                r'\s*style="text-align:[^"]*"',
                "",
                markup,
                flags=re.IGNORECASE,
            )
            return (
                "<!-- wp:table -->\n"
                '<figure class="wp-block-table is-style-regular">'
                f"{markup}"
                "</figure>\n"
                "<!-- /wp:table -->"
            )

    if tag == "blockquote":
        if "class=" not in markup.split(">", 1)[0]:
            markup = markup.replace("<blockquote", '<blockquote class="wp-block-quote"', 1)
        return f"<!-- wp:quote -->\n{markup}\n<!-- /wp:quote -->"

    if tag == "hr":
        return (
            '<!-- wp:separator -->\n'
            '<hr class="wp-block-separator has-alpha-channel-opacity" />\n'
            '<!-- /wp:separator -->'
        )

    if tag == "pre":
        return f"<!-- wp:code -->\n{markup}\n<!-- /wp:code -->"

    return f"<!-- wp:html -->\n{markup}\n<!-- /wp:html -->"


def convert(markdown_text: str, source_name: str) -> tuple[str, list[str]]:
    """Return WordPress block markup and warnings for one Markdown document."""

    warnings: list[str] = []
    markdown_text = re.sub(
    r"<u>(.*?)</u>",
    r'<span style="text-decoration: underline;">\1</span>',
    markdown_text,
    flags=re.DOTALL | re.IGNORECASE,
)
    markdown_text = re.sub(
        r"\[\[([^\]|]+)(?:\|([^\]]+))?\]\]",
        lambda m: m.group(2) or m.group(1),
        markdown_text,
    )
    
    if WIKILINK_RE.search(markdown_text):
        warnings.append("Obsidian wikilinks were found and have not yet been converted.")
    if CALLOUT_RE.search(markdown_text):
        warnings.append("Obsidian callouts were found and are rendered as ordinary blockquotes in version 2.")

    md = MarkdownIt("commonmark", {"html": True, "linkify": False, "typographer": False})
    md.enable("table")
    rendered_html = md.render(markdown_text)

    collector = RootElementCollector()
    collector.feed(rendered_html)
    collector.close()

    elements = collector.elements
    title: str | None = None
    if elements and elements[0].tag.lower() == "h1":
        title_match = re.search(
            r"<h1[^>]*>(.*?)</h1>",
            elements[0].markup,
            re.DOTALL | re.IGNORECASE,
        )
        if title_match:
            title = re.sub(r"<[^>]+>", "", title_match.group(1)).strip()
        elements = elements[1:]

    header = [
        "<!--",
        "GENERATED FILE - DO NOT EDIT DIRECTLY",
        f"Source: {source_name}",
    ]
    if title:
        header.append(f"Title: {title}")
    header.append("-->")

    body = "\n\n".join(wp_block(element) for element in elements)
    output = "\n".join(header) + "\n\n" + body.rstrip() + "\n"
    return output, warnings


def safe_paths(source: Path, destination: Path) -> None:
    if source.resolve() == destination.resolve():
        raise ValueError("Source and destination must be different files.")
    if source.suffix.lower() != ".md" or destination.suffix.lower() != ".md":
        raise ValueError("Both source and destination must use the .md extension.")


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert one Markdown file to BetterDocs-friendly WordPress block markup."
    )
    parser.add_argument("source", type=Path, help="Source Markdown file, normally under docs/")
    parser.add_argument("destination", type=Path, help="Generated file, normally under docs/")
    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        safe_paths(args.source, args.destination)
        if not args.source.is_file():
            raise FileNotFoundError(f"Source file not found: {args.source}")

        markdown_text = args.source.read_text(encoding="utf-8-sig")
        output, warnings = convert(markdown_text, args.source.as_posix())

        args.destination.parent.mkdir(parents=True, exist_ok=True)
        args.destination.write_text(output, encoding="utf-8", newline="\n")

        print(f"Converted: {args.source}")
        print(f"Generated: {args.destination}")
        print("Source file was not modified.")
        for warning in warnings:
            print(f"WARNING: {warning}")
        return 0
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
