"""Create a deterministic, anonymized README screenshot of the real formatter.

Optional local tools only: pip install playwright; chromium installed on system,
or `python -m playwright install chromium` to install its browser binary.
Do NOT render personal emails into public documentation.
"""

from __future__ import annotations

import os
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from paperless_ngx_mail_header.formatting import render_header  # noqa: E402


def main() -> None:
    from playwright.sync_api import sync_playwright

    example = SimpleNamespace(
        from_values=SimpleNamespace(full="Beispiel GmbH <service@example.org>"),
        to_values=[SimpleNamespace(full="Alex Beispiel <alex@example.net>")],
        date=datetime(2026, 10, 29, 9, 15, tzinfo=timezone.utc),
        subject="Bestellbestätigung für deine Unterlagen",
    )
    markup = render_header(example)
    html = (
        '<!DOCTYPE html><html lang="de"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        '<style>body{margin:0;background:white;padding:12px;font-family:Arial,sans-serif}'
        '</style></head><body>' + markup + '</body></html>'
    )
    path = ROOT / "docs/images/mail-header-example.png"
    with sync_playwright() as playwright:
        executable = os.environ.get("CHROMIUM_PATH") or shutil.which("chromium") or shutil.which("google-chrome")
        opts = {"headless": True, "args": ["--no-sandbox", "--disable-dev-shm-usage"]}
        if executable:
            opts["executable_path"] = executable
        browser = playwright.chromium.launch(**opts)
        try:
            page = browser.new_page(viewport={"width": 900, "height": 300}, device_scale_factor=2)
            page.set_content(html, wait_until="load")
            page.locator('[data-paperless-mail-header="1"]').screenshot(path=str(path))
        finally:
            browser.close()
    print(f"Wrote {path} ({path.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
