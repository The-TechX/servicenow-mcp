from dataclasses import dataclass, field
from datetime import datetime
from .activity import ActivityDTO

@dataclass
class TaskDTO:
    sys_id: str
    number: str
    record_type: str
    site_name: str | None
    short_description: str | None
    assigned_to: str | None
    assignment_group: str | None
    created_by: str | None
    created_at: datetime | None
    closed_at: datetime | None

@dataclass
class TicketDTO:
    sys_id: str
    number: str
    record_type: str
    parent: str | None
    customer: str | None
    site_name: str | None
    po_number: str | None
    state: str | None
    assigned_to: str | None
    catalog_item: str | None
    due_date: str | None
    short_description: str | None
    description: str | None
    activities: list[ActivityDTO] = field(default_factory=list)
