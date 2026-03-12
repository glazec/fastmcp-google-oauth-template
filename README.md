# FastMCP Google OAuth Template

A minimal FastMCP server template with:
- Google OAuth authentication
- Encrypted persistent storage (survives Railway deploys)
- Ready to deploy on Railway

## Quick Start

### 1. Copy the template

```bash
cp .env.example .env
```

Edit `.env` with your values.

### 2. Install dependencies

```bash
uv sync
```

### 3. Run locally

```bash
uv run python main.py
```

OAuth data is persisted to `./oauth_data/` automatically.

---

## Google OAuth Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/) → APIs & Services → Credentials
2. Create an **OAuth 2.0 Client ID** (Web application)
3. Add authorized redirect URIs:
   - `https://your-service.up.railway.app/auth/callback`
   - `http://localhost:8000/auth/callback` (for local dev)
4. Copy the **Client ID** and **Client Secret** into your `.env`

---

## Railway Deployment

### First-time setup

1. **Create a Railway service** pointing to this repo.

2. **Add a Volume** to the service:
   - Mount path: `/data`
   - Size: 1 GB (~$0.25/month)

3. **Set environment variables** in Railway:

   | Variable | Value |
   |---|---|
   | `FASTMCP_JWT_SIGNING_KEY` | Long random string — **never change in production** |
   | `GOOGLE_CLIENT_ID` | From Google Cloud Console |
   | `GOOGLE_CLIENT_SECRET` | From Google Cloud Console |
   | `BASE_URL` | `https://your-service.up.railway.app` |
   | `OAUTH_STORAGE_PATH` | `/data/oauth` |

4. **Deploy.** OAuth credentials will now persist across deploys.

### Why the volume?

FastMCP stores OAuth client registrations and tokens on disk. Without a persistent volume, every Railway deploy creates a fresh filesystem — clients (e.g. Claude) would need to re-authenticate after every deploy.

### Adding to Claude

In Claude's MCP settings, add:
```
https://your-service.up.railway.app/mcp
```

---

## Adding Tools

Edit `main.py` and add tools below the marked section:

```python
@mcp.tool
def my_tool(param: str) -> str:
    """Description shown to the AI."""
    return f"Result for {param}"
```

## Environment Variables Reference

| Variable | Required | Description |
|---|---|---|
| `FASTMCP_JWT_SIGNING_KEY` | Yes | Signs JWTs. Must be stable across deploys. |
| `GOOGLE_CLIENT_ID` | Yes | Google OAuth client ID |
| `GOOGLE_CLIENT_SECRET` | Yes | Google OAuth client secret |
| `BASE_URL` | Yes | Public URL of the deployed server |
| `OAUTH_STORAGE_PATH` | No | Storage path (default: `./oauth_data`) |
