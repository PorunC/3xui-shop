FROM python:3.12-slim-bullseye

ENV PYTHONPATH=/

# Install system dependencies for localization
RUN apt-get update && apt-get install -y gettext && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml /
RUN pip install poetry && poetry install

COPY ./app /app

# Compile language files during build
WORKDIR /
RUN poetry run pybabel compile -d /app/locales -D bot || echo "Warning: Language compilation failed during build"