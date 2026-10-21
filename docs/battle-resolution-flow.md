START

```mermaid

flowchart TD

A[Player]
A --> B{Deployment Valid?}

B -->|Yes| C[Create Battle]
B -->|No| D[Reject Battle]


```
