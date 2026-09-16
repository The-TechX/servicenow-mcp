from dataclasses import dataclass, field

@dataclass
class ActivityDTO:
    type: str | None
    author: str | None
    timestamp: str | None
    content: str | None
    details: dict[str, str] = field(default_factory=dict)
