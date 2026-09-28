.PHONY: install install-dev install-global db-up db-init db-down db-reset run clean

install:
	@echo "Installing..."
	pip install .

install-dev:
	@echo "Installing in developer mode..."
	pip install -e .

install-global: install
	@echo "Creating symlink in /usr/local/bin for global access..."
	sudo ln -sf $$(which cmatch) /usr/local/bin/cmatch
	@echo "Done! You can use 'cmatch' from any path."

db-up:
	@echo "Starting PostgreSQL..."
	docker compose up -d postgres

db-init:
	@echo "Starting PostgreSQL..."
	docker compose up -d postgres
	@echo "Waiting for PostgreSQL..."
	@until docker exec postgres-dev pg_isready -U postgres >/dev/null 2>&1; do sleep 1; done
	@echo "Importing dump.sql..."
	docker exec -i postgres-dev psql -U postgres -d postgres < dump.sql
	@echo "Database initialized."

db-down:
	@echo "Stopping PostgreSQL..."
	docker compose down

db-reset:
	@echo "Removing PostgreSQL and its data..."
	docker compose down -v

run:
	@echo "Running CMATCH..."
	cmatch

clean:
	@echo "Cleaning temporary files..."
	rm -rf build/ dist/ *.egg-info/ __pycache__/ cmatch/__pycache__
