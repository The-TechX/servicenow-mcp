from urllib.parse import urlencode
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from ..errors import AuthenticationError, ResponseError
from ..parsers.task_list import parse_task_list, extract_total
from ..parsers.record_form import parse_record_form, SUPPORTED_RECORD_TYPES

class ServiceNowClient:
    def __init__(self, base_url: str, auth):
        self.base_url = base_url.rstrip("/")
        self.auth = auth

    def _validated_list(self, response):
        if not response.ok:
            raise ResponseError(f"HTTP {response.status}: {response.status_text}")
        html = response.text(); soup = BeautifulSoup(html, "html.parser")
        if soup.select_one('table.list_table, tr[data-type="list2_row"], input[name="sysparm_query"], [data-list_id]') is not None:
            return html
        url = str(response.url).lower()
        if any(x in url for x in ("session_timeout.do", "login.do", "login_redirect.do", "/saml", "/auth")):
            raise AuthenticationError("ServiceNow session is no longer authenticated")
        raise ResponseError("Expected authenticated ServiceNow list HTML")

    def _validated_form(self, response, table):
        if not response.ok:
            raise ResponseError(f"HTTP {response.status}: {response.status_text}")
        html = response.text(); soup = BeautifulSoup(html, "html.parser")
        if soup.find(attrs={"name": f"{table}.number"}) or soup.find(id=f"{table}.number"):
            return html
        url = str(response.url).lower()
        if any(x in url for x in ("session_timeout.do", "login.do", "login_redirect.do", "/saml", "/auth")):
            raise AuthenticationError("ServiceNow session is no longer authenticated")
        raise ResponseError(f"Expected authenticated {table} form HTML")

    def list_tasks(self, query: str):
        with sync_playwright() as p:
            q = p.request.new_context(storage_state=self.auth.storage_state_path())
            try:
                first = q.get(self.base_url + "/task_list.do?" + urlencode({"sysparm_view":"", "sysparm_query":query, "sysparm_first_row":1, "sysparm_clear_stack":"true"}))
                first_html = self._validated_list(first); total = extract_total(first_html); out=[]; seen=set()
                for first_row in range(1, total + 1, 20):
                    html = first_html if first_row == 1 else self._validated_list(q.get(self.base_url + "/task_list.do?" + urlencode({"sysparm_view":"", "sysparm_query":query, "sysparm_first_row":first_row, "sysparm_clear_stack":"true"})))
                    for task in parse_task_list(html):
                        if task.sys_id not in seen: seen.add(task.sys_id); out.append(task)
                return out
            finally: q.dispose()

    def search_record(self, number: str):
        """Resolve an exact task-derived record number through ServiceNow's task table."""
        number = number.strip().upper()
        records = self.list_tasks(f"number={number}")
        return next((x for x in records if x.number.upper() == number), None)

    def show_record(self, number: str):
        """Return a typed structured view for a supported ServiceNow record."""
        summary = self.search_record(number)
        if summary is None:
            return None
        if summary.record_type not in SUPPORTED_RECORD_TYPES:
            raise ResponseError(f"Unsupported ServiceNow record type: {summary.record_type}")
        with sync_playwright() as p:
            q = p.request.new_context(storage_state=self.auth.storage_state_path())
            try:
                response = q.get(f"{self.base_url}/{summary.record_type}.do?sys_id={summary.sys_id}")
                html = self._validated_form(response, summary.record_type)
            finally:
                q.dispose()
        return parse_record_form(html, summary.record_type, summary.sys_id, summary.number)

    def add_work_note(self, number: str, text: str):
        """Append a work note to a supported task-derived ServiceNow record."""
        text = text.strip()
        if not text:
            raise ValueError("Work note text is required")

        summary = self.search_record(number)
        if summary is None:
            return None
        if summary.record_type not in SUPPORTED_RECORD_TYPES:
            raise ResponseError(f"Unsupported ServiceNow record type: {summary.record_type}")

        table = summary.record_type
        with sync_playwright() as p:
            q = p.request.new_context(storage_state=self.auth.storage_state_path())
            try:
                form = q.get(f"{self.base_url}/{table}.do?sys_id={summary.sys_id}")
                html = self._validated_form(form, table)
                soup = BeautifulSoup(html, "html.parser")

                work_notes = soup.find(attrs={"name": f"{table}.work_notes"}) or soup.find(id=f"{table}.work_notes")
                if work_notes is None:
                    raise ResponseError(f"Work notes are not available on {table} for this session")

                ck = soup.find("input", attrs={"name": "sysparm_ck"})
                token = ck.get("value") if ck else None
                if not token:
                    raise AuthenticationError("ServiceNow CSRF token was not present in the authenticated form")

                url = self.base_url + "/angular.do?" + urlencode({
                    "sysparm_type": "list_history",
                    "action": "insert",
                    "table": table,
                    "sys_id": summary.sys_id,
                    "sysparm_timestamp": "",
                    "sysparm_source": "from_form",
                })
                response = q.post(
                    url,
                    headers={
                        "X-UserToken": token,
                        "Content-Type": "application/json;charset=UTF-8",
                        "Accept": "application/json, text/plain, */*",
                    },
                    data={"entries": [{"field": "work_notes", "text": text}]},
                )
                if not response.ok:
                    raise ResponseError(f"HTTP {response.status}: {response.status_text}")
            finally:
                q.dispose()

        return {
            "number": summary.number,
            "record_type": table,
            "success": True,
        }

    # Compatibility aliases for callers using the original v0.1 API.
    def search_task(self, number: str):
        return self.search_record(number)

    def show_task(self, number: str):
        return self.show_record(number)
