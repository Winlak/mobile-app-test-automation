.DEFAULT_GOAL := help

.PHONY: help install lint typecheck check build-sut appium-setup test-smoke test-regression test-e2e allure

help:
	@echo "install         установить Python-зависимости"
	@echo "lint            запустить ruff"
	@echo "typecheck       запустить mypy"
	@echo "check           запустить статические проверки"
	@echo "build-sut       собрать локальное Android-приложение"
	@echo "appium-setup    установить UiAutomator2 для Appium 2"
	@echo "test-smoke      выполнить smoke-набор"
	@echo "test-regression выполнить регрессионный набор"
	@echo "test-e2e        выполнить сквозной сценарий"
	@echo "allure          открыть локальный Allure-отчёт"

install:
	python3.12 -m pip install --upgrade pip
	python3.12 -m pip install -e '.[dev]'

lint:
	ruff check conftest.py src tests
	ruff format --check conftest.py src tests

typecheck:
	mypy

check: lint typecheck

build-sut:
	cd sut && ./gradlew :app:assembleDebug

appium-setup:
	appium driver install uiautomator2

test-smoke:
	pytest -m smoke --alluredir=allure-results

test-regression:
	pytest -m 'regression and not e2e' --alluredir=allure-results

test-e2e:
	pytest -m e2e --alluredir=allure-results

allure:
	allure serve allure-results
