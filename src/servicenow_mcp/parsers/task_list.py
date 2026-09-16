from datetime import datetime
import re
from bs4 import BeautifulSoup
from ..models.task import TaskDTO


def _text(node):
    if node is None:
        return None
    value = node.get_text(" ", strip=True)
    return value or None


def _datetime(node):
    value = _text(node)
    if not value:
        return None
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            pass
    return None


def parse_task_list(html: str) -> list[TaskDTO]:
    soup = BeautifulSoup(html, "html.parser")
    tasks = []
    for row in soup.select('tr[data-type="list2_row"][sys_id]'):
        cells = row.find_all("td", recursive=False)
        if len(cells) < 10:
            continue
        link = cells[2].find("a", class_="formlink", href=True)
        if link is None:
            continue
        def text(i): return _text(cells[i]) if i < len(cells) else None
        def dt(i): return _datetime(cells[i].select_one(".date-calendar")) if i < len(cells) else None
        tasks.append(TaskDTO(
            sys_id=row.get("sys_id"), number=link.get_text(" ", strip=True),
            record_type=row.get("record_class", "task"), site_name=text(3),
            short_description=text(4), assigned_to=text(5), assignment_group=text(6),
            created_by=text(7), created_at=dt(8), closed_at=dt(9)))
    return tasks


def extract_total(html: str) -> int:
    for pattern in (r"sysparm_record_rows=(\d+)", r'data-total-rows=["\'](\d+)', r'sysparm_total_rows[=:"\']+(\d+)'):
        match = re.search(pattern, html)
        if match:
            return int(match.group(1))
    return len(parse_task_list(html))
