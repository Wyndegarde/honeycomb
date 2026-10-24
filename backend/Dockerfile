FROM python:3.13-slim
COPY --from=ghcr.io/astral-sh/uv:0.12.23 /uv /usr/local/bin/uv

ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy PATH="/app/.venv/bin:$PATH"
WORKDIR /app

# deps first so code-only changes reuse this layer
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

COPY app ./app
RUN useradd --system app
USER app

EXPOSE 8000
# upgrade head is a no-op when the schema is current
CMD ["sh", "-c", "alembic -c app/db/alembic.ini upgrade head && fastapi run app/main.py --port 8000"]
