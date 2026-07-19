"""Root Pytest lifecycle, state reset and post-failure diagnostics."""

from __future__ import annotations

from collections.abc import Generator
from pathlib import Path
from typing import Any

import pytest
from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.webdriver import WebDriver

from expense_automation.config import Settings, load_settings
from expense_automation.pages.expenses import ExpensesScreen
from expense_automation.pages.login import LoginScreen
from expense_automation.utils.diagnostics import capture_failure_artifacts


def pytest_addoption(parser: pytest.Parser) -> None:
    group = parser.getgroup("android")
    group.addoption("--config", default="config/devices.yaml", help="Путь к YAML-конфигурации")
    group.addoption("--device", default="emulator", help="Имя профиля устройства из YAML")
    group.addoption("--device-name", default=None, help="Отображаемое имя Android-устройства")
    group.addoption("--android-version", default=None, help="Версия Android/API для capability")
    group.addoption("--udid", default=None, help="Serial реального устройства или эмулятора")
    group.addoption("--appium-url", default=None, help="URL сервера Appium 2")
    group.addoption("--apk", default=None, help="Путь к APK вместо app_path из конфигурации")
    group.addoption("--explicit-timeout", type=int, default=None, help="Таймаут явных ожиданий")
    group.addoption(
        "--new-command-timeout", type=int, default=None, help="Appium newCommandTimeout в секундах"
    )
    group.addoption(
        "--keep-app-data",
        action="store_true",
        default=False,
        help="Не очищать состояние приложения: только для локальной отладки",
    )


@pytest.fixture(scope="session")
def settings(pytestconfig: pytest.Config) -> Settings:
    return load_settings(
        Path(str(pytestconfig.getoption("config"))).resolve(),
        str(pytestconfig.getoption("device")),
        appium_url=pytestconfig.getoption("appium_url"),
        apk=pytestconfig.getoption("apk"),
        device_name=pytestconfig.getoption("device_name"),
        platform_version=pytestconfig.getoption("android_version"),
        udid=pytestconfig.getoption("udid"),
        explicit_timeout=pytestconfig.getoption("explicit_timeout"),
        new_command_timeout=pytestconfig.getoption("new_command_timeout"),
        keep_app_data=bool(pytestconfig.getoption("keep_app_data")),
    )


@pytest.fixture(scope="session")
def driver(settings: Settings) -> Generator[WebDriver, None, None]:
    """Create exactly one Appium session; individual tests reset its app data."""

    if not settings.app_path.is_file():
        raise FileNotFoundError(
            f"APK не найден: {settings.app_path}. "
            "Сначала выполните make build-sut или передайте --apk."
        )
    options = UiAutomator2Options().load_capabilities(settings.capabilities)
    mobile_driver = webdriver.Remote(command_executor=settings.appium_url, options=options)
    yield mobile_driver
    mobile_driver.quit()


@pytest.fixture(autouse=True)
def reset_application(driver: WebDriver, settings: Settings) -> Generator[None, None, None]:
    """Give every test isolated storage and a predictable initial login screen."""

    if not settings.keep_app_data:
        driver.terminate_app(settings.app_package)
        driver.execute_script("mobile: clearApp", {"appId": settings.app_package})
        driver.activate_app(settings.app_package)
    yield


@pytest.fixture
def authenticated_driver(driver: WebDriver, settings: Settings) -> WebDriver:
    """Log in through the UI, preserving the same behavior as a user."""

    login = LoginScreen(driver, settings.explicit_timeout).wait_until_opened()
    login.login(settings.test_user.email, settings.test_user.password)
    ExpensesScreen(driver, settings.explicit_timeout).wait_until_opened()
    return driver


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(
    item: pytest.Item, call: pytest.CallInfo[Any]
) -> Generator[None, None, None]:
    """Attach evidence while the driver is still alive, before fixture teardown."""

    outcome = yield
    report = outcome.get_result()
    if report.when not in {"setup", "call"} or not report.failed:
        return
    active_driver = item.funcargs.get("driver")
    active_settings = item.funcargs.get("settings")
    if isinstance(active_driver, WebDriver) and isinstance(active_settings, Settings):
        capture_failure_artifacts(active_driver, active_settings, item.nodeid)
