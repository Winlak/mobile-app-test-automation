"""Factories deliberately generate isolated data for parallel-safe test runs."""

from __future__ import annotations

from decimal import Decimal
from secrets import token_hex

from expense_automation.models import Expense


def new_expense(*, category: str = "Продукты", amount: Decimal = Decimal("149.90")) -> Expense:
    """Create an expense whose title cannot collide with another test session."""

    return Expense(title=f"AQA расход {token_hex(4)}", amount=amount, category=category)
