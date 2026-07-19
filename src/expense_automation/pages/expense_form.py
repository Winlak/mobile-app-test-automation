"""Add and edit expense form object."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

import allure

from expense_automation.components.category_picker import CategoryPicker
from expense_automation.components.confirmation_dialog import ConfirmationDialog
from expense_automation.models import Expense
from expense_automation.pages.base import BaseScreen

if TYPE_CHECKING:
    from expense_automation.pages.expenses import ExpensesScreen


class ExpenseFormScreen(BaseScreen):
    """Models validation, persistence and deletion of a single expense."""

    SCREEN = ("accessibility id", "expense-form-screen")
    TITLE = ("accessibility id", "expense-title")
    AMOUNT = ("accessibility id", "expense-amount")
    CATEGORY = ("accessibility id", "expense-category")
    SAVE = ("accessibility id", "expense-save")
    DELETE = ("accessibility id", "expense-delete")
    ERROR = ("accessibility id", "expense-form-error")

    def wait_until_opened(self) -> ExpenseFormScreen:
        self.element(self.SCREEN)
        return self

    @allure.step("Сохранить расход «{expense.title}»")
    def save(self, expense: Expense) -> ExpensesScreen:
        from expense_automation.pages.expenses import ExpensesScreen

        self.fill(self.TITLE, expense.title)
        self.fill(self.AMOUNT, f"{expense.amount:.2f}")
        self.choose_category(expense.category)
        self.tap(self.SAVE)
        return ExpensesScreen(self.driver, self.timeout).wait_until_opened()

    @allure.step("Выбрать категорию «{category}»")
    def choose_category(self, category: str) -> None:
        self.tap(self.CATEGORY)
        CategoryPicker(self.driver, self.timeout).choose(category)

    @allure.step("Отправить форму с названием «{title}» и суммой «{amount}»")
    def submit_raw(self, title: str, amount: str) -> None:
        self.fill(self.TITLE, title)
        self.fill(self.AMOUNT, amount)
        self.tap(self.SAVE)

    def error_message(self) -> str:
        return self.text(self.ERROR)

    @allure.step("Удалить расход")
    def delete(self) -> None:
        self.tap(self.DELETE)
        ConfirmationDialog(self.driver, self.timeout).confirm()


def expense_with(title: str, amount: str, category: str) -> Expense:
    """Build an expected value for a post-edit assertion."""

    return Expense(title=title, amount=Decimal(amount), category=category)
