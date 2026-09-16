from dataclasses import asdict


def register_record_tools(mcp, client):
    @mcp.tool()
    def search_record(number: str):
        """Find an exact ServiceNow task-derived record by human-readable number."""
        record = client.search_record(number)
        return asdict(record) if record else None

    @mcp.tool()
    def show_record(number: str):
        """Return a typed structured view for a supported ServiceNow record."""
        record = client.show_record(number)
        return asdict(record) if record else None

    @mcp.tool()
    def add_work_note(number: str, text: str):
        """Append a work note to a supported ServiceNow record."""
        return client.add_work_note(number, text)
