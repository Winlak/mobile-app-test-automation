from __future__ import annotations

from decimal import Decimal

import allure
import pytest
from appium.webdriver.webdriver import WebDriver

from expense_automation.config import Settings
from expense_automation.data import new_expense
from expense_automation.pages.expense_form import expense_with
from expense_automation.pages.expenses import ExpensesScreen
from expense_automation.pages.login import LoginScreen


@allure.epic("Учёт расходов")
@allure.feature("Сквозной пользовательский путь")
@pytest.mark.e2e
@pytest.mark.regression
class TestExpenseJourney:
    @allure.title("Пользователь ведёт расход от входа до удаления и выхода")
    def test_expense_lifecycle(self, driver: WebDriver, settings: Settings) -> None:
        initial = new_expense(category="Продукты", amount=Decimal("99.90"))
        updated = expense_with(f"{initial.title} после правки", "120.00", "Транспорт")

        login = LoginScreen(driver, settings.explicit_timeout).wait_until_opened()
        login.login(settings.test_user.email, settings.test_user.password)
        expenses = ExpensesScreen(driver, settings.explicit_timeout).wait_until_opened()

        expenses = expenses.add_expense().save(initial)
        expenses.assert_expense_visible(initial)
        expenses.filter_by("Продукты").assert_expense_visible(initial)

        expenses = expenses.open_expense(initial.title).save(updated)
        expenses.filter_by("Все категории").assert_expense_visible(updated)

        expenses.open_expense(updated.title).delete()
        expenses.wait_until_opened().assert_empty()
        expenses.logout()
        LoginScreen(driver, settings.explicit_timeout).wait_until_opened()
