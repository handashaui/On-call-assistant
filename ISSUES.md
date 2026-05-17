# Improvement Backlog

1. Upgrade the V3 agent to a real ReAct-style loop with multiple tools, while keeping `readFile` as the only required tool for the interview spec.
2. Add a small retrieval evaluation set and tune V2 hybrid ranking weights with metrics instead of fixed `0.7/0.3`.
3. Add section-level source citations to V3 answers so users can see exactly which SOP paragraph was used.
4. Persist parsed documents and embeddings to SQLite or a local vector index instead of rebuilding on every startup.
5. Add a cleaner frontend with source filters, highlighted snippets, and better tool-call visualization.
6. Add GitHub Actions to run `pytest` on every push.
