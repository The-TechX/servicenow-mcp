from pathlib import Path
from playwright.sync_api import sync_playwright
from .config import Settings


def main() -> None:
    settings = Settings()
    if not settings.base_url:
        raise SystemExit("SERVICENOW_BASE_URL is required")
    target = settings.session_file.resolve()
    target.parent.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        page.goto(settings.base_url, wait_until="domcontentloaded")
        print("Complete ServiceNow SSO/MFA in the browser.")
        input("When ServiceNow is fully authenticated, press Enter here to save the session... ")
        context.storage_state(path=str(target))
        browser.close()
    print(f"Session saved to {target}")

if __name__ == "__main__":
    main()
