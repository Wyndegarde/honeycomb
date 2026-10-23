# honeycomb

A project created with FastAPI CLI.

## Quick Start

### Start the development server

```bash
uv run fastapi dev
```

Visit http://localhost:8000

### Run the tests

```bash
uv run pytest
```

Requires only a running Docker daemon. The suite starts its own throwaway Postgres container, so `make run-db-container` and `.env` are not needed.

### Deploy to FastAPI Cloud

Sign up and log in at https://fastapicloud.com, then deploy with:

```bash
uv run fastapi deploy
```

## Project Structure

- `app/main.py` - FastAPI application
- `app/routes/` - API routers (`media`, `reviews`, `health`)
- `app/schemas/` - Pydantic request/response models
- `app/db/models/` - SQLAlchemy models; `app/db/repositories/` - data access
- `app/db/migrations/` - Alembic migrations (`make run-migration` to apply)
- `pyproject.toml` - Project dependencies

## API

A review belongs to a media item (book, film, TV show, ...). There is one review per item.

- `/media` - create, list (`?q=`, `?type=`, `?limit=`, `?offset=`), get, update, delete
- `/media/{id}/review` - `PUT` creates or replaces, plus `GET` and `DELETE`

The old `/reviews` endpoints were removed when reviews were split from media.

## Learn More

- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [FastAPI Cloud](https://fastapicloud.com)
