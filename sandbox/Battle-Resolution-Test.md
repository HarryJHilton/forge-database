# Test

```mermaid

flowchart LR

subgraph Database
    A[forge_great_buildings]
    B[forge_ages]
end

subgraph Views
    C[forge_gb_base]
    D[forge_dashboard]
end

A --> C
B --> C
B --> D
```
