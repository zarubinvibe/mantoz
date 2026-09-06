import argparse
import json
import math
import random
import sys
import tempfile
from pathlib import Path

SCHEMA = (
    Path(__file__).resolve().parents[2] / "persona" / "schema" / "dimensions.json"
)
DEPENDENCIES = SCHEMA.with_name("dependencies.json")


def positive_int(value: str) -> int:
    number = int(value)
    if number < 1:
        raise argparse.ArgumentTypeError("must be at least 1")
    return number


def load_schema() -> list[dict]:
    return json.loads(SCHEMA.read_text(encoding="utf-8"))["dimensions"]


def load_edges() -> list[dict]:
    graph = json.loads(DEPENDENCIES.read_text(encoding="utf-8"))
    return graph["edges"] if isinstance(graph, dict) else graph


def load_grounding(path: Path, dimensions: list[dict]) -> dict[str, dict[str, float]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    marginals = payload.get("dimensions", payload) if isinstance(payload, dict) else None
    if not isinstance(marginals, dict):
        raise ValueError("маргиналы должны быть объектом dimensions")
    schema = {dimension["id"]: dimension["values"] for dimension in dimensions}
    result = {}
    for dimension, distribution in marginals.items():
        if dimension not in schema or not isinstance(distribution, dict):
            raise ValueError(
                f"неизвестное измерение в маргиналах: {dimension}"
            )
        unknown = set(distribution) - set(schema[dimension])
        if unknown:
            raise ValueError(
                f"неизвестные значения {dimension}: {sorted(unknown)}"
            )
        weights = {value: float(weight) for value, weight in distribution.items()}
        invalid = any(
            weight < 0 or not math.isfinite(weight) for weight in weights.values()
        )
        if not weights or invalid or not any(weights.values()):
            raise ValueError(f"некорректные веса маргиналов: {dimension}")
        result[dimension] = weights
    if not result:
        raise ValueError("маргиналы пусты")
    return result


def topological_order(dimensions: list[dict], edges: list[dict]) -> list[dict]:
    """Kahn: родители измерений идут раньше потомков. Граф обязан быть ацикличным."""
    by_id = {d["id"]: d for d in dimensions}
    indegree = {d["id"]: 0 for d in dimensions}
    children: dict[str, list[str]] = {}
    for edge in edges:
        children.setdefault(edge["parent"], []).append(edge["child"])
        indegree[edge["child"]] += 1
    queue = [d["id"] for d in dimensions if indegree[d["id"]] == 0]
    order = []
    while queue:
        node = queue.pop(0)
        order.append(by_id[node])
        for child in children.get(node, []):
            indegree[child] -= 1
            if indegree[child] == 0:
                queue.append(child)
    if len(order) != len(dimensions):
        raise ValueError("цикл в графе зависимостей")
    return order


def weighted_choice(
    rng: random.Random,
    dimension: dict,
    edges: list[dict],
    attributes: dict,
    marginals: dict[str, dict[str, float]],
) -> str:
    values = dimension["values"]
    distribution = marginals.get(dimension["id"])
    weights = (
        [distribution.get(value, 0.0) for value in values]
        if distribution
        else [1.0] * len(values)
    )
    for edge in edges:
        if edge["child"] != dimension["id"]:
            continue
        parent_value = attributes[edge["parent"]]
        if edge["kind"] == "forbid":
            forbidden = {child for parent, child in edge["forbid"] if parent == parent_value}
            weights = [0.0 if v in forbidden else w for v, w in zip(values, weights)]
        elif edge["kind"] == "prefer":
            boost = edge["boost"].get(parent_value, {})
            weights = [w * boost.get(v, 1.0) for v, w in zip(values, weights)]
    if not any(weights):
        raise ValueError(f"все значения {dimension['id']} запрещены правилами")
    return rng.choices(values, weights=weights)[0]


def write_jsonl(rows: list[dict], out: Path) -> None:
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            "w", encoding="utf-8", newline="\n", dir=out.parent, delete=False
        ) as stream:
            temporary = Path(stream.name)
            for attributes in rows:
                line = json.dumps({"attributes": attributes}, ensure_ascii=False)
                stream.write(line + "\n")
        temporary.replace(out)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def sample(n: int, seed: int, out: Path, dag: bool, grounding: Path | None = None) -> None:
    dimensions = load_schema()
    marginals = load_grounding(grounding, dimensions) if grounding else {}
    rng = random.Random(seed)
    if dag:
        edges = load_edges()
        order = topological_order(dimensions, edges)
        rows = []
        for _ in range(n):
            attributes = {}
            for dimension in order:
                attributes[dimension["id"]] = weighted_choice(
                    rng, dimension, edges, attributes, marginals
                )
            rows.append(attributes)
    else:
        rows = [
            {
                dimension["id"]: rng.choices(
                    dimension["values"],
                    weights=[
                        marginals[dimension["id"]].get(value, 0.0)
                        for value in dimension["values"]
                    ],
                )[0]
                if dimension["id"] in marginals
                else rng.choice(dimension["values"])
                for dimension in dimensions
            }
            for _ in range(n)
        ]
    write_jsonl(rows, out)


def check(file: Path) -> int:
    edges = [edge for edge in load_edges() if edge["kind"] == "forbid"]
    violations = 0
    for lineno, line in enumerate(file.read_text(encoding="utf-8").splitlines(), 1):
        attributes = json.loads(line)
        attributes = attributes.get("attributes", attributes)
        for edge in edges:
            for parent_value, child_value in edge["forbid"]:
                if (
                    attributes.get(edge["parent"]) == parent_value
                    and attributes.get(edge["child"]) == child_value
                ):
                    violations += 1
                    print(
                        f"строка {lineno}: запрещённая связка "
                        f"{edge['parent']}={parent_value!r} -> {edge['child']}={child_value!r}",
                        file=sys.stderr,
                    )
    if violations:
        print(f"нарушений связок: {violations}", file=sys.stderr)
        return 1
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(prog="mantoz.persona")
    commands = parser.add_subparsers(dest="command", required=True)
    sample_parser = commands.add_parser("sample")
    sample_parser.add_argument("--n", required=True, type=positive_int)
    sample_parser.add_argument("--seed", required=True, type=int)
    sample_parser.add_argument("--out", required=True, type=Path)
    sample_parser.add_argument("--dag", action="store_true")
    sample_parser.add_argument("--grounding", type=Path)
    check_parser = commands.add_parser("check")
    check_parser.add_argument("--file", required=True, type=Path)
    args = parser.parse_args()
    if args.command == "sample":
        sample(args.n, args.seed, args.out, args.dag, args.grounding)
    else:
        sys.exit(check(args.file))


if __name__ == "__main__":
    main()
