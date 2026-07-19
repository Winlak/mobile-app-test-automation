from __future__ import annotations

from decimal import Decimal

import allure
import pytest
from appium.webdriver.webdriver import WebDriver

from expense_automation.components.app_lifecycle import AppLifecycle
from expense_automation.config import Settings
from expense_automation.data import new_expense
from expense_automation.pages.expense_form import expense_with
from expense_automation.pages.expenses import ExpensesScreen


@allure.epic("Учёт расходов")
@allure.feature("Расходы")
@pytest.mark.regression
class TestExpenses:
    @allure.title("Добавленный расход отображается с суммой и категорией")
    @pytest.mark.smoke
    def test_add_expense(self, authenticated_driver: WebDriver, settings: Settings) -> None:
        expense = new_expense()
        expenses = ExpensesScreen(
            authenticated_driver, settings.explicit_timeout
        ).wait_until_opened()

        expenses = expenses.add_expense().save(expense)

        expenses.assert_expense_visible(expense)

    @allure.title("Пользователь редактирует существующий расход")
    def test_edit_expense(self, authenticated_driver: WebDriver, settings: Settings) -> None:
        initial = new_expense(category="Продукты", amount=Decimal("100.00"))
        updated = expense_with(f"{initial.title} обновлён", "245.50", "Здоровье")
        expenses = ExpensesScreen(
            authenticated_driver, settings.explicit_timeout
        ).wait_until_opened()
        expenses = expenses.add_expense().save(initial)

        expenses = expenses.open_expense(initial.title).save(updated)

        expenses.assert_expense_visible(updated)
        expenses.assert_expense_hidden(initial.title)

    @allure.title("Пользователь удаляет расход после подтверждения")
    def test_delete_expense(self, authenticated_driver: WebDriver, settings: Settings) -> None:
        expense = new_expense()
        expenses = ExpensesScreen(
            authenticated_driver, settings.explicit_timeout
        ).wait_until_opened()
        expenses = expenses.add_expense().save(expense)

        expenses.open_expense(expense.title).delete()
        expenses.wait_until_opened().assert_expense_hidden(expense.title)
        expenses.assert_empty()

    @allure.title("Фильтр категории скрывает расходы из других категорий")
    def test_filter_by_category(self, authenticated_driver: WebDriver, settings: Settings) -> None:
        groceries = new_expense(category="Продукты")
        transport = new_expense(category="Транспорт")
        expenses = ExpensesScreen(
            authenticated_driver, settings.explicit_timeout
        ).wait_until_opened()
        expenses = expenses.add_expense().save(groceries)
        expenses = expenses.add_expense().save(transport)

        expenses.filter_by("Продукты")

        expenses.assert_expense_visible(groceries)
        expenses.assert_expense_hidden(transport.title)

    @allure.title("Пустые обязательные поля показывают понятную ошибку")
    def test_required_fields_validation(
        self, authenticated_driver: WebDriver, settings: Settings
    ) -> None:
        expenses = ExpensesScreen(
            authenticated_driver, settings.explicit_timeout
        ).wait_until_opened()
        form = expenses.add_expense()

        form.submit_raw("", "")

        assert form.error_message() == "Заполните название и сумму"

    @allure.title("Неположительные и нечисловые суммы не сохраняются")
    @pytest.mark.parametrize("amount", ["0", "-50", "не число"])
    def test_invalid_money_validation(
        self, authenticated_driver: WebDriver, settings: Settings, amount: str
    ) -> None:
        expenses = ExpensesScreen(
            authenticated_driver, settings.explicit_timeout
        ).wait_until_opened()
        form = expenses.add_expense()

        form.submit_raw("Проверка суммы", amount)

        assert form.error_message() == "Укажите сумму больше нуля"

    @allure.title("Расход и сессия сохраняются после перезапуска приложения")
    def test_state_is_persisted_after_restart(
        self, authenticated_driver: WebDriver, settings: Settings
    ) -> None:
        expense = new_expense()
        expenses = ExpensesScreen(
            authenticated_driver, settings.explicit_timeout
        ).wait_until_opened()
        expenses = expenses.add_expense().save(expense)

        AppLifecycle(authenticated_driver, settings.explicit_timeout, settings).restart()
        expenses.wait_until_opened().assert_expense_visible(expense)
