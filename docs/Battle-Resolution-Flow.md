START

```mermaid

flowchart TD

A[Player Selects Army]

A --> B[Load Troop Deployment]

B --> C{Deployment Valid?}

C -->|Yes| D[Create Battle]

C -->|No| E[Reject Battle]

```mermaid
