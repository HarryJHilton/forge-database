# Schema Overview

This document provides a high-level overview of the Forge database schema, including core tables, reporting views and stored procedures.

## Core Tables

- forge_eras_normalised (Canonical Era Dimension)
- forge_ages (Reporting Age Reference)
- forge_eras (Legacy Lookup)
- forge_great_buildings (Great Building Source Data)

## Views

- forge_gb_base (Great Building Reporting View)
- forge_dashboard (Reporting Dashboard View)
- forge_dashboard_dynamic (Dynamic Dashboard View)
- forge_efficiency_rank (Efficiency Ranking View)

## Stored Procedures

- load_battle_from_deployment (Battle loader and setup)
- resolve_battle (Battle resolution engine)

