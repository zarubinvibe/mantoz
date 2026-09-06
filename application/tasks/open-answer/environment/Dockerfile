FROM python:3.13-alpine
# ponytail: POSIX verifier only; replace shim with bash package if scripts need Bash syntax.
RUN printf '#!/bin/sh\nexec /bin/sh "$@"\n' > /bin/bash && chmod +x /bin/bash
WORKDIR /app
