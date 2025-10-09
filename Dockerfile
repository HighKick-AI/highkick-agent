# Base with Python 3.13
FROM python:3.13-slim

# Install latest JDK available for this distro and make
RUN apt-get update && \
    apt-get install -y --no-install-recommends default-jdk make && \
    rm -rf /var/lib/apt/lists/*

# Ensure pip stays modern
RUN python -m pip install --upgrade pip


# --- Begin: auxiliary venv (separate from the main app env) ---
# Create an isolated venv; don't modify PATH.
ENV AUX_VENV=/opt/aux-venv

# Create the virtual environment and upgrade pip
RUN python -m venv $AUX_VENV && \
    $AUX_VENV/bin/pip install --no-cache-dir --upgrade pip

# Install packages one by one to leverage Docker layer caching
RUN $AUX_VENV/bin/pip install --no-cache-dir "pyspark==4.0.0"
RUN $AUX_VENV/bin/pip install --no-cache-dir "psycopg[binary]"
RUN $AUX_VENV/bin/pip install --no-cache-dir "psycopg2-binary"
RUN $AUX_VENV/bin/pip install --no-cache-dir "PyMySQL"

# (Optional) Helper script to enter this venv when you shell in
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
