.PHONY: install run test lint format build build-dev up down

install:
	pip install -r requirements-dev.txt

run:
	uvicorn main:app --reload --port 8000

test:
	pytest

lint:
	ruff check .

format:
	ruff format .

build:
	docker build -t flow-manager .

build-dev:
	docker build --target dev -t flow-manager-dev .

up:
	docker run --rm -p 8000:8000 flow-manager

dev:
	docker run --rm -it -v $(PWD):/app flow-manager-dev
