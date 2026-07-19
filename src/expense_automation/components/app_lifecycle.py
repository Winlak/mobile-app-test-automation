"""Explicit app lifecycle actions used by persistence checks."""

from __future__ import annotations

import allure
from appium.webdriver.webdriver import WebDriver

from expense_automation.config import Settings
from expense_automation.pages.base import BaseScreen


class AppLifecycle(BaseScreen):
    """Keeps process-level Android actions out of business tests."""

    def __init__(self, driver: WebDriver, timeout: int, settings: Settings) -> None:
        super().__init__(driver, timeout)
        self.settings = settings

    @allure.step("Перезапустить приложение")
    def restart(self) -> None:
        self.driver.terminate_app(self.settings.app_package)
        self.driver.activate_app(self.settings.app_package)
