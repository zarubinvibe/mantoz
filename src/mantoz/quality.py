import argparse
import json
import sys
from collections import Counter
from pathlib import Path

from mantoz.persona import load_edges, load_schema

Rule = tuple[str, str, str, str]


def forbidden_rules() -> list[Rule]:
    # ponytail: prefer не имеет порога; статистический гейт добавит T09.
    return [
        (edge["parent"], parent_value, edge["child"], child_value)
        for edge in load_edges()
        if edge["kind"] == "forbid"
        for parent_value, child_value in edge["forbid"]
    ]


def read_attributes(line: str, lineno: int, allowed: dict[str, set[str]]) -> dict:
    try:
        row = json.loads(line)
    except json.JSONDecodeError as error:
        raise ValueError(
            f"строка {lineno}: невалидный JSON: {error.msg}"
        ) from error
    if not isinstance(row, dict):
        raise ValueError(
            f"строка {lineno}: персона должна быть JSON-объектом"
        )
    attributes = row.get("attributes", row)
    if not isinstance(attributes, dict):
        raise ValueError(
            f"строка {lineno}: attributes должен быть JSON-объектом"
        )
    missing = allowed.keys() - attributes.keys()
    if missing:
        raise ValueError(
            f"строка {lineno}: нет измерений: {', '.join(sorted(missing))}"
        )
    invalid = [key for key, values in allowed.items() if attributes[key] not in values]
    if invalid:
        raise ValueError(
            f"строка {lineno}: значение вне схемы: {', '.join(invalid)}"
        )
    return attributes


def describe(rule: Rule) -> str:
    parent, parent_value, child, child_value = rule
    return f"{parent}={parent_value!r} запрещает {child}={child_value!r}"


def gate(file: Path) -> int:
    rules = forbidden_rules()
    allowed = {item["id"]: set(item["values"]) for item in load_schema()}
    counts: Counter[Rule] = Counter()
    checked = violating_personas = 0
    with file.open(encoding="utf-8") as stream:
        for lineno, line in enumerate(stream, 1):
            if not line.strip():
                raise ValueError(f"строка {lineno}: пустая строка")
            attributes = read_attributes(line, lineno, allowed)
            checked += 1
            broken = [
                rule
                for rule in rules
                if attributes[rule[0]] == rule[1] and attributes[rule[2]] == rule[3]
            ]
            counts.update(broken)
            violating_personas += bool(broken)
    if not checked:
        raise ValueError("выборка пуста")
    print(f"проверено персон: {checked}")
    print(f"персон с нарушениями: {violating_personas}")
    for rule in rules:
        print(f"правило {describe(rule)} нарушено {counts[rule]} раз")
    return bool(violating_personas)


def main() -> None:
    parser = argparse.ArgumentParser(prog="mantoz.quality")
    commands = parser.add_subparsers(dest="command", required=True)
    gate_parser = commands.add_parser("gate")
    gate_parser.add_argument("--file", required=True, type=Path)
    args = parser.parse_args()
    try:
        raise SystemExit(gate(args.file))
    except (OSError, ValueError) as error:
        print(f"ошибка: {error}", file=sys.stderr)
        raise SystemExit(2) from error


if __name__ == "__main__":
    main()
