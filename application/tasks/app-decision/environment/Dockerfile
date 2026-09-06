FROM ubuntu:24.04

# computer-use runtime: Harbor computer-1 так же работает через Xvfb,
# xdotool и screenshots. Ubuntu уже содержит bash для обёртки Harbor.
# ponytail: XFCE/VNC не нужны для автопрогона; добавить для live-view.
RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        fonts-dejavu-core python3 python3-tk scrot xauth xdotool xvfb \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY desktop_app.py run_scenario.py /app/
