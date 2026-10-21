Battle Resolution Flow
flowchart TD

    A[Player Selects Army]

    A --> B[Load Troop Deployment]
    B --> C[Validate Units]

    C --> D{Deployment Valid?}

    D -->|No| E[Reject Battle]
    D -->|Yes| F[Create Battle Record]

    F --> G[Load Battle Round]

    G --> H{Attacker Turn?}

    H -->|Yes| I[Select Attacking Unit]
    I --> J[Calculate Attack]
    J --> K[Apply Damage]

    H -->|No| L[Select Defending Unit]
    L --> M[Calculate Defence]
    M --> N[Apply Damage]

    K --> O{Units Remaining?}
    N --> O

    O -->|Yes| G
    O -->|No| P[Determine Winner]

    P --> Q[Calculate Rewards]

    Q --> R[Update Battle Statistics]
    R --> S[Store Battle Results]
    S --> T[Battle Complete]

    classDef process fill:#d1ecf1,stroke:#0c5460;
    classDef decision fill:#fff3cd,stroke:#856404;
    classDef outcome fill:#d4edda,stroke:#155724;

    class A,B,C,F,G,I,J,K,L,M,N,Q,R,S process;
    class D,H,O decision;
    class E,P,T outcome;
