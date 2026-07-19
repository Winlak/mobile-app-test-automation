from __future__ import annotations

import allure
import pytest
from appium.webdriver.webdriver import WebDriver

from expense_automation.config import Settings
from expense_automation.pages.expenses import ExpensesScreen
from expense_automation.pages.login import LoginScreen


@allure.epic("Учёт расходов")
@allure.feature("Авторизация")
@pytest.mark.auth
class TestAuthentication:
    @allure.title("Пользователь с корректными данными открывает список расходов")
    @pytest.mark.smoke
    @pytest.mark.regression
    def test_successful_login(self, driver: WebDriver, settings: Settings) -> None:
        LoginScreen(driver, settings.explicit_timeout).wait_until_opened().login(
            settings.test_user.email, settings.test_user.password
        )

        ExpensesScreen(driver, settings.explicit_timeout).wait_until_opened()

    @allure.title("Некорректный пароль не создаёт сессию")
    @pytest.mark.regression
    def test_unsuccessful_login(self, driver: WebDriver, settings: Settings) -> None:
        login = LoginScreen(driver, settings.explicit_timeout).wait_until_opened()
        login.login(settings.test_user.email, "not-the-demo-password")

        assert login.error_message() == "Неверный e-mail или пароль"

    @allure.title("Logout возвращает пользователя на экран входа")
    @pytest.mark.smoke
    @pytest.mark.regression
    def test_logout(self, authenticated_driver: WebDriver, settings: Settings) -> None:
        expenses = ExpensesScreen(
            authenticated_driver, settings.explicit_timeout
        ).wait_until_opened()
        expenses.logout()

        LoginScreen(authenticated_driver, settings.explicit_timeout).wait_until_opened()
