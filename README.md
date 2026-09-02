# triager-app

A simple Copilot plugin that triages GitHub issues.

## Run locally

```bash
python -m triager_app.server --host 127.0.0.1 --port 8000
```

The plugin exposes:

- `GET /.well-known/ai-plugin.json` for plugin metadata
- `GET /openapi.yaml` for the OpenAPI contract
- `POST /triage` to suggest labels, priority, type, summary, and rationale

Example request:

```bash
curl -X POST http://127.0.0.1:8000/triage \
  -H 'Content-Type: application/json' \
  -d '{"title":"Crash during setup","body":"Install fails with an error"}'
```

## Test

```bash
python -m unittest discover
```
