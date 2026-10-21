# Test

```mermaid
flowchart TD
A --> BA[(forge_eras_normalised)]

A --> B[(forge_ages)]

B --> C[forge_dashboard]

flowchart TD
subgraph Setup
    A[Select Army]
    B[Validate Army]
end

```
