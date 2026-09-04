# Phase 0 probes

`mcp_probe_server.py` is a temporary localhost-only MCP Streamable HTTP probe.
It exposes only `phase0_ping`, returns a fixed response, and records method names
plus request IDs without request bodies or secrets.

Run:

```bash
python3 phase0/mcp_probe_server.py
```

Health check:

```bash
curl http://127.0.0.1:18080/health
```

This probe is audit infrastructure only. It must not be reused as the production
state service without authentication, authorization, rate limiting, migrations,
backup, and a security review.
