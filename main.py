from dotenv import load_dotenv
load_dotenv()

from fastmcp import FastMCP
from fastmcp.server.auth.providers.google import GoogleProvider
from fastmcp.server.dependencies import get_access_token
from key_value.aio.stores.disk import DiskStore
from key_value.aio.wrappers.encryption import FernetEncryptionWrapper
import os
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# A stable JWT signing key ensures issued tokens stay valid across deploys.
# Set FASTMCP_JWT_SIGNING_KEY in your environment to a long random string.
# NEVER change this in production — it invalidates all existing client tokens.
_jwt_signing_key = os.environ["FASTMCP_JWT_SIGNING_KEY"]

# Persistent OAuth storage.
# Railway: set OAUTH_STORAGE_PATH=/data/oauth (mount a volume at /data).
# Local: falls back to ./oauth_data automatically.
_oauth_storage_path = Path(os.environ.get("OAUTH_STORAGE_PATH", "./oauth_data"))
_oauth_storage_path.mkdir(parents=True, exist_ok=True)

_client_storage = FernetEncryptionWrapper(
    key_value=DiskStore(directory=str(_oauth_storage_path)),
    source_material=_jwt_signing_key,
    salt="fastmcp-storage-encryption-key",
)

# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

auth_provider = GoogleProvider(
    client_id=os.environ["GOOGLE_CLIENT_ID"],
    client_secret=os.environ["GOOGLE_CLIENT_SECRET"],
    base_url=os.environ["BASE_URL"],  # e.g. https://your-service.up.railway.app
    required_scopes=[
        "openid",
        "https://www.googleapis.com/auth/userinfo.email",
    ],
    allowed_client_redirect_uris=[
        "https://claude.ai/api/mcp/auth_callback",
        "http://localhost:*",
    ],
    redirect_path="/auth/callback",
    client_storage=_client_storage,
    jwt_signing_key=_jwt_signing_key,
)

mcp = FastMCP(name="My MCP Server", auth=auth_provider)

# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------

@mcp.tool
async def get_user_info() -> dict:
    """Returns information about the authenticated Google user."""
    token = get_access_token()
    return {
        "google_id": token.claims.get("sub"),
        "email": token.claims.get("email"),
        "name": token.claims.get("name"),
        "picture": token.claims.get("picture"),
    }


@mcp.tool
def get_version() -> str:
    """Returns the server version."""
    return "0.1.0"


# ---------------------------------------------------------------------------
# Add your tools below
# ---------------------------------------------------------------------------

# @mcp.tool
# def my_tool(param: str) -> str:
#     """Description of what this tool does."""
#     return f"Result for {param}"


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    mcp.run(transport="http", port=8000, host="0.0.0.0")
