Status: resolved

## Problem Statement

To run Honeycomb I currently have to start Postgres from the backend compose file, apply Alembic migrations by hand, run the FastAPI server through uv, and run the frontend dev server separately. There is no single command to bring up the whole app, and the backend has no container image.

## Solution

One `docker compose up --build` from the repo root starts the whole app: Postgres, the backend (migrated automatically) and the frontend. I open `http://localhost:8080` and it works from an empty database. Backend-only development with the existing `backend/docker-compose.yml` and Makefile keeps working unchanged.

## User Stories

1. As a developer, I want to run the full app with one `docker compose up --build` from the repo root, so that I don't have to start three things by hand.
2. As a developer, I want the app to work from an empty database volume, so that a fresh clone is usable immediately.
3. As a developer, I want migrations applied automatically when the backend container starts, so that I never forget `make run-migration`.
4. As a developer, I want the migration step to be a no-op when the schema is already current, so that restarting the stack is safe.
5. As a developer, I want a pending migration applied to an already-populated volume on restart, so that upgrading doesn't need a volume reset.
6. As a developer, I want the backend to start only after Postgres is healthy, so that startup doesn't race the database.
7. As a developer, I want database data to persist in a named volume across `docker compose down`/`up`, so that my library isn't lost.
8. As a developer, I want only the frontend published on host port 8080, so that the backend and database aren't exposed unnecessarily.
9. As a user, I want to open `http://localhost:8080` and see the Library page, so that I can use the app.
10. As a user, I want API calls from the browser to go through `/api/` on the same origin, so that no CORS setup is needed.
11. As a user, I want to create media, links and reviews and have them persist, so that the containerised app is fully functional.
12. As a developer, I want the backend image built with uv from `pyproject.toml` and `uv.lock`, so that installs are reproducible and match local dev.
13. As a developer, I want dev dependencies excluded from the backend image, so that it stays small.
14. As a developer, I want dependency layers cached separately from source, so that code-only rebuilds are fast.
15. As a developer, I want the backend to run as a non-root user, so that the container is safer.
16. As a developer, I want `backend/` and `frontend/` each to build with their own folder as the Docker context, so that each is self-contained.
17. As a developer, I want `.dockerignore` files that exclude `.venv`, `node_modules`, caches, build output and `.env`, so that local junk and secrets don't enter images.
18. As a developer, I want configuration read from a root `.env`, with a committed `.env.example`, so that I know which variables to set without committing secrets.
19. As a developer, I want the backend's `DB_HOST` set to the compose `db` service inside the stack, so that my local `localhost` value in `backend/.env` doesn't break the container.
20. As a developer, I want `backend/docker-compose.yml` and the Makefile left alone, so that I can still develop the backend in isolation against a local DB.
21. As a developer, I want the stock `postgres:18` image used, so that I don't maintain a custom DB image.
22. As a developer, I want a healthcheck on the database, so that dependent services wait for readiness.
23. As a developer, I want the existing frontend Dockerfile (node build, nginx serve, `/api/` proxy) kept, so that the frontend is unchanged.
24. As a developer, I want the root compose to be the only thing needed to run the app, so that onboarding is one command.

## Implementation Decisions

- New root compose file defining three services: `db`, `backend`, `frontend`. The existing backend compose file and Makefile are untouched.
- `db`: stock `postgres:18` image; credentials and database name from the root `.env` (`DB_USERNAME`, `DB_PASSWORD`, `DB_NAME`); named volume for data; `pg_isready` healthcheck; port not published to the host.
- `backend`: new Dockerfile using the uv binary (copied from the official uv image) on a `python:3.13-slim` base, matching `requires-python >= 3.13`. Install with a frozen lockfile and no dev group. Copy dependency manifests before source for layer caching. Run as a non-root user. Build context is the backend folder.
- Backend startup command runs the Alembic upgrade to `head` and then starts the FastAPI server on port 8000. Upgrade to head is idempotent: it initialises an empty DB, applies pending revisions to an existing one, and does nothing if current.
- `backend` depends on `db` with `condition: service_healthy`. Its environment sets `DB_HOST=db` and the other `DB_*` values from the root `.env`. The Alembic config used by the Makefile must resolve inside the container using the same settings the app uses.
- `frontend`: existing Dockerfile reused unchanged (SPA build served by nginx, `/api/` proxied to `API_URL`, default `http://backend:8000`). Build context is the frontend folder. Published as `8080:80`. Depends on `backend`.
- Root `.env` (gitignored) and committed `.env.example` listing the `DB_*` variables.
- Backend gets a `.dockerignore` excluding virtualenv, caches, `.env`, tests, and docs.
- The backend container's health route (`/health`) is reachable via `/api/health` through nginx, used for verification.

## Testing Decisions

- A good test exercises only external behaviour of the running stack, not Dockerfile or compose internals.
- One seam: the running stack via `docker compose up --build` from the repo root on an empty volume. Verify: `GET :8080/` serves the SPA; `GET :8080/api/health` returns 200; creating a media record through `/api/` and reading it back succeeds (proves migrations ran); a second `up` on the populated volume starts cleanly (idempotent migration).
- This is a manual or scripted smoke check; no new unit tests, as no application code changes.
- Prior art: the existing backend pytest suite with testcontainers is unchanged and remains the test for application behaviour.

## Out of Scope

- Production deployment, TLS, reverse proxy hardening, image publishing or CI.
- Hot-reload / dev-mode containers for either service.
- Changing application code, schema or the frontend build.
- Replacing the backend's isolated dev compose file or Makefile targets.
- Backups or Postgres tuning (the dev compose's `log_statement=all` is not carried over).

## Further Notes

- `backend/.env` has `DB_HOST=localhost` for local dev; the compose environment must override it rather than reuse that file in the container.
- Postgres 18 stores data under a versioned directory; the volume mount should follow the same path as the existing dev compose (`/var/lib/postgresql`).
