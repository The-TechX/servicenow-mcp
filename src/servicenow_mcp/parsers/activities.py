from bs4 import BeautifulSoup
from ..models.activity import ActivityDTO


def _clean(node):
    return node.get_text(" ", strip=True) if node else None


def parse_activities(soup: BeautifulSoup) -> list[ActivityDTO]:
    out = []
    root = soup.select_one("#sn_form_inline_stream_entries")
    if not root:
        return out
    for li in root.select("ul.activities-form > li.h-card"):
        author = _clean(li.select_one(".sn-card-component-createdby"))
        timebox = li.select_one(".sn-card-component-time")
        timestamp = _clean(timebox.select_one(".date-calendar")) if timebox else None
        spans = timebox.find_all("span", recursive=False) if timebox else []
        typ = _clean(spans[0]) if spans else None
        content = _clean(li.select_one(".sn-card-component_summary .sn-widget-textblock-body"))
        details = {}
        records = li.select_one(".sn-card-component_records")
        if records:
            for row in records.select("li"):
                cells = row.select(".sn-widget-list-table-cell")
                if len(cells) >= 2:
                    key, value = _clean(cells[0]), _clean(cells[1])
                    if key and value:
                        details[key.rstrip(":")] = value
        out.append(ActivityDTO(typ, author, timestamp, content, details))
    return out
