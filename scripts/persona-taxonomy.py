#!/usr/bin/env python3
"""Пересборка таксономии персон из объявленных доменов жизни.

Схема на сорок измерений даёт мало групп для разбивки, а это и есть главное
обещание продукта: показать, где группы разошлись. Дописывать измерения руками
не выход - каждое новое требует своих значений и своих связей, и на сотне
человек рука сдаётся раньше схемы.

Поэтому схема растёт данными. `persona/schema/domains.json` держит домены жизни
и шкалы; одна строка домена с тремя фасетами даёт три измерения со связными
значениями. Ядро (`core.json`) писано руками и не трогается: демографический
костяк должен оставаться таким, каким его задумали.

    python3 scripts/persona-taxonomy.py            # пересобрать
    python3 scripts/persona-taxonomy.py --check    # только сверить, ничего не писать

`--check` нужен воротам: схема в дереве обязана совпадать с тем, что даёт
источник, иначе правка руками разъедется с генератором и никто не заметит.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCHEMA = ROOT / "persona/schema"
CORE = SCHEMA / "core.json"
DOMAINS = SCHEMA / "domains.json"
DIMENSIONS = SCHEMA / "dimensions.json"
DEPENDENCIES = SCHEMA / "dependencies.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def build_dimensions(core: dict, source: dict) -> list[dict]:
    """Ядро идёт первым и неизменным, дальше домен на фасет."""
    out = list(core["dimensions"])
    known = {d["id"] for d in out}
    for domain in source["domains"]:
        for facet in domain["facets"]:
            scale = source["scales"][facet]
            ident = f"{domain['id']}_{facet}"
            if ident in known:
                raise SystemExit(f"измерение {ident} уже есть в ядре: переименуй домен или фасет")
            known.add(ident)
            out.append({
                "id": ident,
                "category": domain["category"],
                "description": f"{domain['label']}: {scale['label']}",
                "values": list(scale["values"]),
            })
    return out


NEAR, FAR = 1.8, 0.5


def boost_map(parent_values: list[str], child_values: list[str], inverse: bool) -> dict:
    """Карта весов между двумя порядковыми шкалами.

    Ребро `prefer` без весов ничего не двигает: оно только красиво считается в
    отчёте. Поэтому вес считается здесь, из положения значения на своей шкале.
    Близкие по рангу значения получают перевес, далёкие теряют. Обратная связь
    переворачивает шкалу потомка: чем старше человек, тем реже он играет.
    """
    out: dict[str, dict[str, float]] = {}
    last_parent = max(len(parent_values) - 1, 1)
    last_child = max(len(child_values) - 1, 1)
    for pi, parent_value in enumerate(parent_values):
        position = pi / last_parent
        if inverse:
            position = 1.0 - position
        row = {}
        for ci, child_value in enumerate(child_values):
            distance = abs(position - ci / last_child)
            row[child_value] = NEAR if distance <= 0.25 else (1.0 if distance <= 0.5 else FAR)
        out[parent_value] = row
    return out


def build_edges(core_edges: list[dict], source: dict, dims: list[dict]) -> list[dict]:
    """Связи ядра сохраняются как есть, к ним добавляются объявленные зависимости доменов.

    Ребро `prefer` не запрещает сочетание, а смещает вероятность. Жёсткие запреты
    пишутся руками там, где сочетание физически невозможно, а «люди с нестабильным
    доходом реже летают за границу» это смещение.
    """
    by_id = {d["id"]: d for d in dims}
    edges = list(core_edges)
    seen = {(e.get("parent"), e.get("child")) for e in edges}
    for domain in source["domains"]:
        for raw in domain.get("depends_on", []):
            inverse = raw.startswith("-")
            parent = raw[1:] if inverse else raw
            if parent not in by_id:
                raise SystemExit(f"домен {domain['id']} зависит от неизвестного измерения {parent}")
            for facet in domain["facets"]:
                child = f"{domain['id']}_{facet}"
                if (parent, child) in seen or child not in by_id:
                    continue
                seen.add((parent, child))
                edges.append({
                    "parent": parent,
                    "child": child,
                    "kind": "prefer",
                    "note": f"{domain['label']}: {'обратная' if inverse else 'прямая'} связь с «{parent}»",
                    "boost": boost_map(by_id[parent]["values"], by_id[child]["values"], inverse),
                })
    return edges


def acyclic(edges: list[dict]) -> bool:
    graph: dict[str, set[str]] = {}
    for edge in edges:
        graph.setdefault(edge["parent"], set()).add(edge["child"])
    colour: dict[str, int] = {}

    def walk(node: str) -> bool:
        colour[node] = 1
        for nxt in graph.get(node, ()):
            if colour.get(nxt) == 1:
                return False
            if colour.get(nxt) is None and not walk(nxt):
                return False
        colour[node] = 2
        return True

    return all(colour.get(node) is not None or walk(node) for node in list(graph))


def main() -> int:
    check = "--check" in sys.argv
    core, source = load(CORE), load(DOMAINS)
    dims = build_dimensions(core, source)
    ids = {d["id"] for d in dims}
    old_edges = load(DEPENDENCIES)
    core_edges = [e for e in old_edges["edges"] if e.get("kind") != "prefer" or "note" not in e]
    edges = build_edges(core_edges, source, dims)
    if not acyclic(edges):
        print("граф зависимостей получился с циклом", file=sys.stderr)
        return 1

    dimensions_doc = {"schema_version": 1,
                      "note": "Собрано прибором scripts/persona-taxonomy.py из core.json и domains.json. Руками не править.",
                      "dimensions": dims}
    dependencies_doc = dict(old_edges)
    dependencies_doc["edges"] = edges

    if check:
        drift = []
        if load(DIMENSIONS).get("dimensions") != dims:
            drift.append(str(DIMENSIONS.relative_to(ROOT)))
        if load(DEPENDENCIES).get("edges") != edges:
            drift.append(str(DEPENDENCIES.relative_to(ROOT)))
        if drift:
            print("схема разошлась с источником: " + ", ".join(drift), file=sys.stderr)
            print("починка: python3 scripts/persona-taxonomy.py", file=sys.stderr)
            return 1
        print(f"схема совпадает с источником: {len(dims)} измерений, {len(edges)} рёбер")
        return 0

    DIMENSIONS.write_text(json.dumps(dimensions_doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    DEPENDENCIES.write_text(json.dumps(dependencies_doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    groups: dict[str, int] = {}
    for d in dims:
        groups[d["category"]] = groups.get(d["category"], 0) + 1
    print(f"собрано: {len(dims)} измерений, {len(edges)} рёбер")
    for name, count in sorted(groups.items()):
        print(f"  {name}: {count}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
