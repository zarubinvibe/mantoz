"""Проходит desktop-сценарий мышью и снимает виртуальный дисплей."""

import json
import os
import subprocess
import sys
from pathlib import Path

from desktop_app import DecisionApp

OPTIONS = ("allow", "later", "deny")
SCREENSHOTS = Path("/app/screenshots")


def command(*args: str) -> None:
    subprocess.run(
        args, check=True, env={**os.environ, "DISPLAY": os.environ["DISPLAY"]}
    )


def main() -> int:
    plan = json.loads(Path("/app/plan.json").read_text("utf-8"))
    target = plan.get("choose")
    if target not in OPTIONS:
        print(f"неизвестное решение: {target!r}", file=sys.stderr)
        return 1

    SCREENSHOTS.mkdir(exist_ok=True)
    app = DecisionApp()
    actions = [{"type": "open", "target": "notification-dialog"}]
    failure: list[Exception] = []

    def automate() -> None:
        try:
            command("scrot", "-o", str(SCREENSHOTS / "before.png"))
            actions.append({"type": "screenshot", "target": "before.png"})
            button = app.buttons[target]
            x = button.winfo_rootx() + button.winfo_width() // 2
            y = button.winfo_rooty() + button.winfo_height() // 2
            command("xdotool", "mousemove", "--sync", str(x), str(y), "click", "1")
            actions.append({"type": "click", "target": target, "x": x, "y": y})
            app.root.after(150, finish)
        except Exception as exc:
            failure.append(exc)
            app.root.quit()

    def finish() -> None:
        try:
            app.root.update_idletasks()
            command("scrot", "-o", str(SCREENSHOTS / "after.png"))
            actions.append({"type": "screenshot", "target": "after.png"})
        except Exception as exc:
            failure.append(exc)
        finally:
            app.root.quit()

    app.root.after(350, automate)
    app.root.mainloop()
    app.root.destroy()
    if failure:
        raise failure[0]
    if app.decision != target:
        print("клик не изменил состояние приложения", file=sys.stderr)
        return 1
    Path("/app/result.json").write_text(
        json.dumps({"actions": actions, "decision": app.decision}, ensure_ascii=False)
        + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
