FROM python:3.12-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    UV_PYTHON_DOWNLOADS=never

WORKDIR /app

# We copy .toml and not uv.lock because has librairy personnalized for my computer
COPY pyproject.toml ./
RUN uv sync --no-dev --no-editable --no-install-project

FROM python:3.12-slim AS runtime

RUN apt-get update && apt-get install -y --no-install-recommends libmagic1 gosu && rm -rf /var/lib/apt/lists/*

COPY --from=builder --chown=root:root /app/.venv /app/.venv

WORKDIR /app

COPY src ./src

COPY docker/entrypoint.sh /entrypoint.sh

RUN useradd -m -u 1000 appuser \
    && mkdir -p /app/storage/uploads \
    && chmod -R o=rx /app \
    && chmod +x /entrypoint.sh

EXPOSE 8000

ENV PYTHONPATH=/app/.venv/lib/python3.12/site-packages

ENTRYPOINT ["/entrypoint.sh"]

CMD ["python", "-m", "uvicorn", "src.back.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
