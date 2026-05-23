# TASKS

## Create `/solve` Route

1. Accepts either the JSON schema above or a plain sentence.
2. If plain text → pipe through LLM → produce schema.
3. Push the schema + job ID onto SQS with a reply‑to SNS topic or WebSocket.

## Worker Lambda/Batch

1. Pull job, map kind → solver engine.
2. Run optimisation, capture result & stats.
3. Persist to Dynamo (userdata) and dump full artefacts (logs, CSV solution, PNG plot) to S3 under results/{id}/.

## Callback / Polling Endpoint

1. `/results/{id}` returns status: `QUEUED | RUNNING | SUCCEEDED | FAILED` plus payload.

## Graph‑Specific Module

1. Implement Dijkstra, A*, Bellman‑Ford with NetworkX.
2. Show JSON input shape: `{ "graph": { "nodes":[...], "edges":[...] }, "source":"A", "target":"B" }`.

## Tests and Docs

1. `PyTest` for solver wrappers.
2. `pydantic` models for all request/response bodies (you already started this pattern).
3. Autodoc with mkdocs‑material, publish to GitHub Pages.

## Cost/Scale Considerations

1. If QP/LP jobs become large, spawn AWS Batch (Fargate) instead of Lambda.
2. Use Step Functions for >15‑minute workflows.
