FROM python:3.13-alpine
# ponytail: POSIX scripts only; install bash if task commands need bash syntax.
RUN printf '#!/bin/sh\nexec /bin/sh "$@"\n' > /bin/bash && chmod +x /bin/bash
WORKDIR /app
COPY scenario.json operator_replies.json /app/
