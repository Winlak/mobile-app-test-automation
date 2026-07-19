"""Small domain objects used by tests and screen objects."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class Expense:
    title: str
    amount: Decimal
    category: str

    @property
    def amount_text(self) -> str:
        """Format money exactly as the Android demo app renders it."""

        return f"{self.amount:.2f} ₽"
