# On-Call Assistant

FastAPI implementation for the three-phase On-Call Assistant interview project.

## Phases

- V1: structured HTML parsing plus weighted keyword search.
- V2: chunk-level embedding retrieval with hybrid semantic and keyword ranking.
- V3: on-call agent with a constrained `readFile(fname)` tool and visible tool calls.

## Run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
./run.sh
```

Open:

- `http://127.0.0.1:8000/v1` keyword search
- `http://127.0.0.1:8000/v2` semantic search
- `http://127.0.0.1:8000/v3` on-call agent

The service loads `data/*.html` at startup.
V2 builds an in-memory chunk embedding index during startup. If `sentence-transformers`
cannot load `BAAI/bge-small-zh-v1.5`, the app falls back to a deterministic local
hashing embedding so the demo still runs offline.

## Architecture

- `app/services/html_parser.py`: cleans SOP HTML and extracts structured sections.
- `app/services/keyword_search.py`: V1 weighted keyword retrieval.
- `app/services/semantic_search.py`: V2 chunk embedding index and cosine search.
- `app/services/hybrid_search.py`: combines semantic and keyword scores.
- `app/services/agent.py`: V3 Agent workflow and `readFile` tool.

## API

```bash
curl -X POST http://127.0.0.1:8000/v1/documents \
  -H 'Content-Type: application/json' \
  -d '{"id":"sop-001","html":"<html><title>demo</title><body>OOM</body></html>"}'

curl 'http://127.0.0.1:8000/v1/search?q=OOM'
curl 'http://127.0.0.1:8000/v2/search?q=服务器挂了'
curl -X POST http://127.0.0.1:8000/v3/chat \
  -H 'Content-Type: application/json' \
  -d '{"message":"数据库主从延迟超过30秒怎么处理？"}'
```

## Test

```bash
pytest
```
