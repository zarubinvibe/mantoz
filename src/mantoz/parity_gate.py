"""Гейт приёмки паритета Mantoz ↔ MatrAIx (REQ-01).

Читает docs/PARITY.md (или путь из ``--file``) и раздел «Вне цели» из
queue/GOAL.md. Код 0 только когда ни одной строки таблицы в статусе
«отсутствует» без обоснования; иначе код 1 и печать незакрытых строк.
Статус «отсутствует обоснованно» засчитывается, только когда ссылка
содержит точный ID вида ``OUT-NN``, реально присутствующий в разделе
«Вне цели» queue/GOAL.md, И подсистема строки входит в заявленную у
этого ID область действия ``[покрывает: …]``. Пункт без объявленной
области не покрывает ничего (fail-closed). Проза, слова из пункта,
REQ/LIM — не обоснование; нечёткое сопоставление запрещено (LIM-10).
``--selftest`` прогоняет фикстуры против настоящего queue/GOAL.md:
снятие сверки с GOAL.md делает селфтест красным.
"""

from __future__ import annotations

import argparse
import re
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PARITY_PATH = ROOT / "docs" / "PARITY.md"
GOAL_PATH = ROOT / "queue" / "GOAL.md"

OUT_ID_RE = re.compile(r"\bOUT-\d{2}\b")
SCOPE_RE = re.compile(r"\[покрывает:\s*([^\]]+)\]")

CLOSED_FIXTURE = """\
| Подсистема | Возможность MatrAIx | Статус Mantoz | Ссылка |
|---|---|---|---|
| persona | Схема персоны | есть эквивалент | REQ-01 |
| persona | Persona 1M как продакшн-граунд | отсутствует обоснованно | OUT-03 |
| harbor | 15 sandbox-бэкендов | отсутствует обоснованно | OUT-02 |
| playground | apps/viewer — второй SPA | отсутствует обоснованно | OUT-04 |
"""

OPEN_FIXTURE = """\
| Подсистема | Возможность MatrAIx | Статус Mantoz | Ссылка |
|---|---|---|---|
| persona | Схема персоны | отсутствует | docs/tickets/06-persona-taxonomy.md |
"""

REQ_REF_FIXTURE = """\
| Подсистема | Возможность MatrAIx | Статус Mantoz | Ссылка |
|---|---|---|---|
| persona | Выдумка | отсутствует обоснованно | REQ-99 |
"""

PROSE_FIXTURE = """\
| Подсистема | Возможность MatrAIx | Статус Mantoz | Ссылка |
|---|---|---|---|
| persona | Выдумка | отсутствует обоснованно | платной основе выдуманный сервис |
"""

GHOST_ID_FIXTURE = """\
| Подсистема | Возможность MatrAIx | Статус Mantoz | Ссылка |
|---|---|---|---|
| persona | Выдумка | отсутствует обоснованно | OUT-99 |
"""

SHORT_ID_FIXTURE = """\
| Подсистема | Возможность MatrAIx | Статус Mantoz | Ссылка |
|---|---|---|---|
| persona | Выдумка | отсутствует обоснованно | OUT-1 |
"""

LONG_ID_FIXTURE = """\
| Подсистема | Возможность MatrAIx | Статус Mantoz | Ссылка |
|---|---|---|---|
| persona | Выдумка | отсутствует обоснованно | OUT-001 |
"""

WRONG_SCOPE_FIXTURE = """\
| Подсистема | Возможность MatrAIx | Статус Mantoz | Ссылка |
|---|---|---|---|
| persona | Выдумка | отсутствует обоснованно | OUT-04 |
"""

RIGHT_SCOPE_FIXTURE = """\
| Подсистема | Возможность MatrAIx | Статус Mantoz | Ссылка |
|---|---|---|---|
| playground | Выдумка | отсутствует обоснованно | OUT-04 |
"""


def load_out_scopes(goal_path: Path) -> dict[str, set[str]]:
    """``OUT-NN`` → подсистемы из ``[покрывает: …]`` раздела «Вне цели» GOAL.md.

    Пункт без объявленной области действия получает пустое множество —
    fail-closed: он не освобождает ни одной строки.
    """
    scopes: dict[str, set[str]] = {}
    in_section = False
    for line in goal_path.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            in_section = line[3:].strip().startswith("Вне цели")
            continue
        if not in_section:
            continue
        ids = OUT_ID_RE.findall(line)
        if not ids:
            continue
        match = SCOPE_RE.search(line)
        covered = {s.strip() for s in match.group(1).split(",") if s.strip()} if match else set()
        for out_id in ids:
            scopes[out_id] = covered
    return scopes


def _honest_justification(link: str, subsystem: str, out_scopes: dict[str, set[str]]) -> bool:
    """Точный ID из «Вне цели», чья область действия покрывает подсистему строки."""
    return any(
        subsystem in out_scopes.get(out_id, set()) for out_id in OUT_ID_RE.findall(link)
    )


def evaluate(path: Path, goal_path: Path = GOAL_PATH) -> list[str]:
    """Вернуть список незакрытых строк таблицы паритета."""
    out_scopes = load_out_scopes(goal_path)
    open_rows: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 3:
            continue
        cells += [""] * (4 - len(cells))
        subsystem, capability, status, link = cells[:4]
        if set(subsystem) <= set("-: "):
            continue  # строка-разделитель
        if subsystem == "Подсистема":
            continue  # заголовок
        if not all(cells[:4]):
            open_rows.append(f"{capability or subsystem or '?'} (пустая ячейка)")
            continue
        normalized = status.lower()
        if normalized.startswith("отсутствует обоснованно"):
            if not _honest_justification(link, subsystem, out_scopes):
                open_rows.append(
                    f"{capability} (обоснование не является точным ID «Вне цели» queue/GOAL.md "
                    f"в области действия подсистемы «{subsystem}»)"
                )
            continue
        if normalized.startswith("есть эквивалент"):
            continue
        open_rows.append(capability)
    return open_rows


def selftest() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        fixtures = {
            "closed": (CLOSED_FIXTURE, 0, "закрытая точными OUT-ID таблица должна быть зелёной"),
            "open": (OPEN_FIXTURE, 1, "строка «отсутствует» должна дать ровно 1 незакрытую"),
            "req_ref": (REQ_REF_FIXTURE, 1, "ссылка на REQ — не обоснование"),
            "prose": (PROSE_FIXTURE, 1, "проза со словами настоящего пункта — не обоснование"),
            "ghost": (GHOST_ID_FIXTURE, 1, "несуществующий OUT-99 — не обоснование"),
            "short_id": (SHORT_ID_FIXTURE, 1, "OUT-1 не эквивалентен строгому OUT-01"),
            "long_id": (LONG_ID_FIXTURE, 1, "OUT-001 не эквивалентен строгому OUT-01"),
            "wrong_scope": (WRONG_SCOPE_FIXTURE, 1, "OUT-04 в строке persona — чужая область действия"),
            "right_scope": (RIGHT_SCOPE_FIXTURE, 0, "OUT-04 в строке playground — своя область действия"),
        }
        failures = []
        for name, (content, expected, message) in fixtures.items():
            fixture = Path(tmp) / f"{name}.md"
            fixture.write_text(content, encoding="utf-8")
            if len(evaluate(fixture)) != expected:
                failures.append(message)
    if failures:
        for failure in failures:
            print(f"selftest: FAIL — {failure}")
        return 1
    print("selftest: ok — закрытая 0, «отсутствует» 1, REQ-ссылка 1, проза 1, OUT-99 1, OUT-1 1, OUT-001 1, чужая область 1, своя область 0")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(prog="mantoz.parity_gate")
    parser.add_argument("--selftest", action="store_true", help="прогнать фикстуры вместо таблицы")
    parser.add_argument("--file", type=Path, help="путь к таблице паритета вместо docs/PARITY.md")
    args = parser.parse_args()
    if args.selftest:
        return selftest()
    open_rows = evaluate(args.file or PARITY_PATH)
    if open_rows:
        print(f"parity: КРАСНЫЙ — {len(open_rows)} незакрытых строк")
        for row in open_rows:
            print(f"  - {row}")
        return 1
    print("parity: ЗЕЛЁНЫЙ — 0 незакрытых строк")
    return 0


if __name__ == "__main__":
    sys.exit(main())
