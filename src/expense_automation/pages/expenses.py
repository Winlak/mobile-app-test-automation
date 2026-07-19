"""Expense list screen object."""

from __future__ import annotations

from typing import TYPE_CHECKING

import allure
from selenium.webdriver.support import expected_conditions as conditions

from expense_automation.components.category_picker import CategoryPicker
from expense_automation.models import Expense
from expense_automation.pages.base import BaseScreen, by_text

if TYPE_CHECKING:
    from expense_automation.pages.expense_form import ExpenseFormScreen


class ExpensesScreen(BaseScreen):
    """Models list, filtering and session actions without leaking locators to tests."""

    SCREEN = ("accessibility id", "expenses-screen")
    ADD = ("accessibility id", "expense-add")
    FILTER = ("accessibility id", "filter-open")
    LOGOUT = ("accessibility id", "logout")
    EMPTY_STATE = ("accessibility id", "expenses-empty")

    def wait_until_opened(self) -> ExpensesScreen:
        self.element(self.SCREEN)
        return self

    @allure.step("Открыть форму добавления расхода")
    def add_expense(self) -> ExpenseFormScreen:
        from expense_automation.pages.expense_form import ExpenseFormScreen

        self.tap(self.ADD)
        return ExpenseFormScreen(self.driver, self.timeout).wait_until_opened()

    @allure.step("Открыть расход «{title}»")
    def open_expense(self, title: str) -> ExpenseFormScreen:
        from expense_automation.pages.expense_form import ExpenseFormScreen

        self.tap(by_text(title))
        return ExpenseFormScreen(self.driver, self.timeout).wait_until_opened()

    @allure.step("Отфильтровать расходы по категории «{category}»")
    def filter_by(self, category: str) -> ExpensesScreen:
        self.tap(self.FILTER)
        CategoryPicker(self.driver, self.timeout).choose(category)
        return self

    @allure.step("Выйти из учётной записи")
    def logout(self) -> None:
        self.tap(self.LOGOUT)

    def assert_expense_visible(self, expense: Expense) -> None:
        self.element(by_text(expense.title))
        self.element(by_text(f"{expense.amount:.2f} ₽ · {expense.category}"))

    def assert_expense_hidden(self, title: str) -> None:
        hidden = self.until(conditions.invisibility_of_element_located(by_text(title)))
        assert hidden, f"Расход '{title}' всё ещё отображается"

    def assert_empty(self) -> None:
        self.element(self.EMPTY_STATE)
