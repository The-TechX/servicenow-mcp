from mcp.server import MCPServer
from .config import Settings
from .auth.playwright_session import PlaywrightSessionAuth
from .client.servicenow import ServiceNowClient
from .tools.tasks import register_task_tools
from .tools.records import register_record_tools

settings = Settings()
mcp = MCPServer("servicenow")
client = ServiceNowClient(settings.base_url, PlaywrightSessionAuth(settings.session_file))
register_task_tools(mcp, client)
register_record_tools(mcp, client)


def main() -> None:
    mcp.run(
        transport="streamable-http",
        host=settings.host,
        port=settings.port,
    )


if __name__ == "__main__":
    main()
