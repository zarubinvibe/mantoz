"""Среда Survey: персона отвечает на анкету детерминированно, по своим признакам.

Дефолт — без вызова модели: ответ выводится правилами из атрибутов персоны,
иначе population-прогон стал бы платным по числу персон. Живого режима модели
намеренно нет: заводить его — только за отдельным флагом и отдельным тикетом.
"""

import argparse
import asyncio
import json
import shutil
import sys
import tempfile
from pathlib import Path

import yaml

from mantoz.calibrate import judge_trial, run_trial_result
from mantoz.persona import sample
from mantoz.sandbox import resolve_backend

TASK_DIR = (
    Path(__file__).resolve().parents[2] / "application" / "tasks" / "survey-feedback"
)
QUESTIONNAIRE = TASK_DIR / "questionnaire.yaml"

LIKERT_BY_DIGITAL_LITERACY = {"базовая": 2, "уверенная": 4, "продвинутая": 5}
LIKERT_BY_PRIVACY = {"низкая": 5, "средняя": 3, "высокая": 2}
FREQUENCY_BY_ADOPTION = {
    "сразу": "каждый день",
    "после проверки другими": "несколько раз в неделю",
    "после широкого распространения": "несколько раз в месяц",
    "избегает": "реже одного раза в месяц",
}
TEXT_BY_FEEDBACK_STYLE = {
    "прямой": "Сделайте вход без СМС и уберите лишние шаги.",
    "дипломатичный": "В целом сервис удобный, но хотелось бы проще восстанавливать доступ.",
    "сдержанный": "Пока всё устраивает.",
}
DETAIL_ADDENDUM = " Особенно это мешает, когда записываешься в спешке."


def load_questionnaire(path: Path = QUESTIONNAIRE) -> list[dict]:
    return yaml.safe_load(path.read_text(encoding="utf-8"))["questions"]


def completes_questionnaire(attributes: dict) -> bool:
    """Незавершённость тоже следствие персоны: бросающие на полпути не дописывают."""
    return not (
        attributes["follow_through"] == "часто бросает"
        and (
            attributes["conscientiousness"] == "низкая"
            or attributes["digital_literacy"] == "базовая"
        )
    )


def answer_questionnaire(attributes: dict, questions: list[dict]) -> dict:
    answers = {}
    for question in questions:
        qid = question["id"]
        if qid == "usage_frequency":
            answers[qid] = FREQUENCY_BY_ADOPTION[attributes["technology_adoption"]]
        elif qid == "usability_rating":
            answers[qid] = LIKERT_BY_DIGITAL_LITERACY[attributes["digital_literacy"]]
        elif qid == "data_trust":
            answers[qid] = LIKERT_BY_PRIVACY[attributes["privacy_sensitivity"]]
        elif qid == "recommendation":
            score = (
                LIKERT_BY_DIGITAL_LITERACY[attributes["digital_literacy"]]
                + LIKERT_BY_PRIVACY[attributes["privacy_sensitivity"]]
                + (1 if attributes["agreeableness"] == "высокая" else 0)
            )
            answers[qid] = (
                "да" if score >= 8
                else "скорее да" if score >= 6
                else "скорее нет" if score >= 4
                else "нет"
            )
        elif qid == "improvement_text":
            if not completes_questionnaire(attributes):
                continue  # персона бросила анкету на свободном вопросе
            text = TEXT_BY_FEEDBACK_STYLE[attributes["feedback_style"]]
            if attributes["response_detail_preference"] == "подробная":
                text += DETAIL_ADDENDUM
            answers[qid] = text
        else:  # ponytail: новый вопрос без правила - крах, а не молчаливый пропуск
            raise ValueError(f"нет правила ответа на вопрос {qid}")
    return answers


def validate_answers(answers: object, questions: list[dict]) -> list[str]:
    if not isinstance(answers, dict):
        return ["answers не словарь"]
    errors = []
    for question in questions:
        qid, qtype = question["id"], question["type"]
        if qid not in answers:
            errors.append(f"нет ответа на {qid}")
            continue
        value = answers[qid]
        if qtype == "single_choice" and value not in question["options"]:
            errors.append(f"{qid}: {value!r} вне списка options")
        elif qtype == "likert":
            low, high = question["scale"]["min"], question["scale"]["max"]
            if not (isinstance(value, int) and low <= value <= high):
                errors.append(f"{qid}: {value!r} вне шкалы {low}..{high}")
        elif qtype == "free_text" and not (isinstance(value, str) and value.strip()):
            errors.append(f"{qid}: пустой свободный ответ")
    return errors


async def run_persona_trial(attributes: dict, jobs_root: Path) -> dict:
    """Прогоняет survey-задачу одной персоной ЧЕРЕЗ Harbor.

    Ответы выводятся детерминированно из признаков персоны на хосте (без
    платной модели), запекаются в solution/solve.sh копии задачи, а пишет их
    в контейнер и судит верификатор - уже настоящий прогон Harbor.
    """
    questions = load_questionnaire()
    answers = answer_questionnaire(attributes, questions)
    jobs_root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="survey-", dir=jobs_root) as tmp:
        task_dir = Path(tmp) / "task"
        shutil.copytree(TASK_DIR, task_dir)
        solution_dir = task_dir / "solution"
        solution_dir.mkdir()
        payload = json.dumps({"answers": answers}, ensure_ascii=False, indent=2)
        (solution_dir / "solve.sh").write_text(
            "#!/bin/sh\n"
            "# Ответы персоны, запечённые хостом (детерминированный режим).\n"
            "cat > /app/answers.json <<'ANSWERS'\n"
            f"{payload}\n"
            "ANSWERS\n",
            encoding="utf-8",
        )
        trial = await run_trial_result("oracle", Path(tmp) / "jobs", task_dir)
    passed, detail = judge_trial(trial)
    # Инфраструктурный сбой != исход персоны: крах трайла, либо отрицательный
    # вердикт при ПОЛНОЙ анкете (честные ответы валидны по построению, значит
    # контейнер их потерял). Честный провал - только неполная анкета.
    infrastructure_failure = not passed and (
        detail.startswith("крах прогона:")
        or not validate_answers(answers, questions)
    )
    return {
        "answers": answers,
        "passed": passed,
        "detail": detail,
        "infrastructure_failure": infrastructure_failure,
        "trial_id": str(trial.id),
        "agent": trial.agent_info.name if trial.agent_info else "oracle",
        "backend": resolve_backend().value,
    }


def run(persona_seed: int, out: Path) -> int:
    with tempfile.TemporaryDirectory(prefix="survey-persona-") as tmp:
        personas_path = Path(tmp) / "persona.jsonl"
        sample(1, persona_seed, personas_path, dag=True)
        attributes = json.loads(
            personas_path.read_text(encoding="utf-8").splitlines()[0]
        )["attributes"]
    # jobs_dir обязан лежать под $HOME - см. комментарий в mantoz.calibrate.
    outcome = asyncio.run(
        run_persona_trial(attributes, Path.home() / ".cache" / "mantoz")
    )
    result = {
        "task": "survey-feedback",
        "environment": "survey",
        "persona_seed": persona_seed,
        "persona": attributes,
        **outcome,
    }
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    # Тихий откат запрещён: инфраструктурный сбой (классификация - в
    # run_persona_trial) - это провал команды с названной причиной. Провал
    # при неполной анкете - честный исход (персона бросила анкету), он
    # остаётся в reward, код не меняется.
    if outcome["infrastructure_failure"]:
        print(f"прогон survey не состоялся: {outcome['detail']}", file=sys.stderr)
        return 1
    return 0


def verify(file: Path) -> int:
    result = json.loads(file.read_text(encoding="utf-8"))
    errors = validate_answers(result.get("answers"), load_questionnaire())
    for error in errors:
        print(f"верификатор: {error}", file=sys.stderr)
    if errors:
        print(f"верификатор: провал ({len(errors)} ошибок)", file=sys.stderr)
        return 1
    print("верификатор: анкета полна и в формате")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(prog="mantoz.survey")
    commands = parser.add_subparsers(dest="command", required=True)
    run_parser = commands.add_parser("run")
    run_parser.add_argument("--persona-seed", required=True, type=int)
    run_parser.add_argument("--out", required=True, type=Path)
    verify_parser = commands.add_parser("verify")
    verify_parser.add_argument("--file", required=True, type=Path)
    args = parser.parse_args()
    if args.command == "run":
        sys.exit(run(args.persona_seed, args.out))
    else:
        sys.exit(verify(args.file))


if __name__ == "__main__":
    main()
