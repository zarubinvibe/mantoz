import argparse
import csv
import json
import sys
import tempfile
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "config" / "grounding.json"
SCHEMA = ROOT / "persona" / "schema" / "dimensions.json"


def load_rows(path: Path) -> list[dict]:
    if not path.is_file():
        raise FileNotFoundError(f"файл данных отсутствует: {path}")
    # ponytail: whole-file import; stream rows if source exports exceed memory.
    if path.suffix.lower() == ".csv":
        with path.open(encoding="utf-8-sig", newline="") as stream:
            return list(csv.DictReader(stream))
    if path.suffix.lower() == ".jsonl":
        lines = path.read_text(encoding="utf-8").splitlines()
        rows = [json.loads(line) for line in lines if line.strip()]
    else:
        rows = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(rows, dict):
            rows = rows.get("rows")
    if not isinstance(rows, list) or not all(isinstance(row, dict) for row in rows):
        raise ValueError(
            "данные должны быть массивом объектов, JSONL или CSV"
        )
    return rows


def build_marginals(rows: list[dict]) -> dict[str, dict[str, float]]:
    dimensions = json.loads(SCHEMA.read_text(encoding="utf-8"))["dimensions"]
    counts: dict[str, Counter] = {dimension["id"]: Counter() for dimension in dimensions}
    allowed = {dimension["id"]: set(dimension["values"]) for dimension in dimensions}
    for row_number, row in enumerate(rows, 1):
        for dimension, values in allowed.items():
            value = row.get(dimension)
            if value in (None, ""):
                continue
            if value not in values:
                raise ValueError(
                    f"строка {row_number}: {dimension}={value!r} "
                    "отсутствует в persona-схеме"
                )
            counts[dimension][value] += 1
    marginals = {}
    for dimension, distribution in counts.items():
        total = distribution.total()
        if total:
            marginals[dimension] = {
                value: count / total for value, count in distribution.items()
            }
    if not marginals:
        raise ValueError("в данных нет измерений из persona-схемы")
    return marginals


def validate_source(source: str) -> None:
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    if source not in {item["id"] for item in registry["sources"]}:
        raise ValueError(
            f"источник {source!r} отсутствует в config/grounding.json"
        )


def write_marginals(source: str, dimensions: dict, out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            "w", encoding="utf-8", dir=out.parent, delete=False
        ) as stream:
            temporary = Path(stream.name)
            json.dump(
                {"source": source, "dimensions": dimensions},
                stream,
                ensure_ascii=False,
                indent=2,
            )
            stream.write("\n")
        temporary.replace(out)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def main() -> None:
    parser = argparse.ArgumentParser(prog="mantoz.grounding")
    commands = parser.add_subparsers(dest="command", required=True)
    importer = commands.add_parser("import")
    importer.add_argument("--source", required=True)
    importer.add_argument("--path", required=True, type=Path)
    importer.add_argument("--out", type=Path)
    args = parser.parse_args()
    try:
        validate_source(args.source)
        rows = load_rows(args.path)
        if args.out is None:
            raise ValueError("не указан --out для файла маргиналов")
        write_marginals(args.source, build_marginals(rows), args.out)
    except (FileNotFoundError, json.JSONDecodeError, OSError, ValueError) as error:
        parser.exit(1, f"ошибка: {error}\n")


if __name__ == "__main__":
    main()
