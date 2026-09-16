from mcp.server.fastmcp import FastMCP
from .config import Settings
from .auth.playwright_session import PlaywrightSessionAuth
from .client.servicenow import ServiceNowClient
from .tools.tasks import register_task_tools

settings=Settings()
mcp=FastMCP("servicenow")
client=ServiceNowClient(settings.base_url, PlaywrightSessionAuth(settings.session_file))
register_task_tools(mcp, client)

def main():
    mcp.settings.host=settings.host; mcp.settings.port=settings.port
    mcp.run(transport="streamable-http")
if __name__ == "__main__": main()
