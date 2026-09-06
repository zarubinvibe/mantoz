Пройди desktop-сценарий в виртуальном дисплее командой
`xvfb-run -a python3 /app/run_scenario.py`. Сценарий читает цель из
`/app/plan.json`, сохраняет PNG до и после клика, а также
`/app/result.json` со следом действий и решением `allow`, `later` или
`deny`.
