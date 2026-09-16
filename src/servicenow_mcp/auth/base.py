from typing import Protocol

class AuthProvider(Protocol):
    """Provides authentication state to a ServiceNow transport."""
    def storage_state_path(self) -> str: ...
