# Structured View: Work Order (WO)

> XRAY status: initial discovery

## Identity

| Property | Value |
| --- | --- |
| ServiceNow table | `wm_order` |
| Common number prefix | `WO` |
| Classic form | `wm_order.do` |
| Domain concept | Work Order |

## Structured fields

The classic Work Order form exposes a substantial set of structured fields. The generic parser should distinguish standard Work Management fields from tenant-specific custom fields.

| Concept | Typical ServiceNow field | Notes |
| --- | --- | --- |
| Number | `number` | Human-readable work-order number |
| Active | `active` | Boolean record status |
| Customer/company | `company` | Reference; prefer display value |
| Caller | `caller` | Reference when present |
| Configuration item | `cmdb_ci` | Affected CI when applicable |
| Location | `location` | Work/site location when available |
| Template | `template` | Work-order template when used |
| Category | `category` | Work classification |
| Subcategory | `subcategory` | Dependent work classification |
| Opened at | `opened_at` | Record open timestamp |
| Priority | `priority` | Prefer human-readable display value |
| State | `state` | Prefer human-readable display value |
| Qualification group | `qualification_group` | Qualification/routing reference when used |
| Assignment group | `assignment_group` | Current owning group |
| Assigned to | `assigned_to` | Current assignee |
| Assigned vendor | `assigned_vendor` | Vendor reference when used |
| Vendor reference | `vendor_reference` | External vendor reference when used |
| Initiated from | `initiated_from` | Source record; can reference a requested item |
| Billable | `billable` | Boolean billing indicator |
| Duration | `calendar_duration` | Calendar duration when calculated |
| Actual work start | `work_start` | Actual execution start |
| Actual work end | `work_end` | Actual execution end |
| Short description | `short_description` | Human-readable summary |
| Description | `description` | Full work description |
| Comments | `comments` | Customer-visible journal field |
| Work notes | `work_notes` | Internal journal field |
| Scheduled start | `expected_start` | Scheduled start in observed form |
| Estimated end | `estimated_end` | Estimated completion timestamp |
| Expected end | `expected_end` | Expected completion timestamp when present |
| Requested due by | `requested_due_by` | Requested completion timestamp |

Missing fields must be treated as optional rather than parser failures.

## Custom fields

Work Order forms can contain tenant-specific fields, commonly recognizable by custom field names such as the `u_*` namespace. These must not become assumptions of the generic MCP core.

Examples of concepts that may be custom in a deployment include:

- survey contact
- legal entity
- customer PO / AFE
- catalog item linkage
- fulfillment group
- negotiated date
- rework indicator
- internal/external update indicator
- vendor number / local procurement metadata

A generic parser may preserve discovered custom fields in an extension collection, but typed `WorkOrderDTO` properties should be limited to stable concepts unless a reusable mapping is established.

```python
@dataclass
class CustomFieldDTO:
    name: str
    label: str | None
    value: str | None
    display_value: str | None
```

## Proposed structured representation

```python
@dataclass
class WorkOrderDTO:
    sys_id: str
    number: str
    record_type: str = "wm_order"

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
```

This is an XRAY/proposed representation, not yet a guarantee of the runtime API.

## Relationships / related lists

The observed Work Order form exposes several relationship surfaces. Generic implementations should model these as relationships rather than eagerly embedding all related records into `show_record`.

Important relationships include:

- Work Order Tasks (`WOT` / `wm_task`) — child execution tasks
- source/initiating record — the observed `initiated_from` field can point to a Requested Item (`RITM`)
- affected configuration items
- part requirements
- task SLAs
- documents
- task activities
- incidental expenses
- generic child tasks
- related Work Orders

Conceptually:

```text
RITM / other source
       ↓ initiated_from
      Work Order
       ├── Work Order Tasks[]
       ├── Affected CIs[]
       ├── Part Requirements[]
       ├── Task SLAs[]
       ├── Documents[]
       └── Activities[]
```

## Activity stream

The Work Order uses the same broad ServiceNow journal/activity pattern seen in task-derived records. The form exposes filters for events such as:

- comments
- work notes
- assignment changes
- state changes
- attachments
- correspondence/autogenerated email events
- opened-by events

`comments` and `work_notes` are input/journal fields; historical activity should be represented through `ActivityDTO` rather than by treating the current textarea value as history.

## Parsing strategy

```text
WO number
   ↓
resolve wm_order
   ↓
GET wm_order.do?sys_id=<id>
   ↓
validate wm_order form structure
   ↓
parse stable fields
   ├── resolve reference display values
   ├── preserve optional custom fields separately
   └── parse activity stream
   ↓
WorkOrderDTO
```

### Reference fields

ServiceNow forms commonly expose both an internal reference value and a display value. Agent-facing output should prefer the display value:

```text
wm_order.assignment_group             → internal identifier
sys_display.wm_order.assignment_group → human-readable value
```

The same pattern applies to references such as customer/company, location, assignee, configuration item, vendor, and initiating record.

### Choice fields

For choice fields such as `state` and `priority`, the raw value can be numeric/internal while the selected option contains the meaningful display value. Structured output should prefer the display value while allowing the raw value to be retained internally if needed.

## Discovery notes

The classic Work Order page is sufficiently structured to parse directly from authenticated server-rendered HTML. The navigation wrapper and list-position parameters are not required once `table + sys_id` are known; the canonical record fetch can be reduced to `wm_order.do?sys_id=<id>`.

The Work Order is also an important relationship hub: it can retain the record that initiated it and expose child Work Order Tasks. This supports navigation such as `RITM → WO → WOT` without making those relationships part of one oversized DTO.

Future XRAY passes should determine which Work Management fields are stable across ServiceNow deployments and whether related-list metadata can be discovered through one generic relation parser.
