import argparse
import json
import shutil
import sys
from pathlib import Path

REGISTRY = Path(__file__).resolve().parents[2] / "config" / "agents.json"


def load_registry() -> list[dict]:
    return json.loads(REGISTRY.read_text(encoding="utf-8"))["agents"]


def list_agents() -> None:
    agents = load_registry()
    installed = [a for a in agents if a["installed"]]
    missing = [a for a in agents if not a["installed"]]
    print("Установленные:")
    for a in installed:
        print(f"  {a['id']} -> {a['harbor_agent']} (бинарь: {a.get('binary') or a['id']})")
    print("Не установленные:")
    for a in missing:
        print(f"  {a['id']} -> {a['harbor_agent']}")


def resolve(agent_id: str) -> None:
    for a in load_registry():
        if a["id"] == agent_id or a.get("binary") == agent_id:
            # Отказ при обмане: installed=true обязан подтверждаться бинарём.
            if a["installed"] and shutil.which(a.get("binary") or a["id"]) is None:
                print(f"ошибка: {agent_id} помечен installed, но бинаря нет", file=sys.stderr)
                sys.exit(2)
            print(a["harbor_agent"])
            return
    print(f"ошибка: неизвестный агент '{agent_id}'", file=sys.stderr)
    sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(prog="mantoz.agents")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("list")
    resolve_parser = commands.add_parser("resolve")
    resolve_parser.add_argument("--id", required=True)
    args = parser.parse_args()
    if args.command == "list":
        list_agents()
    else:
        resolve(args.id)


if __name__ == "__main__":
    main()
