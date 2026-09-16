from bs4 import BeautifulSoup
from ..models.task import TicketDTO
from .activities import parse_activities


def _clean(node): return node.get_text(" ", strip=True) if node else None

def _input(soup, name):
    node = soup.find(attrs={"name": name}) or soup.find(id=name)
    return node.get("value", "").strip() if node else None

def _display(soup, table, field):
    return _input(soup, f"sys_display.{table}.{field}") or _input(soup, f"{table}.{field}_label") or _input(soup, f"{table}.{field}")


def parse_task_form(html: str, table: str, sys_id: str, fallback_number: str) -> TicketDTO:
    soup = BeautifulSoup(html, "html.parser")
    state_node = soup.find(attrs={"name": f"{table}.state"})
    state = None
    if state_node:
        selected = state_node.find("option", selected=True)
        state = _clean(selected) if selected else state_node.get("value")
    return TicketDTO(
        sys_id=sys_id, number=_input(soup, f"{table}.number") or fallback_number, record_type=table,
        parent=_display(soup, table, "parent"), customer=_display(soup, table, "company"),
        site_name=_display(soup, table, "location"), po_number=_input(soup, f"{table}.u_wot_po_number"),
        state=state, assigned_to=_display(soup, table, "assigned_to"), catalog_item=_display(soup, table, "cat_item"),
        due_date=_input(soup, f"{table}.due_date"), short_description=_input(soup, f"{table}.short_description"),
        description=_clean(soup.find("textarea", attrs={"name": f"{table}.description"})) or _input(soup, f"{table}.description"),
        activities=parse_activities(soup))
