FROM python:3.13-alpine
# Harbor исполняет команды через bash -c, а в alpine bash нет - шим на sh
# (тот же приём, что в smoke-choice).
RUN printf '#!/bin/sh\nexec /bin/sh "$@"\n' > /bin/bash && chmod +x /bin/bash
WORKDIR /app
# Анкета обещана инструкцией по пути /app/questionnaire.yaml; контекст сборки -
# только environment/, поэтому файл лежит здесь копией канонической анкеты
# из корня задачи (держать в синхроне с ../questionnaire.yaml).
COPY questionnaire.yaml /app/questionnaire.yaml
