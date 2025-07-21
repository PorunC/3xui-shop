FROM python:3.12-slim-bullseye

ENV PYTHONPATH=/

# Install system dependencies for localization
RUN apt-get update && apt-get install -y gettext && rm -rf /var/lib/apt/lists/*

# Copy dependency files
COPY pyproject.toml poetry.lock* /

# Install Poetry and dependencies
RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --only main

# Copy application code
COPY ./app /app

# Compile language files during build
WORKDIR /
RUN poetry run pybabel compile -d /app/locales -D bot || echo "Warning: Language compilation failed during build"