# FastMCP Google OAuth Template — Claude Code Guide

## Key Files

- `main.py` — Server entry point: FastMCP setup, Google OAuth config, tools
- `pyproject.toml` — Dependencies (fastmcp, httpx)
- `.env.example` — Environment variable reference

## Development Commands

```bash
uv sync                  # Install dependencies
uv run python main.py    # Run server locally
```

## Architecture

- **Framework**: FastMCP (wraps MCP SDK)
- **Auth**: Google OAuth via `GoogleProvider`
- **Token storage**: `DiskStore` + `FernetEncryptionWrapper` from `key_value` library
  - Local: `./oauth_data/`
  - Production: Railway Volume at `/data/oauth` (set via `OAUTH_STORAGE_PATH` env var)

## Environment Variables

| Variable | Purpose |
|---|---|
| `FASTMCP_JWT_SIGNING_KEY` | Signs JWTs; must be stable across deploys or all tokens invalidate |
| `GOOGLE_CLIENT_ID` | Google OAuth client ID |
| `GOOGLE_CLIENT_SECRET` | Google OAuth client secret |
| `BASE_URL` | Public URL of deployed server |
| `OAUTH_STORAGE_PATH` | OAuth credential storage path (Railway: `/data/oauth`, local: `./oauth_data`) |

## Adding New Tools

Add `@mcp.tool` decorated functions in `main.py` below the marked section. Tools are automatically registered with FastMCP.

## OAuth Credential Persistence

OAuth data is stored via `key_value.DiskStore` encrypted with Fernet (AES-128). The encryption key is derived from `FASTMCP_JWT_SIGNING_KEY`.

**Do not change `FASTMCP_JWT_SIGNING_KEY` in production** — this would invalidate all existing client tokens.
