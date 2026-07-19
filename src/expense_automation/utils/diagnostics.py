"""Failure artifact capture that never serialises configured credentials."""

from __future__ import annotations

import json
import re
import subprocess
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast

import allure
from appium.webdriver.webdriver import WebDriver

from expense_automation.config import Settings

SENSITIVE_KEY = re.compile(r"password|token|secret|authorization|cookie", re.IGNORECASE)
SAFE_NAME = re.compile(r"[^a-zA-Z0-9_.-]+")
attach_file = cast(Callable[..., None], allure.attach.file)


def capture_failure_artifacts(driver: WebDriver, settings: Settings, node_id: str) -> Path:
    """Persist and attach a screenshot, XML, logcat and safe capabilities on failure."""

    artifact_dir = _artifact_dir(node_id)
    screenshot = artifact_dir / "screenshot.png"
    source = artifact_dir / "page-source.xml"
    logcat = artifact_dir / "logcat.txt"
    capabilities = artifact_dir / "capabilities.json"

    screenshot.write_bytes(driver.get_screenshot_as_png())
    source.write_text(_redact(driver.page_source, settings), encoding="utf-8")
    logcat.write_text(_redact(_read_logcat(driver, settings), settings), encoding="utf-8")
    capabilities.write_text(
        json.dumps(
            _sanitize(dict(driver.capabilities)), ensure_ascii=False, indent=2, sort_keys=True
        ),
        encoding="utf-8",
    )

    attach_file(str(screenshot), name="screenshot", attachment_type=allure.attachment_type.PNG)
    attach_file(str(source), name="page source", attachment_type=allure.attachment_type.XML)
    attach_file(str(logcat), name="logcat", attachment_type=allure.attachment_type.TEXT)
    attach_file(str(capabilities), name="capabilities", attachment_type=allure.attachment_type.JSON)
    return artifact_dir


def _artifact_dir(node_id: str) -> Path:
    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%S.%fZ")
    name = SAFE_NAME.sub("_", node_id).strip("_")
    path = Path("artifacts") / f"{timestamp}_{name}"
    path.mkdir(parents=True, exist_ok=False)
    return path


def _read_logcat(driver: WebDriver, settings: Settings) -> str:
    serial = settings.udid or str(driver.capabilities.get("udid", ""))
    command = ["adb"]
    if serial:
        command.extend(["-s", serial])
    command.extend(["logcat", "-d", "-t", "400"])
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=10, check=False)
    except (FileNotFoundError, subprocess.TimeoutExpired) as error:
        return f"Не удалось получить logcat: {error}"
    return result.stdout or result.stderr or "logcat не вернул строк"


def _sanitize(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: "***" if SENSITIVE_KEY.search(key) else _sanitize(item)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [_sanitize(item) for item in value]
    return value


def _redact(value: str, settings: Settings) -> str:
    return value.replace(settings.test_user.password, "***")
