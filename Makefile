.PHONY: dev test lint format docker-up docker-down

dev:
	uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

test:
	pytest -v

lint:
	ruff check app/ tests/

format:
	ruff format app/ tests/

docker-up:
	docker-compose up --build

docker-down:
	docker-compose down
