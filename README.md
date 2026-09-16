# servicenow-mcp

Local MCP server for ServiceNow. The first supported capability is reading generic ServiceNow task records.

## Architecture

`Claude Code -> MCP tools -> ServiceNowClient -> Playwright request context -> ServiceNow server-rendered HTML -> parsers -> DTOs`

Authentication is local. `servicenow-login` opens Chromium so the user can complete the normal ServiceNow SSO/MFA flow and then stores Playwright `storage_state` in `session.json`. The session file is ignored by Git.

## Setup

Python 3.11+ is required.

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
python -m pip install -e .
playwright install chromium
```

Configure the local environment using `.env.example` as reference. At minimum set `SERVICENOW_BASE_URL` to your ServiceNow instance. `SERVICENOW_SESSION_FILE` defaults to `./session.json`.

## Login

```bash
servicenow-login
```

A Chromium window opens. Complete SSO/MFA normally, wait until ServiceNow is fully loaded, then return to the terminal and press Enter. The authenticated browser state is written locally to `session.json`.

If ServiceNow later reports that authentication expired, run `servicenow-login` again.

## Test primitives directly

These commands bypass MCP and exercise the same client/parsers used by the MCP tools:

```bash
servicenow-cli active
servicenow-cli completed
servicenow-cli search TASK0012345
servicenow-cli show TASK0012345
```

## Run MCP

```bash
servicenow-mcp
```

Default endpoint: `http://127.0.0.1:3310/mcp`.

Current MCP tools:

- `list_active_tasks`
- `list_completed_tasks`
- `search_task`
- `show_task`

## Security

Never commit `session.json`, `.env`, cookies, SSO artifacts, or authentication tokens. The intended deployment is local on the user's workstation; Docker is intentionally deferred until the interactive authentication lifecycle is understood.

## Documentation

Record-type discovery and parser design notes live in [Structured Views](docs/structured-views/README.md). These XRAY documents describe the generic HTML structure observed for each supported ServiceNow record type without containing tenant-specific data.
