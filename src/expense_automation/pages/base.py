"""Common explicit-wait primitives shared by screen objects."""

from __future__ import annotations

import json
from collections.abc import Callable
from typing import TypeVar

from appium.webdriver.common.appiumby import AppiumBy
from appium.webdriver.webdriver import WebDriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as conditions
from selenium.webdriver.support.ui import WebDriverWait

Locator = tuple[str, str]
T = TypeVar("T")


def by_text(value: str) -> Locator:
    """Create a UiAutomator text selector without brittle absolute selectors."""

    quoted = json.dumps(value, ensure_ascii=False)
    return (AppiumBy.ANDROID_UIAUTOMATOR, f"new UiSelector().text({quoted})")


class BaseScreen:
    """Base class that keeps synchronization at the semantic screen layer."""

    def __init__(self, driver: WebDriver, timeout: int) -> None:
        self.driver = driver
        self.timeout = timeout
        self.wait = WebDriverWait(driver, timeout, poll_frequency=0.2)

    def element(self, locator: Locator) -> WebElement:
        """Wait until an element is visible and return it."""

        return self.wait.until(conditions.visibility_of_element_located(locator))

    def tap(self, locator: Locator) -> None:
        """Wait until an element can receive a touch action."""

        element = self.wait.until(conditions.element_to_be_clickable(locator))
        element.click()

    def fill(self, locator: Locator, value: str) -> None:
        """Replace a field value after the field becomes interactable."""

        field = self.wait.until(conditions.element_to_be_clickable(locator))
        field.clear()
        field.send_keys(value)

    def text(self, locator: Locator) -> str:
        return self.element(locator).text

    def is_visible(self, locator: Locator) -> bool:
        """Return visibility without failing a negative assertion immediately."""

        try:
            return self.wait.until(conditions.visibility_of_element_located(locator)) is not None
        except TimeoutException:
            return False

    def until(self, condition: Callable[[WebDriver], T]) -> T:
        """Expose a typed explicit wait for state-based assertions."""

        return self.wait.until(condition)
