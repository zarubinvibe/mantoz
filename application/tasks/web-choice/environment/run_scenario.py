"""Проходит сценарий выбора тарифа в настоящем браузере (Playwright/Chromium).

Читает план из /app/plan.json (запечён хостом из признаков персоны), исполняет
его кликами по странице-стенду и пишет /app/result.json: след действий и
итоговое решение, ПРОЧИТАННОЕ ИЗ DOM страницы, а не из плана.
"""

import json
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

OPTIONS = ("base", "standart", "premium")


def main() -> int:
    plan = json.loads(Path("/app/plan.json").read_text("utf-8"))
    inspect = plan.get("inspect") or []
    choose = plan.get("choose")
    unknown = [o for o in [*inspect, choose] if o is not None and o not in OPTIONS]
    if unknown:
        print(f"неизвестные тарифы в плане: {unknown}", file=sys.stderr)
        return 1

    actions = []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        try:
            page = browser.new_page()
            page.goto("file:///app/stand.html")
            page.wait_for_selector("h1")
            actions.append({"type": "open", "target": "stand"})
            for option_id in inspect:
                page.click(f"[data-details='{option_id}']")
                page.wait_for_selector(f"[data-panel='{option_id}'].open")
                actions.append({"type": "inspect", "target": option_id})
            decision = None
            if choose is not None:
                page.click(f"[data-choose='{choose}']")
                page.wait_for_selector("#confirmation[data-decision]")
                # Решение - из DOM страницы, не из плана: это итог браузерного
                # прогона, а не пересказ входных данных.
                decision = page.get_attribute("#confirmation", "data-decision")
                actions.append({"type": "choose", "target": decision})
        finally:
            browser.close()

    Path("/app/result.json").write_text(
        json.dumps({"actions": actions, "decision": decision}, ensure_ascii=False)
        + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
