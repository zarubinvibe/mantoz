#!/bin/sh
# Верификатор smoke-choice: судит только по диску.
# Отсутствие файла - провал (reward 0), а не крах прогона.
# Сравнение строгое, побайтовое: $(cat ...) съедает хвостовые переводы строк
# и пропускал бы лишнюю пустую строку, а instruction требует ровно одну.
mkdir -p /logs/verifier
if [ -f /app/answer.txt ] && printf 'yes\n' | cmp -s - /app/answer.txt; then
  echo 1 > /logs/verifier/reward.txt
else
  echo 0 > /logs/verifier/reward.txt
fi
