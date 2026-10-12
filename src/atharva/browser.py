from pathlib import Path

from playwright.sync_api import sync_playwright

HOME = Path.home() / ".atharva"

def open_cf():
    p = sync_playwright().start()
    try:
        ctx = p.chromium.launch_persistent_context(
            user_data_dir=str(HOME / "profile"),
            headless=False,
            channel="chrome",
            ignore_default_args=["--enable-automation"],
            args=["--disable-blink-features=AutomationControlled"],
        )
    except Exception as e:
        p.stop()
        if "chrome" in str(e).lower() and "not found" in str(e).lower():
            raise SystemExit("cfx needs Google Chrome. Install it from https://google.com/chrome")
        raise
    return p, ctx
