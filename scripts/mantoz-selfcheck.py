#!/usr/bin/env python3
"""Offline self-check for a fresh clone of Mantoz.

Runs with the standard library only: no network, no Docker, no Harbor, no git.
It proves the tree a stranger just downloaded is internally consistent — the
schemas parse, the persona dependency graph has no cycle, the grounding
registry still separates what may be redistributed from what may not, and the
attribution required by the licenses is actually present in the files.

Exit code 0 means every check passed. Any failure prints the reason and exits 1.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FAILURES: list[str] = []
PASSED: list[str] = []


def check(name: str, condition: bool, detail: str = "") -> None:
    if condition:
        PASSED.append(name)
    else:
        FAILURES.append(f"{name}: {detail}" if detail else name)


def load_json(relative: str):
    path = ROOT / relative
    if not path.is_file():
        FAILURES.append(f"missing file: {relative}")
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as error:
        FAILURES.append(f"unreadable JSON: {relative}: {error}")
        return None


def check_persona_schema() -> None:
    schema = load_json("persona/schema/dimensions.json")
    if schema is None:
        return
    dimensions = schema.get("dimensions", [])
    ids = [item.get("id") for item in dimensions]
    categories = {item.get("category") for item in dimensions}
    check("persona schema has dimensions", len(dimensions) >= 40, f"found {len(dimensions)}")
    check("persona dimension ids are unique", len(ids) == len(set(ids)))
    check("persona schema keeps four categories", len(categories) == 4, f"found {sorted(categories)}")
    for item in dimensions:
        if not item.get("values"):
            FAILURES.append(f"dimension without values: {item.get('id')}")
            return
    PASSED.append("every persona dimension carries values")


def check_taxonomy_matches_source() -> None:
    """Схема собрана прибором. Правка руками разъедется с источником молча."""
    import subprocess
    tool = ROOT / "scripts/persona-taxonomy.py"
    if not tool.is_file():
        FAILURES.append("missing file: scripts/persona-taxonomy.py")
        return
    done = subprocess.run([sys.executable, str(tool), "--check"], cwd=ROOT,
                          capture_output=True, text=True)
    check("taxonomy matches its declared source", done.returncode == 0,
          (done.stderr or done.stdout).strip().split("\n")[0])


def check_persona_dag() -> None:
    schema = load_json("persona/schema/dimensions.json")
    edges_file = load_json("persona/schema/dependencies.json")
    if schema is None or edges_file is None:
        return
    known = {item.get("id") for item in schema.get("dimensions", [])}
    edges = edges_file.get("edges", edges_file.get("dependencies", []))
    graph: dict[str, set[str]] = {}
    for edge in edges:
        parent = edge.get("parent") or edge.get("from")
        child = edge.get("child") or edge.get("to")
        if parent not in known or child not in known:
            FAILURES.append(f"dependency edge points outside the schema: {parent} -> {child}")
            return
        graph.setdefault(parent, set()).add(child)
    check("persona dependency graph is not empty", bool(graph))

    colour: dict[str, int] = {}

    def has_cycle(node: str) -> bool:
        colour[node] = 1
        for nxt in graph.get(node, ()):  # grey means we are back on our own path
            if colour.get(nxt) == 1:
                return True
            if colour.get(nxt) is None and has_cycle(nxt):
                return True
        colour[node] = 2
        return False

    for node in list(graph):
        if colour.get(node) is None and has_cycle(node):
            FAILURES.append(f"persona dependency graph has a cycle through {node}")
            return
    PASSED.append("persona dependency graph is acyclic")


def check_grounding_registry() -> None:
    registry = load_json("config/grounding.json")
    if registry is None:
        return
    sources = registry["sources"] if isinstance(registry, dict) else registry
    check("grounding registry lists sources", bool(sources))
    commercial = [s for s in sources if s.get("commercial_use") is True]
    check("at least one source allows commercial use", bool(commercial))
    for source in sources:
        if source.get("commercial_use") is True:
            continue
        if source.get("local_only") is not True:
            FAILURES.append(
                f"source {source.get('id')} is not cleared for commercial use "
                "and is not marked local_only"
            )
            return
    PASSED.append("every restricted grounding source is marked local_only")


def check_agent_registry() -> None:
    registry = load_json("config/agents.json")
    if registry is None:
        return
    agents = registry["agents"] if isinstance(registry, dict) else registry
    check("agent registry holds at least ten entries", len(agents) >= 10, f"found {len(agents)}")
    ids = [agent.get("id") for agent in agents]
    check("agent ids are unique", len(ids) == len(set(ids)))


def check_task_contracts() -> None:
    tasks = sorted((ROOT / "application" / "tasks").glob("*/"))
    check("task library is not empty", bool(tasks))
    for task in tasks:
        for required in ("task.toml", "instruction.md", "tests/test.sh"):
            if not (task / required).is_file():
                FAILURES.append(f"task {task.name} is missing {required}")
                return
    PASSED.append("every task carries a contract, an instruction and its own verifier")


def check_parity_checklist() -> None:
    path = ROOT / "docs" / "PARITY.md"
    if not path.is_file():
        FAILURES.append("missing file: docs/PARITY.md")
        return
    rows = [line for line in path.read_text(encoding="utf-8").splitlines() if line.startswith("|")]
    open_rows = []
    for row in rows:
        cells = [cell.strip() for cell in row.strip("|").split("|")]
        if len(cells) < 4:
            continue
        status = cells[2]
        if status.startswith("отсутствует") and not re.search(r"OUT-\d{2}", cells[3]):
            open_rows.append(cells[1][:60])
    check("parity checklist has no unjustified gap", not open_rows, "; ".join(open_rows))
    check("parity checklist has real rows", len(rows) > 10, f"found {len(rows)}")


def check_attribution() -> None:
    notice = (ROOT / "NOTICE").read_text(encoding="utf-8") if (ROOT / "NOTICE").is_file() else ""
    check("NOTICE credits Harbor", "harbor-framework" in notice)
    check("NOTICE names the Apache-2.0 license", "Apache License" in notice)
    readme = (ROOT / "README.md").read_text(encoding="utf-8") if (ROOT / "README.md").is_file() else ""
    check("README cites the persona research", "arXiv:2608.04205" in readme)
    check("LICENSE is present", (ROOT / "LICENSE").is_file())


def check_data_boundary() -> None:
    ignore = (ROOT / ".gitignore").read_text(encoding="utf-8") if (ROOT / ".gitignore").is_file() else ""
    check("data/ is ignored by git", any(line.strip() in {"data/", "/data/"} for line in ignore.splitlines()))
    stray = [str(p.relative_to(ROOT)) for p in ROOT.rglob("*.sav")] + \
            [str(p.relative_to(ROOT)) for p in ROOT.rglob("*.dta")] + \
            [str(p.relative_to(ROOT)) for p in ROOT.rglob("*.marginals.json")]
    check("no restricted survey data sits in the tree", not stray, ", ".join(stray[:5]))


def main() -> int:
    check_persona_schema()
    check_taxonomy_matches_source()
    check_persona_dag()
    check_grounding_registry()
    check_agent_registry()
    check_task_contracts()
    check_parity_checklist()
    check_attribution()
    check_data_boundary()

    for name in PASSED:
        print(f"ok    {name}")
    for failure in FAILURES:
        print(f"FAIL  {failure}", file=sys.stderr)
    if FAILURES:
        print(f"\n{len(FAILURES)} check(s) failed", file=sys.stderr)
        return 1
    print(f"\nall {len(PASSED)} checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
