from dataclasses import dataclass
import os
from pathlib import Path
from dotenv import load_dotenv

# Load a local .env when present. Existing environment variables keep priority.
load_dotenv()

@dataclass(frozen=True)
class Settings:
    base_url: str = os.getenv("SERVICENOW_BASE_URL", "").rstrip("/")
    session_file: Path = Path(os.getenv("SERVICENOW_SESSION_FILE", "session.json"))
    host: str = os.getenv("SERVICENOW_MCP_HOST", "127.0.0.1")
    port: int = int(os.getenv("SERVICENOW_MCP_PORT", "3310"))
