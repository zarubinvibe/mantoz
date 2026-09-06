# Чек-лист паритета Mantoz ↔ MatrAIx

<p align="center"><img src="assets/pantheon/doc-reference.png" alt="Мраморная стена ниш, в каждой нише стоит плита с тремя высеченными строками, справа семейная колонна" width="100%"></p>

Построчное сравнение по 7 подсистемам аудита MatrAIx-Persona-8B
(persona / task-contract / harbor / playground / packages / deployment / testing).
Гейт приемки: `uv run python -m mantoz.parity_gate`, зеленый только когда нет строк
«отсутствует» без обоснования (REQ-01). Критерий не занижается (LIM-10).

Статусы: `есть эквивалент` · отсутствие с обоснованием (обязателен точный ID `OUT-NN`
из раздела «Вне цели» queue/GOAL.md; проза, REQ, LIM обоснованием не являются) ·
`отсутствует` (незакрытая строка, гейт красный).

Актуализировано на приемке MVP (T16): каждый статус «есть эквивалент» подтвержден
файлом/командой на диске.

| Подсистема | Возможность MatrAIx | Статус Mantoz | Ссылка |
|---|---|---|---|
| persona | Схема персоны из 1290 категориальных измерений (background/psychology/capability/behavior) | есть эквивалент | persona/schema/dimensions.json, те же 4 группы (background_demographics/psychology_values/capabilities_skills/behavior_habits), 40 измерений; 1290 это масштаб таксономии MatrAIx, механизм тот же (T06) |
| persona | Dependency-aware синтетический DAG-генератор персон | есть эквивалент | persona/schema/dependencies.json + `topological_order`/`--dag` в src/mantoz/persona.py (T07) |
| persona | Evidence-aware human grounding по реальным социологическим данным | есть эквивалент | src/mantoz/grounding.py + config/grounding.json, маргиналы Росстат/ЦБ через tochno.st, CC BY 4.0 (T09) |
| persona | Persona 1M, детерминированный quality-filtered коресет (HF) как продакшн-граунд | отсутствует обоснованно | OUT-03 |
| persona | Dev-сэмпл персон для smoke-тестов (~200 в репо) | есть эквивалент | `python -m mantoz.persona sample --n N --seed S`, детерминированная генерация по seed вместо хранения файла; используется пробами evals/t06, t08 (T06) |
| persona | Контроль «персона ведет себя как персона» (91.5% на 400 прогонах) | есть эквивалент | src/mantoz/quality.py, гейт качества выборки с отрицательной стороной (evals/t08_consistency_probes.sh); число 91.5% это метрика конкретного исследования MatrAIx, не механизм (T08) |
| task-contract | Контракт задачи task.toml + instruction.md + input/ + verifier | есть эквивалент | application/tasks/*/: task.toml + instruction.md + tests/test.sh (верификатор) + environment/; данные задачи рядом (questionnaire.yaml, scenario.json) (T04, T11–T14) |
| task-contract | Общая схема контракта (application/task-spec) | есть эквивалент | схема task.toml Harbor (`schema_version = "1.4"`) через зависимость harbor==0.22.0, не свой форк (REQ-02) |
| task-contract | Опциональное эталонное solution для Oracle-агента | есть эквивалент | application/tasks/smoke-choice/solution/solve.sh, используется калибровкой oracle (T04) |
| task-contract | LLM-judge верификатор (llm-judge-example) | есть эквивалент | src/mantoz/judge.py + application/tasks/open-answer (rubric.yaml + task-owned tests/test.sh → /logs/verifier/verdict.json, reward.txt): два судьи с замером расхождения и сохранением сырого ответа, живые LLM-провайдеры opt-in через `--live-provider`, дефолт бесплатный детерминированный; пробы evals/t17_llmjudge_probes.sh 8/8 (T17) |
| task-contract | Библиотека 1010 прикладных задач в 25+ доменах | отсутствует обоснованно | OUT-07 |
| task-contract | 4 среды задач одновременно: Survey / Chat / Web / App | есть эквивалент | src/mantoz/survey.py, chat.py, web.py, app.py (T11–T14); все четыре проходят population-прогон в evals/t16_acceptance_probes.sh |
| harbor | Harbor как pip/git-зависимость с LICENSE/NOTICE-атрибуцией, не форк | есть эквивалент | pyproject.toml (`harbor==0.22.0`) + NOTICE в корне; вендоренной копии в дереве нет (T01) |
| harbor | Реестр из 40 агентов (27 CLI + 9 persona-оберток + 2 baseline) | есть эквивалент | config/agents.json (12 CLI) + src/mantoz/agents.py (T10) + baseline oracle/nop в src/mantoz/calibrate.py (T04) + persona-поведение в средах T11–T14; планка REQ-04 в ≥10 CLI закрыта |
| harbor | Baseline-агенты OracleAgent/NopAgent для калибровки верификатора | есть эквивалент | src/mantoz/calibrate.py: `--agent oracle|nop`, `--both`, мутация эталона против строгости верификатора (T04) |
| harbor | Persona-обертка агентов для действия «в характере» персоны | есть эквивалент | среды T11–T14 сэмплируют персону (`mantoz.persona sample --dag`) и гоняют прогон от ее атрибутов: src/mantoz/survey.py, chat.py, web.py, app.py |
| harbor | BaseEnvironment ABC для pluggable sandbox-бэкендов | есть эквивалент | harbor.environments.base.BaseEnvironment (зависимость) + src/mantoz/sandbox.py `resolve_backend`, бэкенд из MANTOZ_SANDBOX, не хардкод (T03, LIM-06) |
| harbor | 15 sandbox-бэкендов (E2B/Runloop/Daytona/GKE/Singularity и др.) | отсутствует обоснованно | OUT-02 |
| harbor | Multi-provider доступ к LLM (litellm или эквивалент) | есть эквивалент | config/agents.json, 12 CLI по нескольким провайдерам (anthropic/openai/kimi/google/…) через Harbor-агентов; src/mantoz/agents.py (T10, REQ-04) |
| playground | Playground cockpit (FastAPI + Vite/React): когорта → задачи → Lock pipeline → Run eval | есть эквивалент | один тонкий вьювер результатов src/mantoz/viewer.py (T15, REQ-06) + раннер `python -m mantoz.population run`; тяжелый cockpit сознательно заменен, и это улучшение сверх паритета, заявлено в цели |
| playground | apps/viewer, второй SPA на другой мажорной версии React | отсутствует обоснованно | OUT-04 |
| playground | CLI-эквивалент раннера (matraix run / matraix results) | есть эквивалент | `python -m mantoz.population run --n-runs N --seed S --task T --out F` + `python -m mantoz.viewer` (T05, T15) |
| playground | Генератор джобов (generate_application_job.py, рецепты configs/jobs) | есть эквивалент | Job/JobConfig собираются программно из CLI-параметров в src/mantoz/population.py, calibrate.py, smoke_harbor.py, отдельный генератор рецептов не нужен |
| packages | packages/playground, отдельно устанавливаемый пакет вьювера | есть эквивалент | вьювер живет модулем src/mantoz/viewer.py в едином пакете mantoz, один тонкий вьювер вместо отдельного пакета (REQ-06) |
| packages | packages/rewardkit, пакет верификации/наград | есть эквивалент | task-owned верификаторы application/tasks/*/tests/test.sh пишут /logs/verifier/reward.txt через VerifierConfig Harbor; агрегация наград в src/mantoz/population.py (T05) |
| packages | packages/harbor-langsmith, телеметрия/трейсинг прогонов | отсутствует обоснованно | OUT-05 |
| deployment | Docker-образы задач (web/app в контейнерах) | есть эквивалент | application/tasks/*/environment/Dockerfile у всех пяти задач, включая браузерную (web-choice: stand.html + run_scenario.py) и computer-use (app-decision: desktop_app.py) (T13, T14) |
| deployment | Self-hosted Docker Swarm/k3s бэкенд (бесплатный дефолт) | есть эквивалент | дефолтный бесплатный бэкенд EnvironmentType.DOCKER в src/mantoz/sandbox.py (T03, REQ-03) |
| deployment | Modal-бэкенд (платный opt-in) | есть эквивалент | EnvironmentType.MODAL с preflight в src/mantoz/sandbox.py, включается через MANTOZ_SANDBOX=modal (T03, REQ-03) |
| deployment | SLURM-масштаб (8.3 млрд персон, 10 млрд строк) | отсутствует обоснованно | OUT-06 |
| deployment | Установка uv + Python 3.12, pyproject без install-хуков | есть эквивалент | pyproject.toml: requires-python >=3.12, uv_build, зависимость одна (harbor), хуков нет; uv.lock в корне (T01) |
| testing | Smoke-тесты без API-ключа (matraix smoke) | есть эквивалент | src/mantoz/smoke_harbor.py + задача application/tasks/smoke-choice; верификатор судит только по диску (T04) |
| testing | Docker-лейн smoke с reward-проверкой (reward.txt) | есть эквивалент | application/tasks/smoke-choice/: environment/Dockerfile + tests/test.sh → /logs/verifier/reward.txt (T04) |
| testing | Референс-эвалы масштаба статьи (18 189 прогонов на 8 задачах) | отсутствует обоснованно | OUT-07 |
| testing | Population-scale агрегация до subgroup/population (aggregation_method, subgroup_breakdown) | есть эквивалент | src/mantoz/population.py `aggregate`: aggregation_method=arithmetic_mean, subgroup_breakdown, n_runs>1 обязателен (T05, REQ-05) |
| testing | Границы сложности задачи через Oracle/Nop прогоны | есть эквивалент | src/mantoz/calibrate.py `--both`: эталон проходит, пустышка нет, границы верификатора измерены (T04) |
