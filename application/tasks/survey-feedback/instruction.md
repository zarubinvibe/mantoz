Прочитай анкету /app/questionnaire.yaml и запиши свои ответы в файл
/app/answers.json — объект JSON вида {"answers": {"<id вопроса>": <ответ>, ...}}.

Ответ обязан покрывать КАЖДЫЙ вопрос анкеты:
- single_choice: ровно одна строка из списка options;
- likert: целое число от scale.min до scale.max;
- free_text: непустая строка.
