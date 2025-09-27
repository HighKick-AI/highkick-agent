# Base with Python 3.13
FROM python:3.13-slim

# Install latest JDK available for this distro and make
RUN apt-get update && \
    apt-get install -y --no-install-recommends default-jdk make && \
    rm -rf /var/lib/apt/lists/*

# Ensure pip stays modern
RUN python -m pip install --upgrade pip


# --- Begin: auxiliary venv (separate from the main app env) ---
# Create an isolated venv just for PySpark & Postgres driver; don't modify PATH.
ENV AUX_VENV=/opt/aux-venv
RUN python -m venv $AUX_VENV && \
    $AUX_VENV/bin/pip install --no-cache-dir --upgrade pip && \
    # PySpark needs a JDK (installed above). Install Postgres driver in this venv too.
    $AUX_VENV/bin/pip install --no-cache-dir "pyspark==4.0.0" "psycopg[binary]" "psycopg2-binary"
# (Optional) leave a helper to enter this venv when you shell in:
# RUN printf '#!/bin/sh\n. $AUX_VENV/bin/activate\nexec "$@"\n' > /usr/local/bin/aux-venv && chmod +x /usr/local/bin/aux-venv
# --- End: auxiliary venv ---


# Install Poetry globally
RUN pip install "poetry>=1.8.0"

WORKDIR /app

# Copy only dependency files first
COPY pyproject.toml poetry.lock* /app/

# Install dependencies (no project install yet)
RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi --no-root

COPY . /app

RUN mkdir -p /spark-data

CMD ["make", "run-python"]
