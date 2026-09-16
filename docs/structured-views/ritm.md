# Structured View: Requested Item (RITM)

> XRAY status: initial discovery

## Identity

| Property | Value |
| --- | --- |
| ServiceNow table | `sc_req_item` |
| Common number prefix | `RITM` |
| Classic form | `sc_req_item.do` |
| Domain concept | Requested Item |

## Structured fields

The following fields are useful candidates for a typed requested-item representation when present in the instance/form:

| Concept | Typical ServiceNow field | Notes |
| --- | --- | --- |
| Number | `number` | Human-readable record number |
| Catalog item | `cat_item` | Item that produced the request |
| Parent request | `request` | Reference to the parent request (`REQ`) |
| Requested for | `requested_for` | Person the item was requested for |
| Due date | `due_date` | Requested/due date when available |
| Configuration item | `cmdb_ci` | Related CI when applicable |
| Business service | `business_service` | Related service when applicable |
| Company/customer | instance-dependent | Reference may vary by implementation |
| Location | `location` | Related location when available |
| Opened at | `opened_at` | Creation/open timestamp |
| Opened by | `opened_by` | User who opened the item |
| Stage | `stage` | Catalog fulfillment stage |
| State | `state` | Prefer display value in structured output |
| Approval | `approval` | Approval state |
| Quantity | `quantity` | Requested quantity |
| Estimated delivery | instance-dependent | May be derived/custom depending on instance |
| Expected start | `expected_start` | Expected start when exposed |
| Assignment group | `assignment_group` | Current owning group |
| Assigned to | `assigned_to` | Current assignee |
| Short description | `short_description` | Human-readable summary |
| Work notes | `work_notes` | Journal field; activity stream is preferred for history |
| Comments | `comments` | Journal field; activity stream is preferred for history |

Missing fields must be treated as optional rather than parser failures.

## Dynamic catalog variables

Catalog variables are not a fixed RITM schema. Their names and presence depend on the catalog item, so the generic model should expose them as a collection rather than adding one DTO property per variable.

```python
@dataclass
class CatalogVariableDTO:
    label: str
    value: str | None
    display_value: str | None
```

Conceptually:

```text
RequestedItem
└── variables[]
    ├── label
    ├── value
    └── display_value
```

The parser should discover variables from the form and preserve their human-readable labels. Internal/generated variable identifiers should not become the public MCP contract.

## Proposed structured representation

```python
@dataclass
class RequestedItemDTO:
    sys_id: str
    number: str
    record_type: str = "sc_req_item"

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
    activities: list[ActivityDTO] = field(default_factory=list)
```

This is an XRAY/proposed representation, not yet a guarantee of the runtime API. Field names can be refined as additional record types are inspected.

## Relationships / related lists

A requested item can expose related lists such as:

- Catalog Tasks (`SCTASK`)
- Approvers
- Group approvals
- Projects
- Work Orders

These should remain relationships rather than being eagerly embedded into the base RITM DTO. They can later be exposed through explicit relation primitives if needed.

## Parsing strategy

```text
RITM number
   ↓
resolve sc_req_item
   ↓
GET sc_req_item.do?sys_id=<id>
   ↓
validate expected form structure
   ↓
parse stable fields
   ├── parse dynamic catalog variables
   └── parse activity stream
   ↓
RequestedItemDTO
```

Principles:

1. Parse the authenticated server-rendered form rather than depending on the ServiceNow REST API.
2. Validate positive form structure before interpreting the response as a record.
3. Treat optional/instance-specific fields as nullable.
4. Keep catalog variables dynamic.
5. Prefer display values for references and choice fields in agent-facing output while retaining identifiers only when they are useful for navigation.
6. Keep tenant-specific customization outside the generic core.

## Discovery notes

The classic RITM form provides enough structured HTML to model the requested item without browser-screen scraping. It also provides the parent request reference directly, making `RITM → REQ` a natural navigable relationship.

Future XRAY passes should verify which fields are universally available, how variable markup differs across catalog items, and whether related-list discovery can be made generic across task-derived record types.
