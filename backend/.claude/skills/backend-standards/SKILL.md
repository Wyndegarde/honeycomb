---
name: backend-standards
description: Coding standards for the honeycomb backend (FastAPI, async SQLAlchemy, Alembic, pytest). Use for any implementation, refactor, bug fix, test or migration work under backend/, and check the "Done" list before declaring work finished.
---

# Backend standards

Follow these for every change. Match the surrounding code first; if a rule here and the code disagree, follow the rule and say so.

## Layering

- `routes/` (thin async handlers) → `db/repositories/` (queries) → `db/models/`. No services layer; don't add one.
- Repositories only `flush`/`refresh`. Routes own `await repo.db.commit()`.
- New repository: add `get_x_repo` and an `XRepoDep` alias in `routes/deps.py`. Routers use `APIRouter(prefix=..., tags=[...])` and are registered in `routes/__init__.py`.
- Concurrency-sensitive writes happen in one SQL statement (`INSERT ... ON CONFLICT ... RETURNING`, see `ReviewRepository.upsert`), never read-then-write.
- Routes call repositories, not `repo.db` directly, except for `commit`.

## Schemas

- One file per resource: `NewX` (create), `UpdateX` (all optional, applied with `model_dump(exclude_unset=True)`, null-rejecting validator for NOT NULL columns), `XRead` (`from_attributes=True`).
- Every string field has `Field` length limits.

## Models

- Inherit `Base` (timestamps) or `BaseNoDate` (join tables).
- `Mapped[...] = mapped_column(...)` with an explicit `nullable=`. `Text`, not `String`.
- Every FK sets `ondelete`. Enums are `StrEnum` with `values_callable`.
- Re-export every new model in `models/__init__.py`, or autogenerate and `create_all` miss it.

## Python style

- Python 3.13 syntax: `X | None`, `list[...]`, PEP 695 generics.
- Everything touching the DB is `async`. Dependencies use `Annotated` aliases, never `Depends()` as a default.
- Handlers set `response_model=` and `status_code=`; no return annotations, no docstrings.
- Comments say why, never what. Imports: stdlib, third-party, `app.*`.
- `# type: ignore` needs a reason.

## Errors

- Missing resource: `HTTPException(status.HTTP_404_NOT_FOUND, "<Resource> not found")`.
- Use one shared `get_<x>_or_404` helper in `routes/deps.py`; don't repeat the check inline.
- No bare `except`, no swallowed exceptions. Use `logging`, never `print`.

## Migrations

- Generate with `make update-migration message="..."`. Always give a message. Review the output; never hand-write a schema diff.
- Write a full `downgrade()` in reverse order, dropping enums explicitly. Backfills use raw `op.execute`. Use `op.f()` names.
- A downgrade that destroys data must say so in its docstring.
- Any model change ships its migration in the same change.

## Tests

- Black-box HTTP tests with the `client` fixture over real Postgres (testcontainers). Each test rolls back; `asyncio_mode=auto`, so no markers. The one exception is `tests/test_migrations.py`, which runs Alembic against an empty database.
- Every endpoint gets: happy path, 404, 422 invalid body, invalid path ID.
- Reuse helpers such as `create_media`; don't rewrite them.
- Bug fixes start with a failing test that reproduces the bug.

## Security and data

- Parameterised SQL only. Never interpolate user input into SQL. Keep the LIKE-wildcard escaping in `MediaRepository.search`.
- No secrets and no `.env` in commits.
- Validate at the request boundary (schemas), not again deeper in.
- Every list endpoint has a bounded `limit`, an `offset` and an explicit `order_by` (see `list_media`).

## Dependencies

- Justify any new dependency in the change description. Add it with `uv add` and commit `uv.lock`. Don't add one for a few lines of code.

## Workflow

- Read `GLOSSARY.md` and `docs/adr/` first if they exist, and use their terms.
- Issues are `.scratch/<feature>/` markdown; see `docs/agents/issue-tracker.md`.
- Commits are small, one concern each. Don't commit or push unless asked.
- Keep the diff to what was asked.

## Done

Do not report work as finished until all of these hold:

1. `uv run pytest` passes (needs Docker). This includes `tests/test_migrations.py`, which fails if a model change has no migration or a downgrade breaks.
2. `uv run ruff check`, `uv run ruff format --check` and `uv run pyright` are clean.
3. `make check` runs all of the above in one go.
4. The README API section is updated if endpoints changed.
5. Say plainly which checks you ran and which you could not.
