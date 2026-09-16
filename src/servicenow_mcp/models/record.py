from dataclasses import dataclass, field
from .activity import ActivityDTO


@dataclass
class CustomFieldDTO:
    name: str
    label: str | None
    value: str | None
    display_value: str | None


@dataclass
class CatalogVariableDTO:
    label: str
    value: str | None
    display_value: str | None


@dataclass
class RecordRefDTO:
    sys_id: str
    number: str
    record_type: str


@dataclass
class WorkOrderTaskDTO(RecordRefDTO):
    parent: str | None = None
    customer: str | None = None
    location: str | None = None
    state: str | None = None
    dispatch_group: str | None = None
    assigned_to: str | None = None
    due_date: str | None = None
    short_description: str | None = None
    description: str | None = None
    custom_fields: list[CustomFieldDTO] = field(default_factory=list)
    activities: list[ActivityDTO] = field(default_factory=list)


@dataclass
class WorkOrderDTO(RecordRefDTO):
    active: bool | None = None
    customer: str | None = None
    caller: str | None = None
    configuration_item: str | None = None
    location: str | None = None
    category: str | None = None
    subcategory: str | None = None
    priority: str | None = None
    state: str | None = None
    assignment_group: str | None = None
    assigned_to: str | None = None
    assigned_vendor: str | None = None
    vendor_reference: str | None = None
    initiated_from: str | None = None
    opened_at: str | None = None
    scheduled_start: str | None = None
    estimated_end: str | None = None
    expected_end: str | None = None
    requested_due_by: str | None = None
    actual_work_start: str | None = None
    actual_work_end: str | None = None
    duration: str | None = None
    billable: bool | None = None
    short_description: str | None = None
    description: str | None = None
    custom_fields: list[CustomFieldDTO] = field(default_factory=list)
    activities: list[ActivityDTO] = field(default_factory=list)


@dataclass
class RequestedItemDTO(RecordRefDTO):
    item: str | None = None
    request: str | None = None
    requested_for: str | None = None
    state: str | None = None
    stage: str | None = None
    approval: str | None = None
    customer: str | None = None
    location: str | None = None
    opened_at: str | None = None
    opened_by: str | None = None
    due_date: str | None = None
    assignment_group: str | None = None
    assigned_to: str | None = None
    short_description: str | None = None
    variables: list[CatalogVariableDTO] = field(default_factory=list)
    custom_fields: list[CustomFieldDTO] = field(default_factory=list)
    activities: list[ActivityDTO] = field(default_factory=list)


@dataclass
class RequestDTO(RecordRefDTO):
    requested_for: str | None = None
    location: str | None = None
    parent: str | None = None
    contact_type: str | None = None
    approval: str | None = None
    request_state: str | None = None
    opened_at: str | None = None
    opened_by: str | None = None
    due_date: str | None = None
    assignment_group: str | None = None
    assigned_to: str | None = None
    company: str | None = None
    price: str | None = None
    custom_fields: list[CustomFieldDTO] = field(default_factory=list)
    activities: list[ActivityDTO] = field(default_factory=list)
