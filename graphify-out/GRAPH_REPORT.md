# Graph Report - zarubinvibe__mantoz  (2026-09-07)

## Corpus Check
- 50 files · ~1,031,036 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 443 nodes · 542 edges · 44 communities (40 shown, 4 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 28 edges (avg confidence: 0.8)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `87eaa646`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]
- [[_COMMUNITY_Community 4|Community 4]]
- [[_COMMUNITY_Community 5|Community 5]]
- [[_COMMUNITY_Community 6|Community 6]]
- [[_COMMUNITY_Community 7|Community 7]]
- [[_COMMUNITY_Community 8|Community 8]]
- [[_COMMUNITY_Community 9|Community 9]]
- [[_COMMUNITY_Community 10|Community 10]]
- [[_COMMUNITY_Community 11|Community 11]]
- [[_COMMUNITY_Community 12|Community 12]]
- [[_COMMUNITY_Community 13|Community 13]]
- [[_COMMUNITY_Community 14|Community 14]]
- [[_COMMUNITY_Community 15|Community 15]]
- [[_COMMUNITY_Community 16|Community 16]]
- [[_COMMUNITY_Community 17|Community 17]]
- [[_COMMUNITY_Community 18|Community 18]]
- [[_COMMUNITY_Community 19|Community 19]]
- [[_COMMUNITY_Community 20|Community 20]]
- [[_COMMUNITY_Community 21|Community 21]]
- [[_COMMUNITY_Community 22|Community 22]]
- [[_COMMUNITY_Community 23|Community 23]]
- [[_COMMUNITY_Community 24|Community 24]]
- [[_COMMUNITY_Community 25|Community 25]]
- [[_COMMUNITY_Community 26|Community 26]]
- [[_COMMUNITY_Community 27|Community 27]]
- [[_COMMUNITY_Community 28|Community 28]]
- [[_COMMUNITY_Community 29|Community 29]]
- [[_COMMUNITY_Community 30|Community 30]]
- [[_COMMUNITY_Community 31|Community 31]]
- [[_COMMUNITY_Community 32|Community 32]]
- [[_COMMUNITY_Community 33|Community 33]]
- [[_COMMUNITY_Community 34|Community 34]]
- [[_COMMUNITY_Community 35|Community 35]]
- [[_COMMUNITY_Community 36|Community 36]]
- [[_COMMUNITY_Community 37|Community 37]]
- [[_COMMUNITY_Community 38|Community 38]]

## God Nodes (most connected - your core abstractions)
1. `Mantoz` - 14 edges
2. `Mantoz` - 14 edges
3. `Mantoz` - 14 edges
4. `上手引导：你的第一次 Mantoz 运行` - 14 edges
5. `Onboarding: your first Mantoz run` - 14 edges
6. `Онбординг: первый прогон Mantoz` - 14 edges
7. `sample()` - 13 edges
8. `Решения проекта «Mantoz»` - 11 edges
9. `check()` - 10 edges
10. `main()` - 10 edges

## Surprising Connections (you probably didn't know these)
- `_live_judges()` --calls--> `command()`  [INFERRED]
  src/mantoz/judge.py → application/tasks/app-decision/environment/run_scenario.py
- `run_persona_trial()` --calls--> `run_trial_result()`  [INFERRED]
  src/mantoz/survey.py → src/mantoz/calibrate.py
- `run_persona_trial()` --calls--> `judge_trial()`  [INFERRED]
  src/mantoz/survey.py → src/mantoz/calibrate.py
- `run_persona_trial()` --calls--> `resolve_backend()`  [INFERRED]
  src/mantoz/survey.py → src/mantoz/sandbox.py
- `run()` --calls--> `sample()`  [INFERRED]
  src/mantoz/survey.py → src/mantoz/persona.py

## Communities (44 total, 4 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.08
Nodes (25): 怎么更新, 第 1 步：打开终端, 第 10 步：换一个环境试试, 接下来看什么, 如果这些对你有用, 第 2 步：确认有 Python, 第 3 步：把代码拿下来, 第 4 步：安装 uv (+17 more)

### Community 1 - "Community 1"
Cohesion: 0.08
Nodes (25): code:bash (python3 --version), code:bash (uv run python -m mantoz.population run --n-runs 3 --seed 7 -), code:bash (cd ~/mantoz), code:bash (git clone https://github.com/zarubinvibe/mantoz.git ~/mantoz), code:bash (curl -LsSf https://astral.sh/uv/install.sh | sh), code:bash (bash install.sh), code:bash (uv run python -m mantoz.persona sample --n 200 --seed 7 --da), code:bash (python3 -c "import json;print(len(json.load(open('runs/peopl) (+17 more)

### Community 2 - "Community 2"
Cohesion: 0.08
Nodes (25): Как обновляться, Шаг 1. Откройте терминал, Шаг 10. Попробуйте другую среду, Куда дальше, Если пригодилось, Шаг 2. Проверьте, есть ли Python, Шаг 3. Заберите код, Шаг 4. Поставьте uv (+17 more)

### Community 3 - "Community 3"
Cohesion: 0.15
Nodes (19): judge_trial(), main(), Прогоняет задачу через агента Harbor, возвращает TrialResult., Судит TrialResult: (прошел, строка-исход). Прошел == положительный     ВЕРДИКТ В, Прогоняет задачу через агента Harbor и судит вердикт верификатора., run(), run_trial(), run_trial_result() (+11 more)

### Community 4 - "Community 4"
Cohesion: 0.1
Nodes (20): 目录, 第 1 步：生成这些人, 快速开始, 简单对比, 简单词汇, 安全与隐私, 局限, 点亮星标与参与 (+12 more)

### Community 5 - "Community 5"
Cohesion: 0.1
Nodes (20): code:bash (git clone https://github.com/zarubinvibe/mantoz.git ~/mantoz), Contents, How It Works, License, Limits, Mantoz, Olympuz family, Quickstart (+12 more)

### Community 6 - "Community 6"
Cohesion: 0.1
Nodes (20): Оглавление, Шаг 1: Собери людей, Быстрый старт, Простое сравнение, Простые слова, Безопасность и приватность, Ограничения, Звезда и вклад (+12 more)

### Community 7 - "Community 7"
Cohesion: 0.19
Nodes (18): command(), list_agents(), load_registry(), main(), resolve(), _exact_judge(), _extract_json(), judge_answer() (+10 more)

### Community 8 - "Community 8"
Cohesion: 0.2
Nodes (15): check(), load_edges(), load_grounding(), load_schema(), main(), Kahn: родители измерений идут раньше потомков. Граф обязан быть ацикличным., sample(), topological_order() (+7 more)

### Community 9 - "Community 9"
Cohesion: 0.21
Nodes (14): completes_scenario(), main(), plan_actions(), Среда Web: персона проходит сценарий выбора тарифа в браузере.  Дефолт — без выз, Читает result.json, скопированный верификатором контейнера на хост., Уход без выбора - тоже следствие персоны: бросающие не доходят до кнопки., Строит план сценария из признаков персоны, детерминированно., Прогоняет web-задачу одной персоной ЧЕРЕЗ Harbor.      План действий выводится д (+6 more)

### Community 10 - "Community 10"
Cohesion: 0.38
Nodes (13): check(), check_agent_registry(), check_attribution(), check_data_boundary(), check_grounding_registry(), check_parity_checklist(), check_persona_dag(), check_persona_schema() (+5 more)

### Community 11 - "Community 11"
Cohesion: 0.3
Nodes (11): answer_questionnaire(), completes_questionnaire(), load_questionnaire(), main(), Среда Survey: персона отвечает на анкету детерминированно, по своим признакам., Прогоняет survey-задачу одной персоной ЧЕРЕЗ Harbor.      Ответы выводятся детер, Незавершённость тоже следствие персоны: бросающие на полпути не дописывают., run() (+3 more)

### Community 12 - "Community 12"
Cohesion: 0.3
Nodes (11): main(), plan_decision(), App-среда: персона решает в desktop-приложении через Harbor., Детерминированно выводит решение из доверия к технологии и приватности., _read_container_result(), run(), run_persona_trial(), _screenshot_evidence() (+3 more)

### Community 13 - "Community 13"
Cohesion: 0.17
Nodes (11): D-01 · Harbor - зависимость, а не форк и не своя обвязка, D-02 · Sandbox-бэкенды - pluggable, минимум два с первого дня, D-03 · Верификация - population-scale столп, а не пара агентов-проверяющих, D-04 · Своя схема персон и свой генератор, Persona1M MatrAIx только для bootstrap, D-05 · Граунд персон - только источники с явным коммерческим разрешением, D-06 · Тонкий вьювер сразу, не два параллельных SPA, D-07 · Реестр агентов - 10+ CLI, не тройка Helioz, D-08 · Планирование - схема Helioz, не GSD (+3 more)

### Community 14 - "Community 14"
Cohesion: 0.31
Nodes (9): acyclic(), boost_map(), build_dimensions(), build_edges(), load(), main(), Ядро идёт первым и неизменным, дальше домен на фасет., Карта весов между двумя порядковыми шкалами.      Ребро `prefer` без весов ничег (+1 more)

### Community 15 - "Community 15"
Cohesion: 0.31
Nodes (9): evaluate(), _honest_justification(), load_out_scopes(), main(), Гейт приёмки паритета Mantoz ↔ MatrAIx (REQ-01).  Читает docs/PARITY.md (или пут, Точный ID из «Вне цели», чья область действия покрывает подсистему строки., Вернуть список незакрытых строк таблицы паритета., ``OUT-NN`` → подсистемы из ``[покрывает: …]`` раздела «Вне цели» GOAL.md.      П (+1 more)

### Community 16 - "Community 16"
Cohesion: 0.2
Nodes (9): Agent Rules — Mantoz, Build, run, test, code:bash (uv venv --python 3.12 && uv pip install -e .   # install), First contact with a stranger, Hard rules, Publication, Style, The knowledge graph answers first (+1 more)

### Community 17 - "Community 17"
Cohesion: 0.28
Nodes (4): DecisionApp, Минимальное desktop-приложение: диалог разрешения уведомлений., main(), Проходит desktop-сценарий мышью и снимает виртуальный дисплей.

### Community 18 - "Community 18"
Cohesion: 0.31
Nodes (5): BaseAgent, main(), run(), smoke(), StubPersona

### Community 19 - "Community 19"
Cohesion: 0.22
Nodes (8): 第 1 步：先看看你机器上已经有什么, 第 2 步：把项目放到磁盘上, 第 3 步：装好运行环境, 第 4 步：把这些人生成出来, 第 5 步：跑你的任务，不是我的, 第 6 步：给你看结果，也给你看数据边界, code:bash (uv run python -m mantoz.viewer render --report runs/first.js), 用对话安装 Mantoz

### Community 20 - "Community 20"
Cohesion: 0.22
Nodes (8): code:bash (uv run python -m mantoz.viewer render --report runs/first.js), Installing Mantoz as a conversation, Step 1: I look at what you already have, Step 2: I put the project on disk, Step 3: I set up the environment, Step 4: I build the people, Step 5: I run your task, not mine, Step 6: I show the result and the data boundary

### Community 21 - "Community 21"
Cohesion: 0.22
Nodes (8): Шаг 1: Смотрю, что у тебя уже стоит, Шаг 2: Кладу проект на диск, Шаг 3: Ставлю окружение, Шаг 4: Собираю людей, Шаг 5: Прогоняю твою задачу, а не мою, Шаг 6: Показываю результат и границу данных, code:bash (uv run python -m mantoz.viewer render --report runs/first.js), Установка Mantoz разговором

### Community 22 - "Community 22"
Cohesion: 0.43
Nodes (7): esc(), main(), Тонкий вьювер отчётов population: самодостаточный HTML без сборки и npm., Несостоявшиеся прогоны - ОТДЕЛЬНЫЙ блок, они не растворяются в долях., render(), render_failed_trials(), render_report()

### Community 23 - "Community 23"
Cohesion: 0.25
Nodes (7): 安装, 一次改动的流程, 会被合并的, 不会被合并的, 报告问题, code:bash (git clone https://github.com/zarubinvibe/mantoz.git), 参与 Mantoz

### Community 24 - "Community 24"
Cohesion: 0.25
Nodes (7): code:bash (git clone https://github.com/zarubinvibe/mantoz.git), Contributing to Mantoz, Reporting a problem, Set up, The path of a change, What does not, What gets merged

### Community 25 - "Community 25"
Cohesion: 0.25
Nodes (7): Установка, Путь изменения, Что примут, Что не примут, Как сообщить о проблеме, code:bash (git clone https://github.com/zarubinvibe/mantoz.git), Как участвовать в Mantoz

### Community 26 - "Community 26"
Cohesion: 0.29
Nodes (6): Безопасность и приватность, Граница по данным, Как сообщить об уязвимости, code:bash (sh evals/licence_boundary_gate.sh), Чего Mantoz касается, От чего Mantoz не защитит

### Community 27 - "Community 27"
Cohesion: 0.29
Nodes (6): 安全与隐私, 数据边界, 如何报告漏洞, code:bash (sh evals/licence_boundary_gate.sh), Mantoz 会碰到什么, Mantoz 不能替你挡住的

### Community 28 - "Community 28"
Cohesion: 0.29
Nodes (6): code:bash (sh evals/licence_boundary_gate.sh), Reporting a vulnerability, Security and Privacy, The data boundary, What Mantoz does not protect you from, What Mantoz touches

### Community 29 - "Community 29"
Cohesion: 0.29
Nodes (6): Конечная цель владельца, Нельзя, Принято по умолчанию, Вне цели, Что станет истинным, Требования

### Community 30 - "Community 30"
Cohesion: 0.53
Nodes (4): aggregate(), main(), run(), write_report()

### Community 31 - "Community 31"
Cohesion: 0.6
Nodes (5): build_marginals(), load_rows(), main(), validate_source(), write_marginals()

### Community 32 - "Community 32"
Cohesion: 0.33
Nodes (5): Исполнение агентов, Верификация, Персоны и граунд, Приемка, Словарь терминов - Mantoz

### Community 33 - "Community 33"
Cohesion: 0.6
Nodes (4): carve(), fit(), main(), Largest size that still leaves a margin inside the plate.

### Community 34 - "Community 34"
Cohesion: 0.4
Nodes (4): Источники, Матрица возможностей, Где мы отстаем и что с этим делаем, Догнать или превзойти: Mantoz против MatrAIx

## Knowledge Gaps
- **201 isolated node(s):** `Ядро идёт первым и неизменным, дальше домен на фасет.`, `Карта весов между двумя порядковыми шкалами.      Ребро `prefer` без весов ничег`, `Связи ядра сохраняются как есть, к ним добавляются объявленные зависимости домен`, `Схема собрана прибором. Правка руками разъедется с источником молча.`, `Largest size that still leaves a margin inside the plate.` (+196 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **4 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `run_persona_trial()` connect `Community 7` to `Community 3`?**
  _High betweenness centrality (0.027) - this node is a cross-community bridge._
- **Why does `sample()` connect `Community 8` to `Community 3`, `Community 9`, `Community 11`, `Community 12`, `Community 30`?**
  _High betweenness centrality (0.023) - this node is a cross-community bridge._
- **Why does `resolve_backend()` connect `Community 3` to `Community 7`, `Community 9`, `Community 11`, `Community 12`, `Community 18`?**
  _High betweenness centrality (0.021) - this node is a cross-community bridge._
- **What connects `Ядро идёт первым и неизменным, дальше домен на фасет.`, `Карта весов между двумя порядковыми шкалами.      Ребро `prefer` без весов ничег`, `Связи ядра сохраняются как есть, к ним добавляются объявленные зависимости домен` to the rest of the system?**
  _201 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Community 0` be split into smaller, more focused modules?**
  _Cohesion score 0.08 - nodes in this community are weakly interconnected._
- **Should `Community 1` be split into smaller, more focused modules?**
  _Cohesion score 0.08 - nodes in this community are weakly interconnected._
- **Should `Community 2` be split into smaller, more focused modules?**
  _Cohesion score 0.08 - nodes in this community are weakly interconnected._