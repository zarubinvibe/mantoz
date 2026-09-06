"""Тонкий вьювер отчётов population: самодостаточный HTML без сборки и npm."""

import argparse
import html
import json
import sys
from pathlib import Path


def esc(value: object) -> str:
    return html.escape(str(value))


def render_failed_trials(failed_trials: list) -> str:
    """Несостоявшиеся прогоны - ОТДЕЛЬНЫЙ блок, они не растворяются в долях."""
    if not failed_trials:
        return ""
    rows = []
    for trial in failed_trials:
        if isinstance(trial, dict):
            detail = "; ".join(f"{esc(k)}: {esc(v)}" for k, v in trial.items())
        else:
            detail = esc(trial)
        rows.append(f"<li>{detail}</li>")
    return (
        '<section class="failed-trials">'
        f"<h2>Несостоявшиеся прогоны ({len(failed_trials)})</h2>"
        "<p>Эти трайлы сломались инфраструктурно и в статистику персон не вошли.</p>"
        f"<ul>{''.join(rows)}</ul>"
        "</section>"
    )


def render_report(report: dict) -> str:
    n_runs = report.get("n_runs", "?")
    method = report.get("aggregation_method", "?")
    population = report.get("population", {})
    breakdown = report.get("subgroup_breakdown", {})

    rows = "".join(
        "<tr>"
        f"<td>{esc(name)}</td>"
        f"<td>{group.get('n_runs', '?')}</td>"
        f"<td>{group.get('passed', '?')}</td>"
        f"<td>{group.get('failed', '?')}</td>"
        f"<td>{group.get('pass_rate', 0):.1%}</td>"
        "</tr>"
        for name, group in breakdown.items()
    )

    return f"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<title>Отчёт population - {esc(n_runs)} прогонов</title>
<style>
body {{ font-family: system-ui, sans-serif; margin: 2rem auto; max-width: 48rem; padding: 0 1rem; }}
table {{ border-collapse: collapse; width: 100%; }}
th, td {{ border: 1px solid #ccc; padding: 0.4rem 0.6rem; text-align: left; }}
.failed-trials {{ border: 2px solid #b00; background: #fdf0f0; padding: 1rem; margin-top: 2rem; }}
</style>
</head>
<body>
<h1>Отчёт population</h1>
<dl>
<dt>Число прогонов</dt><dd>{esc(n_runs)}</dd>
<dt>Метод свертки</dt><dd>{esc(method)}</dd>
<dt>Доля прошедших</dt><dd>{population.get('pass_rate', 0):.1%} (прошло {population.get('passed', '?')}, не прошло {population.get('failed', '?')})</dd>
</dl>
<h2>Подгруппы</h2>
<table>
<thead><tr><th>Подгруппа</th><th>Прогонов</th><th>Прошло</th><th>Не прошло</th><th>Доля прошедших</th></tr></thead>
<tbody>{rows}</tbody>
</table>
{render_failed_trials(report.get('failed_trials', []))}
</body>
</html>
"""


def render(report_path: Path, out_path: Path) -> int:
    if not report_path.is_file():
        print(f"ошибка: отчёт не найден: {report_path}", file=sys.stderr)
        return 2
    try:
        report = json.loads(report_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        print(f"ошибка: отчёт не читается как JSON: {report_path}: {exc}", file=sys.stderr)
        return 2
    if not isinstance(report, dict) or "n_runs" not in report:
        print(f"ошибка: это не отчёт population: {report_path}", file=sys.stderr)
        return 2
    out_path.write_text(render_report(report), encoding="utf-8")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(prog="mantoz.viewer")
    commands = parser.add_subparsers(dest="command", required=True)
    render_parser = commands.add_parser("render")
    render_parser.add_argument("--report", required=True, type=Path)
    render_parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    sys.exit(render(args.report, args.out))


if __name__ == "__main__":
    main()
