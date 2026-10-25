.PHONY: install run test lint format typecheck eval docker-up docker-down

install:
	cd backend && pip install -e ".[dev]"

run:
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:
	cd backend && pytest

lint:
	cd backend && ruff check .

format:
	cd backend && ruff format .

typecheck:
	cd backend && mypy app

eval:
	@echo "Eval suite not implemented yet"

docker-up:
	docker-compose up --build

docker-down:
	docker-compose down
