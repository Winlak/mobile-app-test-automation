"""Category selector shared by add/edit screens and list filtering."""

from __future__ import annotations

from expense_automation.pages.base import BaseScreen, by_text


class CategoryPicker(BaseScreen):
    """A native AlertDialog category list addressed by displayed text."""

    DIALOG = ("accessibility id", "category-dialog")

    def choose(self, category: str) -> None:
        self.element(self.DIALOG)
        self.tap(by_text(category))
