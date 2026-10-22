# Test

```mermaid

flowchart TD

A[Player Army]

A --> B{Deployment Valid?}

B -->|No| C[Reject Battle]

B -->|Yes| D[Battle Begins]

D --> E[Round 1]
E --> F[Round 2]
F --> G[Winner]
```
