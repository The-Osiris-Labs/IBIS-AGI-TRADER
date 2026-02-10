.PHONY: help install dev-install test lint format clean run paper-run docker-build docker-run

help:
	@echo "🦅 IBIS Development Commands"
	@echo "=============================="
	@echo ""
	@echo "Setup:"
	@echo "  make install         Install production dependencies"
	@echo "  make dev-install     Install development dependencies"
	@echo ""
	@echo "Running:"
	@echo "  make run            Run IBIS in live trading mode"
	@echo "  make paper-run      Run IBIS in paper trading mode"
	@echo "  make test-once      Run a single scan test"
	@echo ""
	@echo "Development:"
	@echo "  make test           Run test suite"
	@echo "  make lint           Check code quality"
	@echo "  make format         Format code (black)"
	@echo "  make type-check     Type checking (mypy)"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean          Remove build artifacts and caches"
	@echo "  make logs           View recent IBIS logs"
	@echo "  make status         Check if IBIS is running"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build   Build Docker image"
	@echo "  make docker-run     Run IBIS in Docker"
	@echo ""

install:
	pip install -r requirements.txt

dev-install:
	pip install -r requirements.txt
	pip install -e ".[dev]"

run:
	python3 ibis_true_agent.py

paper-run:
	PAPER_TRADING=true python3 ibis_true_agent.py

test-once:
	python3 ibis_true_agent.py --scan-once

test:
	pytest tests/ -v

lint:
	ruff check ibis_true_agent.py ibis/

format:
	black ibis_true_agent.py ibis/

type-check:
	mypy ibis_true_agent.py ibis/ || true

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf build/ dist/ *.egg-info
	rm -rf .mypy_cache/ .pytest_cache/ .ruff_cache/
	rm -rf htmlcov .coverage

logs:
	tail -100 data/ibis_true.log

logs-follow:
	tail -f data/ibis_true.log

status:
	@if pgrep -f "ibis_true_agent.py" > /dev/null; then \
		echo "✅ IBIS is running"; \
		pgrep -f "ibis_true_agent.py"; \
	else \
		echo "❌ IBIS is not running"; \
	fi

docker-build:
	docker build -t ibis-trader .

docker-run:
	docker run -d \
		--name ibis \
		-v $(PWD)/data:/app/data \
		-v $(PWD)/ibis/keys.env:/app/ibis/keys.env:ro \
		ibis-trader

docker-logs:
	docker logs -f ibis

docker-stop:
	docker stop ibis
	docker rm ibis

.DEFAULT_GOAL := help
