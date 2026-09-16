from dataclasses import dataclass
from pathlib import Path
from ..errors import AuthenticationError

@dataclass(frozen=True)
class PlaywrightSessionAuth:
    path: Path

    def storage_state_path(self) -> str:
        if not self.path.exists():
            raise AuthenticationError(f"ServiceNow session file not found: {self.path}")
        return str(self.path)
