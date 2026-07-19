"""A compact wrapper for the native delete confirmation dialog."""

from __future__ import annotations

from appium.webdriver.common.appiumby import AppiumBy

from expense_automation.pages.base import BaseScreen


class ConfirmationDialog(BaseScreen):
    """Confirms destructive actions through an accessible native dialog."""

    DIALOG = ("accessibility id", "confirmation-dialog")
    CONFIRM = (AppiumBy.ID, "android:id/button1")

    def confirm(self) -> None:
        self.element(self.DIALOG)
        self.tap(self.CONFIRM)
