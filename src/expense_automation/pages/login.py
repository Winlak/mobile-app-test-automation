"""Login screen object."""

from __future__ import annotations

import allure

from expense_automation.pages.base import BaseScreen


class LoginScreen(BaseScreen):
    """Models the deterministic login screen of the demo application."""

    SCREEN = ("accessibility id", "login-screen")
    EMAIL = ("accessibility id", "login-email")
    PASSWORD = ("accessibility id", "login-password")
    SUBMIT = ("accessibility id", "login-submit")
    ERROR = ("accessibility id", "login-error")

    def wait_until_opened(self) -> LoginScreen:
        self.element(self.SCREEN)
        return self

    @allure.step("Войти в приложение")
    def login(self, email: str, password: str) -> None:
        self.fill(self.EMAIL, email)
        self.fill(self.PASSWORD, password)
        self.tap(self.SUBMIT)

    def error_message(self) -> str:
        return self.text(self.ERROR)
