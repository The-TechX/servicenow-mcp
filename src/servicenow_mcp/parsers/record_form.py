from bs4 import BeautifulSoup
from ..models.record import (
    CatalogVariableDTO,
    CustomFieldDTO,
    RequestDTO,
    RequestedItemDTO,
    WorkOrderDTO,
    WorkOrderTaskDTO,
)
from .activities import parse_activities

SUPPORTED_RECORD_TYPES = {"wm_task", "wm_order", "sc_req_item", "sc_request"}


def _clean(node):
    return node.get_text(" ", strip=True) if node else None


def _node(soup, name):
    return soup.find(attrs={"name": name}) or soup.find(id=name)


def _value(soup, table, field):
    node = _node(soup, f"{table}.{field}")
    if not node:
        return None
    if node.name == "textarea":
        return (node.get("value") or node.get_text() or "").strip() or None
    return (node.get("value") or "").strip() or None


def _display(soup, table, field):
    for name in (
        f"sys_display.{table}.{field}",
        f"{table}.{field}_label",
        f"sys_readonly.{table}.{field}",
    ):
        node = _node(soup, name)
        if not node:
            continue
        if node.name == "select":
            selected = node.find("option", selected=True)
            text = _clean(selected)
            if text:
                return text
        value = (node.get("value") or "").strip()
        if value:
            return value
    node = _node(soup, f"{table}.{field}")
    if node and node.name == "select":
        selected = node.find("option", selected=True)
        if selected:
            return _clean(selected)
    return _value(soup, table, field)


def _choice(soup, table, field):
    return _display(soup, table, field)


def _bool(soup, table, field):
    node = _node(soup, f"{table}.{field}") or _node(soup, f"sys_readonly.{table}.{field}")
    if not node:
        return None
    if node.get("type") == "checkbox":
        return node.has_attr("checked")
    value = (node.get("value") or "").strip().lower()
    if value in {"true", "1", "yes"}: return True
    if value in {"false", "0", "no"}: return False
    return None


def _label_for(soup, node):
    node_id = node.get("id")
    if not node_id:
        return None
    label = soup.find("label", attrs={"for": node_id})
    return _clean(label)


def _custom_fields(soup, table):
    out, seen = [], set()
    prefix = f"{table}.u_"
    for node in soup.find_all(["input", "select", "textarea"]):
        name = node.get("name") or node.get("id") or ""
        if not name.startswith(prefix):
            continue
        field = name[len(table) + 1:]
        if field in seen:
            continue
        seen.add(field)
        out.append(CustomFieldDTO(
            name=field,
            label=_label_for(soup, node),
            value=_value(soup, table, field),
            display_value=_display(soup, table, field),
        ))
    return out


def _catalog_variables(soup):
    out, seen = [], set()
    for node in soup.find_all(["input", "select", "textarea"]):
        name = node.get("name") or node.get("id") or ""
        if not name.startswith("ni.VE") or name in seen:
            continue
        seen.add(name)
        label = _label_for(soup, node)
        if not label:
            continue
        value = (node.get("value") or (node.get_text() if node.name == "textarea" else "") or "").strip() or None
        display = None
        if node.name == "select":
            selected = node.find("option", selected=True)
            display = _clean(selected) if selected else None
        out.append(CatalogVariableDTO(label=label, value=value, display_value=display or value))
    return out


def _identity(soup, table, sys_id, fallback_number):
    return dict(
        sys_id=sys_id,
        number=_value(soup, table, "number") or fallback_number,
        record_type=table,
    )


def _parse_wot(soup, table, sys_id, number):
    return WorkOrderTaskDTO(
        **_identity(soup, table, sys_id, number),
        parent=_display(soup, table, "parent"), customer=_display(soup, table, "company"),
        location=_display(soup, table, "location"), state=_choice(soup, table, "state"),
        dispatch_group=_display(soup, table, "dispatch_group"), assigned_to=_display(soup, table, "assigned_to"),
        due_date=_value(soup, table, "due_date"), short_description=_value(soup, table, "short_description"),
        description=_value(soup, table, "description"), custom_fields=_custom_fields(soup, table),
        activities=parse_activities(soup),
    )


def _parse_wo(soup, table, sys_id, number):
    return WorkOrderDTO(
        **_identity(soup, table, sys_id, number), active=_bool(soup, table, "active"),
        customer=_display(soup, table, "company"), caller=_display(soup, table, "caller"),
        configuration_item=_display(soup, table, "cmdb_ci"), location=_display(soup, table, "location"),
        category=_choice(soup, table, "category"), subcategory=_choice(soup, table, "subcategory"),
        priority=_choice(soup, table, "priority"), state=_choice(soup, table, "state"),
        assignment_group=_display(soup, table, "assignment_group"), assigned_to=_display(soup, table, "assigned_to"),
        assigned_vendor=_display(soup, table, "assigned_vendor"), vendor_reference=_value(soup, table, "vendor_reference"),
        initiated_from=_display(soup, table, "initiated_from"), opened_at=_value(soup, table, "opened_at"),
        scheduled_start=_value(soup, table, "expected_start"), estimated_end=_value(soup, table, "estimated_end"),
        expected_end=_value(soup, table, "expected_end"), requested_due_by=_value(soup, table, "requested_due_by"),
        actual_work_start=_value(soup, table, "work_start"), actual_work_end=_value(soup, table, "work_end"),
        duration=_value(soup, table, "calendar_duration"), billable=_bool(soup, table, "billable"),
        short_description=_value(soup, table, "short_description"), description=_value(soup, table, "description"),
        custom_fields=_custom_fields(soup, table), activities=parse_activities(soup),
    )


def _parse_ritm(soup, table, sys_id, number):
    return RequestedItemDTO(
        **_identity(soup, table, sys_id, number), item=_display(soup, table, "cat_item"),
        request=_display(soup, table, "request"), requested_for=_display(soup, table, "requested_for"),
        state=_choice(soup, table, "state"), stage=_choice(soup, table, "stage"), approval=_choice(soup, table, "approval"),
        customer=_display(soup, table, "company"), location=_display(soup, table, "location"),
        opened_at=_value(soup, table, "opened_at"), opened_by=_display(soup, table, "opened_by"),
        due_date=_value(soup, table, "due_date"), assignment_group=_display(soup, table, "assignment_group"),
        assigned_to=_display(soup, table, "assigned_to"), short_description=_value(soup, table, "short_description"),
        variables=_catalog_variables(soup), custom_fields=_custom_fields(soup, table), activities=parse_activities(soup),
    )


def _parse_req(soup, table, sys_id, number):
    return RequestDTO(
        **_identity(soup, table, sys_id, number), requested_for=_display(soup, table, "requested_for"),
        location=_display(soup, table, "location"), parent=_display(soup, table, "parent"),
        contact_type=_choice(soup, table, "contact_type"), approval=_choice(soup, table, "approval"),
        request_state=_choice(soup, table, "request_state"), opened_at=_value(soup, table, "opened_at"),
        opened_by=_display(soup, table, "opened_by"), due_date=_value(soup, table, "due_date"),
        assignment_group=_display(soup, table, "assignment_group"), assigned_to=_display(soup, table, "assigned_to"),
        company=_display(soup, table, "company"), price=_display(soup, table, "price"),
        custom_fields=_custom_fields(soup, table), activities=parse_activities(soup),
    )


PARSERS = {
    "wm_task": _parse_wot,
    "wm_order": _parse_wo,
    "sc_req_item": _parse_ritm,
    "sc_request": _parse_req,
}


def parse_record_form(html: str, table: str, sys_id: str, fallback_number: str):
    parser = PARSERS.get(table)
    if parser is None:
        raise ValueError(f"Unsupported ServiceNow record type: {table}")
    soup = BeautifulSoup(html, "html.parser")
    return parser(soup, table, sys_id, fallback_number)
