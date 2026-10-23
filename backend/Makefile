
include .env
run-db-container:
	docker compose up -d --wait db
	
run-migration:
	uv run alembic -c ./app/db/alembic.ini upgrade head

remove-db-container:
	docker compose down --rmi all -v

update-migration:
	$(MAKE) run-db-container
	$(MAKE) run-migration
	uv run alembic -c ./app/db/alembic.ini revision --autogenerate -m "$(message)"
	$(MAKE) remove-db-container

stop-db:
	docker compose down

reset-db:
	docker compose down -v
	docker compose up -d --wait db

db-logs:
	docker compose logs -f db

check:
	uv run ruff check
	uv run ruff format --check
	uv run pyright
	uv run pytest

db-shell:
	docker compose exec db psql -U $(DB_USERNAME) -d $(DB_NAME)
.PHONY: run-db-container run-migration remove-db-container update-migration stop-db reset-db db-logs db-shell check

