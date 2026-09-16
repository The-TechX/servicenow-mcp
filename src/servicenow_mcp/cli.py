import argparse
import json
from dataclasses import asdict
from datetime import date, datetime
from .config import Settings
from .auth.playwright_session import PlaywrightSessionAuth
from .client.servicenow import ServiceNowClient
from .tools.tasks import ACTIVE_QUERY, COMPLETED_QUERY


def _json_default(value):
    if isinstance(value, (datetime, date)):
        return value.isoformat(sep=" ") if isinstance(value, datetime) else value.isoformat()
    raise TypeError(type(value).__name__)


def _client():
    settings=Settings()
    if not settings.base_url:
        raise SystemExit("SERVICENOW_BASE_URL is required")
    return ServiceNowClient(settings.base_url, PlaywrightSessionAuth(settings.session_file))


def main():
    p=argparse.ArgumentParser(description="Exercise ServiceNow primitives without MCP")
    sub=p.add_subparsers(dest="command", required=True)
    sub.add_parser("active")
    sub.add_parser("completed")
    for name in ("search", "show"):
        x=sub.add_parser(name); x.add_argument("number")
    args=p.parse_args(); c=_client()
    if args.command == "active": result=[asdict(x) for x in c.list_tasks(ACTIVE_QUERY)]
    elif args.command == "completed": result=[asdict(x) for x in c.list_tasks(COMPLETED_QUERY)]
    elif args.command == "search":
        x=c.search_record(args.number); result=asdict(x) if x else None
    else:
        x=c.show_record(args.number); result=asdict(x) if x else None
    print(json.dumps(result, indent=2, ensure_ascii=False, default=_json_default))

if __name__ == "__main__": main()
