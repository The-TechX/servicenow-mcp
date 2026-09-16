from dataclasses import asdict

ACTIVE_QUERY = "active=true^assigned_to=javascript:getMyAssignments()^state!=-5"
COMPLETED_QUERY = "assigned_to=javascript:getMyAssignments()^state=3"

def register_task_tools(mcp, client):
    @mcp.tool()
    def list_active_tasks():
        """List active ServiceNow tasks assigned to the current user."""
        return [asdict(x) for x in client.list_tasks(ACTIVE_QUERY)]
    @mcp.tool()
    def list_completed_tasks():
        """List completed ServiceNow tasks assigned to the current user."""
        return [asdict(x) for x in client.list_tasks(COMPLETED_QUERY)]
    @mcp.tool()
    def search_task(number: str):
        """Find a ServiceNow task by its exact human-readable number."""
        x=client.search_task(number); return asdict(x) if x else None
    @mcp.tool()
    def show_task(number: str):
        """Return task details including Activities when available."""
        x=client.show_task(number); return asdict(x) if x else None
