"""Рубричный судья свободных ответов: бесплатный детерминированный дефолт."""

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from mantoz.agents import load_registry

ROOT = Path(__file__).resolve().parents[2]
TASK_DIR = ROOT / "application" / "tasks" / "open-answer"
DEFAULT_RUBRIC = TASK_DIR / "rubric.yaml"
LIVE_COMMANDS = {
    "claude": lambda binary, prompt: [
        binary,
        "--print",
        "--output-format",
        "text",
        "--no-session-persistence",
        prompt,
    ],
    "codex": lambda binary, prompt: [
        binary,
        "exec",
        "--ephemeral",
        "--skip-git-repo-check",
        "--sandbox",
        "read-only",
        prompt,
    ],
    "kimi": lambda binary, prompt: [
        binary,
        "--prompt",
        prompt,
        "--output-format",
        "text",
    ],
}


def load_rubric(path: Path) -> dict:
    try:
        rubric = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(
            f"не удалось прочитать рубрику {path}: {exc}"
        ) from exc
    if not isinstance(rubric, dict) or not isinstance(rubric.get("criteria"), list):
        raise ValueError("rubric.yaml обязан содержать список criteria")
    criteria = rubric["criteria"]
    if not criteria:
        raise ValueError("rubric.yaml содержит пустой criteria")
    for criterion in criteria:
        valid = (
            isinstance(criterion, dict)
            and isinstance(criterion.get("id"), str)
            and isinstance(criterion.get("weight"), (int, float))
            and not isinstance(criterion["weight"], bool)
            and criterion["weight"] > 0
            and all(
                isinstance(criterion.get(key), list)
                and criterion[key]
                and all(isinstance(value, str) and value for value in criterion[key])
                for key in ("terms", "stems")
            )
        )
        if not valid:
            raise ValueError(f"некорректный критерий: {criterion!r}")
    max_score = rubric.get("max_score")
    pass_score = rubric.get("pass_score")
    if (
        not isinstance(max_score, (int, float))
        or isinstance(max_score, bool)
        or max_score <= 0
        or abs(sum(c["weight"] for c in criteria) - max_score) > 1e-9
        or not isinstance(pass_score, (int, float))
        or isinstance(pass_score, bool)
        or not 0 <= pass_score <= max_score
    ):
        raise ValueError(
            "max_score обязан равняться сумме весов, pass_score — лежать в шкале"
        )
    return rubric


def _normalized(text: str) -> str:
    return " ".join(text.casefold().split())


def _opinion(judge_id: str, score: float, passed: list[str], missed: list[str]) -> dict:
    rationale = (
        f"найдены: {', '.join(passed) or 'нет'}; "
        f"не найдены: {', '.join(missed) or 'нет'}"
    )
    raw = json.dumps(
        {"judge": judge_id, "score": round(score, 4), "rationale": rationale},
        ensure_ascii=False,
    )
    return {"id": judge_id, "score": round(score, 4), "rationale": rationale, "raw": raw}


def _exact_judge(answer: str, rubric: dict) -> dict:
    text = _normalized(answer)
    score = 0.0
    passed, missed = [], []
    for criterion in rubric["criteria"]:
        found = any(
            re.search(rf"(?<!\w){re.escape(_normalized(term))}(?!\w)", text)
            for term in criterion["terms"]
        )
        (passed if found else missed).append(criterion["id"])
        if found:
            score += criterion["weight"]
    return _opinion("rules-exact-v1", score, passed, missed)


def _stem_judge(answer: str, rubric: dict) -> dict:
    text = _normalized(answer)
    score = 0.0
    passed, missed = [], []
    for criterion in rubric["criteria"]:
        found = all(stem.casefold() in text for stem in criterion["stems"])
        (passed if found else missed).append(criterion["id"])
        if found:
            score += criterion["weight"]
    return _opinion("rules-stem-v1", score, passed, missed)


def _extract_json(raw: str) -> dict:
    decoder = json.JSONDecoder()
    for offset, char in enumerate(raw):
        if char != "{":
            continue
        try:
            value, _ = decoder.raw_decode(raw[offset:])
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict) and {"score", "rationale"} <= value.keys():
            return value
    raise ValueError("судья не вернул JSON с score и rationale")


def _live_judges(answer: str, rubric: dict, provider_ids: list[str]) -> list[dict]:
    if len(provider_ids) < 2:
        raise ValueError(
            "живой режим требует минимум два --live-provider"
        )
    registry = {entry["id"]: entry for entry in load_registry()}
    prompt = (
        "Оцени ответ по рубрике. Верни только JSON: "
        '{"score": число, "rationale": "обоснование"}.\n'
        f"Рубрика: {json.dumps(rubric, ensure_ascii=False)}\nОтвет: {answer}"
    )
    opinions = []
    for index, provider_id in enumerate(provider_ids, 1):
        provider = registry.get(provider_id)
        if provider is None:
            raise ValueError(f"провайдера {provider_id!r} нет в config/agents.json")
        binary_name = provider.get("binary") or provider_id
        binary = shutil.which(binary_name)
        if not provider.get("installed") or binary is None:
            raise ValueError(f"провайдер {provider_id!r} не установлен")
        command = LIVE_COMMANDS.get(binary_name)
        if command is None:
            raise ValueError(
                f"для CLI {binary_name!r} нет безопасной non-interactive команды"
            )
        result = subprocess.run(
            command(binary, prompt),
            capture_output=True,
            text=True,
            timeout=180,
            check=False,
            cwd=ROOT,
        )
        if result.returncode != 0:
            raise RuntimeError(
                f"провайдер {provider_id!r} завершился с кодом {result.returncode}"
            )
        parsed = _extract_json(result.stdout)
        score, rationale = parsed["score"], parsed["rationale"]
        if (
            not isinstance(score, (int, float))
            or isinstance(score, bool)
            or not 0 <= score <= rubric["max_score"]
            or not isinstance(rationale, str)
            or not rationale.strip()
        ):
            raise ValueError(
                f"провайдер {provider_id!r} вернул вердикт вне рубрики"
            )
        opinions.append(
            {
                "id": f"{provider_id}-{index}",
                "provider": provider_id,
                "score": score,
                "rationale": rationale,
                "raw": result.stdout,
            }
        )
    return opinions


def judge_answer(
    answer: str,
    rubric: dict,
    simulate_disagreement: bool = False,
    live_providers: list[str] | None = None,
) -> dict:
    if not isinstance(answer, str) or not answer.strip():
        raise ValueError("answer обязан быть непустой строкой")
    opinions = (
        _live_judges(answer, rubric, live_providers)
        if live_providers
        else [_exact_judge(answer, rubric), _stem_judge(answer, rubric)]
    )
    if simulate_disagreement:
        opinions[1]["score"] = 0.0 if opinions[0]["score"] > 0 else rubric["max_score"]
        opinions[1]["rationale"] += (
            "; simulate-disagreement: оценка намеренно изменена"
        )
        opinions[1]["raw"] = json.dumps(opinions[1], ensure_ascii=False)
    scores = [float(opinion["score"]) for opinion in opinions]
    disagreement = max(scores) - min(scores)
    score = sum(scores) / len(scores)
    return {
        "score": round(score, 4),
        "rationale": (
            f"Среднее {score:.4g} по {len(opinions)} судьям; "
            f"диапазон расхождения {disagreement:.4g}."
        ),
        "raw": "\n".join(opinion["raw"] for opinion in opinions),
        "judges": opinions,
        "disagreement": round(disagreement, 4),
        "aggregation_method": "arithmetic_mean",
    }


def write_verdict(verdict: dict, out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            "w", encoding="utf-8", newline="\n", dir=out.parent, delete=False
        ) as stream:
            temporary = Path(stream.name)
            json.dump(verdict, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
        temporary.replace(out)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def _verifier_verdict(trial) -> dict | None:
    path = Path(trial.trial_uri.removeprefix("file://")) / "verifier" / "verdict.json"
    try:
        verdict = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return verdict if isinstance(verdict, dict) else None


async def run_persona_trial(attributes: dict, jobs_root: Path) -> dict:
    # Harbor грузится только population-путём; локальный verify остаётся stdlib-only.
    from mantoz.calibrate import judge_trial, run_trial_result
    from mantoz.sandbox import resolve_backend

    answer = (
        "Кофе горький из-за кофеина и хлорогеновых кислот, "
        "которые дают горькие ноты."
        if attributes["response_detail_preference"] == "подробная"
        else "Кофе горький из-за кофеина и хлорогеновых кислот."
    )
    jobs_root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="open-answer-", dir=jobs_root) as tmp:
        task_dir = Path(tmp) / "task"
        shutil.copytree(TASK_DIR, task_dir)
        solution_dir = task_dir / "solution"
        solution_dir.mkdir()
        (solution_dir / "solve.sh").write_text(
            "#!/bin/sh\ncat > /app/answer.txt <<'ANSWER'\n"
            f"{answer}\nANSWER\n",
            encoding="utf-8",
        )
        trial = await run_trial_result("oracle", Path(tmp) / "jobs", task_dir)
        verdict = _verifier_verdict(trial)
    passed, detail = judge_trial(trial)
    expected = judge_answer(answer, load_rubric(DEFAULT_RUBRIC))
    infrastructure_failure = (
        trial.exception_info is not None
        or verdict is None
        or verdict.get("score") != expected["score"]
    )
    return {
        "answer": answer,
        "verdict": verdict,
        "passed": passed,
        "detail": detail,
        "infrastructure_failure": infrastructure_failure,
        "trial_id": str(trial.id),
        "agent": trial.agent_info.name if trial.agent_info else "oracle",
        "backend": resolve_backend().value,
    }


def main() -> None:
    parser = argparse.ArgumentParser(prog="mantoz.judge")
    commands = parser.add_subparsers(dest="command", required=True)
    verify_parser = commands.add_parser("verify")
    verify_parser.add_argument("--answer", required=True)
    verify_parser.add_argument("--rubric", required=True, type=Path)
    verify_parser.add_argument("--out", required=True, type=Path)
    verify_parser.add_argument("--simulate-disagreement", action="store_true")
    verify_parser.add_argument(
        "--live-provider",
        action="append",
        dest="live_providers",
        help=(
            "opt-in платный/сетевой судья из config/agents.json; "
            "повторить минимум дважды"
        ),
    )
    args = parser.parse_args()
    try:
        verdict = judge_answer(
            args.answer,
            load_rubric(args.rubric),
            args.simulate_disagreement,
            args.live_providers,
        )
        write_verdict(verdict, args.out)
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as exc:
        print(f"ошибка судьи: {exc}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
