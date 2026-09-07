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

CANON_STATUSES = {"есть", "лучше", "нет"}
ROOT = Path(__file__).resolve().parents[2]
PARITY_PATH = ROOT / "docs" / "PARITY.md"
GOAL_PATH = ROOT / "queue" / "GOAL.md"

OUT_ID_RE = re.compile(r"\bOUT-\d{2}\b")
SCOPE_RE = re.compile(r"\[покрывает:\s*([^\]]+)\]")

CLOSED_FIXTURE = """\
| Подсистема | Возможность | У них | У нас | Статус | Чем доказано |
|---|---|---|---|---|---|
| persona | Схема персоны | 1 | 1 | есть | REQ-01 |
| persona | Persona 1M как продакшн-граунд | 1 | 0 | не берём: обосновано пунктом OUT-03 | OUT-03 |
| harbor | 15 sandbox-бэкендов | 1 | 0 | не берём: обосновано пунктом OUT-02 | OUT-02 |
| playground | apps/viewer — второй SPA | 1 | 0 | не берём: обосновано пунктом OUT-04 | OUT-04 |
"""

OPEN_FIXTURE = """\
| Подсистема | Возможность | У них | У нас | Статус | Чем доказано |
|---|---|---|---|---|---|
| persona | Схема персоны | 1 | 0 | нет | docs/tickets/06-persona-taxonomy.md |
"""

REQ_REF_FIXTURE = """\
| Подсистема | Возможность | У них | У нас | Статус | Чем доказано |
|---|---|---|---|---|---|
| persona | Выдумка | 1 | 0 | не берём: обосновано пунктом REQ-99 | REQ-99 |
"""

PROSE_FIXTURE = """\
| Подсистема | Возможность | У них | У нас | Статус | Чем доказано |
|---|---|---|---|---|---|
| persona | Выдумка | 1 | 0 | не берём: обосновано пунктом платной основе выдуманный сервис | платной основе выдуманный сервис |
"""

GHOST_ID_FIXTURE = """\
| Подсистема | Возможность | У них | У нас | Статус | Чем доказано |
|---|---|---|---|---|---|
| persona | Выдумка | 1 | 0 | не берём: обосновано пунктом OUT-99 | OUT-99 |
"""

SHORT_ID_FIXTURE = """\
| Подсистема | Возможность | У них | У нас | Статус | Чем доказано |
|---|---|---|---|---|---|
| persona | Выдумка | 1 | 0 | не берём: обосновано пунктом OUT-1 | OUT-1 |
"""

LONG_ID_FIXTURE = """\
| Подсистема | Возможность | У них | У нас | Статус | Чем доказано |
|---|---|---|---|---|---|
| persona | Выдумка | 1 | 0 | не берём: обосновано пунктом OUT-001 | OUT-001 |
"""

WRONG_SCOPE_FIXTURE = """\
| Подсистема | Возможность | У них | У нас | Статус | Чем доказано |
|---|---|---|---|---|---|
| persona | Выдумка | 1 | 0 | не берём: обосновано пунктом OUT-04 | OUT-04 |
"""

RIGHT_SCOPE_FIXTURE = """\
| Подсистема | Возможность | У них | У нас | Статус | Чем доказано |
|---|---|---|---|---|---|
| playground | Выдумка | 1 | 0 | не берём: обосновано пунктом OUT-04 | OUT-04 |
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
    status_column: int | None = None
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 3:
            continue
        cells += [""] * (6 - len(cells))
        subsystem, capability = cells[0], cells[1]
        if set(subsystem) <= set("-: "):
            continue  # строка-разделитель
        if subsystem in {"Подсистема", "Источник"}:
            if subsystem == "Подсистема":
                status_column = next((i for i, c in enumerate(cells) if c.lower() == "статус"), None)
            continue  # заголовок
        if "github.com/" in " ".join(cells):
            continue  # строка таблицы источников, у неё свои правила
        # Канон семьи: ровно четыре статуса. Номер столбца берётся из ЗАГОЛОВКА таблицы, а не
        # угадывается по значению: в колонках масштаба честно стоит слово «нет», и поиск по
        # значению принимал его за статус строки.
        idx = status_column if status_column is not None else next(
            (i for i, c in enumerate(cells)
             if c.lower().startswith("не берем") or c.lower().startswith("не берём")
             or c.lower() in CANON_STATUSES), -1)
        if idx >= len(cells) or idx < 0:
            open_rows.append(f"{capability or subsystem or '?'} (нет статуса из канона)")
            continue
        status = cells[idx]
        proof = " ".join(cells[idx + 1:]).strip()
        normalized = status.lower()
        if normalized.startswith("не берем") or normalized.startswith("не берём"):
            reason = status.split(":", 1)[1].strip() if ":" in status else ""
            if len(reason) < 10:
                open_rows.append(f"{capability} (отказ без названной причины)")
            elif not _honest_justification(reason, subsystem, out_scopes):
                open_rows.append(
                    f"{capability} (причина отказа не ссылается на точный ID «Вне цели» "
                    f"queue/GOAL.md в области действия подсистемы «{subsystem}»)"
                )
            continue
        if normalized == "нет":
            open_rows.append(f"{capability} (возможности нет и отказ не заявлен)")
            continue
        if not proof.strip("-–— "):
            open_rows.append(f"{capability} (статус «{status}» без улики)")
            continue
        if normalized == "лучше" and not any(ch.isdigit() for ch in proof):
            open_rows.append(f"{capability} («лучше» без числа: в чём именно сильнее)")
            continue
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
