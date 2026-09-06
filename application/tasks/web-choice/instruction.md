На странице-стенде `/app/stand.html` размещены три тарифа: `base`, `standart`,
`premium`. Прочитай план прохождения из `/app/plan.json` формата:

```json
{"inspect": ["base", "standart"], "choose": "standart"}
```

Пройди сценарий в браузере скриптом `/app/run_scenario.py`: открой страницу,
раскрой детали каждого тарифа из `inspect`, затем нажми «Выбрать» на тарифе из
`choose` (если `choose` не `null`). Скрипт запишет `/app/result.json`:

```json
{
  "actions": [{"type": "open", "target": "stand"}, ...],
  "decision": "standart"
}
```

Решение (`decision`) обязано совпадать с тарифом последнего действия `choose`
и быть одним из `base`, `standart`, `premium`. Действий должно быть не меньше
двух. Если тариф не выбран (`choose: null`), поле `decision` остаётся `null` —
это честный исход «персона ушла без выбора», верификатор его не засчитывает.
