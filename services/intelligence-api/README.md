# FashionOS Intelligence API — MVP Skeleton

This is the first executable backend slice for the Studio Brain integration.

Implemented:
- FastAPI app shell
- customer-safe task creation endpoint
- private brain health endpoint
- private deterministic Markdown brain index
- private compact retrieval endpoint with internal unit traceability
- initial tests for preservation retrieval and public provider secrecy

Not implemented yet:
- database persistence
- GitHub remote sync/webhook
- vector/semantic embeddings
- async worker queue
- executor/model gateway
- QC runtime
- authentication/authorization
- website crawler

Run locally from this directory:

```bash
pip install -e '.[test]'
FASHIONOS_BRAIN_ROOT=../.. uvicorn fashionos_intelligence.main:app --app-dir src --reload
pytest
```

The deterministic lexical retriever is an MVP bootstrap. It is intentionally simple and traceable; later semantic retrieval must preserve exact internal evidence IDs and authority rules.
