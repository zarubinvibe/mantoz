FROM mcr.microsoft.com/playwright/python:v1.49.1-noble
# Образ на Ubuntu - bash уже есть (Harbor оборачивает команды в bash).
# В образе браузеры (/ms-playwright), но нет pip-пакета - ставим ровно ту
# версию, под которую собраны браузеры образа.
RUN pip install --no-cache-dir playwright==1.49.1
WORKDIR /app
COPY stand.html run_scenario.py /app/
