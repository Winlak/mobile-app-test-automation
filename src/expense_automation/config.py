"""Typed runtime configuration with YAML, environment and CLI overrides."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True, slots=True)
class TestUser:
    """Credentials of the deterministic account built into the demo SUT."""

    email: str
    password: str


@dataclass(frozen=True, slots=True)
class Settings:
    """All runtime values required to start one Android Appium session."""

    appium_url: str
    app_path: Path
    app_package: str
    app_activity: str
    device_name: str
    platform_version: str | None
    udid: str | None
    explicit_timeout: int
    new_command_timeout: int
    adb_exec_timeout: int
    server_install_timeout: int
    server_launch_timeout: int
    language: str
    locale: str
    auto_grant_permissions: bool
    disable_window_animation: bool
    system_port: int | None
    mjpeg_server_port: int | None
    keep_app_data: bool
    test_user: TestUser

    @property
    def capabilities(self) -> dict[str, Any]:
        """Return W3C capabilities without any secret values."""

        capabilities: dict[str, Any] = {
            "platformName": "Android",
            "appium:automationName": "UiAutomator2",
            "appium:deviceName": self.device_name,
            "appium:app": str(self.app_path),
            "appium:appPackage": self.app_package,
            "appium:appActivity": self.app_activity,
            "appium:noReset": self.keep_app_data,
            "appium:fullReset": False,
            "appium:newCommandTimeout": self.new_command_timeout,
            "appium:adbExecTimeout": self.adb_exec_timeout,
            "appium:uiautomator2ServerInstallTimeout": self.server_install_timeout,
            "appium:uiautomator2ServerLaunchTimeout": self.server_launch_timeout,
            "appium:language": self.language,
            "appium:locale": self.locale,
            "appium:autoGrantPermissions": self.auto_grant_permissions,
            "appium:disableWindowAnimation": self.disable_window_animation,
        }
        if self.platform_version:
            capabilities["appium:platformVersion"] = self.platform_version
        if self.udid:
            capabilities["appium:udid"] = self.udid
        if self.system_port:
            capabilities["appium:systemPort"] = self.system_port
        if self.mjpeg_server_port:
            capabilities["appium:mjpegServerPort"] = self.mjpeg_server_port
        return capabilities


def load_settings(
    config_path: Path,
    device: str,
    *,
    appium_url: str | None = None,
    apk: str | None = None,
    device_name: str | None = None,
    platform_version: str | None = None,
    udid: str | None = None,
    explicit_timeout: int | None = None,
    new_command_timeout: int | None = None,
    keep_app_data: bool = False,
) -> Settings:
    """Load a device profile and apply environment then explicit CLI overrides."""

    raw = _read_yaml(config_path)
    defaults = _mapping(raw, "defaults")
    devices = _mapping(raw, "devices")
    try:
        device_values = _mapping(devices, device)
    except KeyError as error:
        available = ", ".join(devices)
        message = f"Неизвестный профиль устройства '{device}'. Доступны: {available}"
        raise ValueError(message) from error

    values = {**defaults, **device_values}
    env = os.environ
    source_app_path = apk or env.get("APK_PATH") or _required(values, "app_path")
    path = Path(source_app_path).expanduser()
    if not path.is_absolute():
        path = (config_path.parent.parent / path).resolve()

    user_values = _mapping(raw, "test_user")
    return Settings(
        appium_url=appium_url or env.get("APPIUM_URL") or str(_required(values, "appium_url")),
        app_path=path,
        app_package=str(_required(values, "app_package")),
        app_activity=str(_required(values, "app_activity")),
        device_name=device_name or env.get("DEVICE_NAME") or str(_required(values, "device_name")),
        platform_version=(
            platform_version
            or env.get("ANDROID_VERSION")
            or _optional_string(values.get("platform_version"))
        ),
        udid=udid or env.get("UDID") or _optional_string(values.get("udid")),
        explicit_timeout=explicit_timeout
        or int(env.get("EXPLICIT_TIMEOUT") or _required(values, "explicit_timeout")),
        new_command_timeout=int(
            new_command_timeout
            or env.get("NEW_COMMAND_TIMEOUT")
            or _required(values, "new_command_timeout")
        ),
        adb_exec_timeout=int(env.get("ADB_EXEC_TIMEOUT") or _required(values, "adb_exec_timeout")),
        server_install_timeout=int(
            env.get("SERVER_INSTALL_TIMEOUT") or _required(values, "server_install_timeout")
        ),
        server_launch_timeout=int(
            env.get("SERVER_LAUNCH_TIMEOUT") or _required(values, "server_launch_timeout")
        ),
        language=str(_required(values, "language")),
        locale=str(_required(values, "locale")),
        auto_grant_permissions=bool(_required(values, "auto_grant_permissions")),
        disable_window_animation=bool(_required(values, "disable_window_animation")),
        system_port=_optional_int(values.get("system_port")),
        mjpeg_server_port=_optional_int(values.get("mjpeg_server_port")),
        keep_app_data=keep_app_data or env.get("KEEP_APP_DATA", "false").lower() == "true",
        test_user=TestUser(
            email=env.get("TEST_USER_EMAIL") or str(_required(user_values, "email")),
            password=env.get("TEST_USER_PASSWORD") or str(_required(user_values, "password")),
        ),
    )


def _read_yaml(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError(f"Не найден файл конфигурации: {path}")
    with path.open(encoding="utf-8") as stream:
        loaded = yaml.safe_load(stream)
    if not isinstance(loaded, dict):
        raise ValueError(f"Конфигурация {path} должна быть YAML-объектом")
    return loaded


def _mapping(source: dict[str, Any], key: str) -> dict[str, Any]:
    value = source.get(key)
    if not isinstance(value, dict):
        raise KeyError(f"В конфигурации отсутствует объект '{key}'")
    return value


def _required(source: dict[str, Any], key: str) -> Any:
    value = source.get(key)
    if value is None or value == "":
        raise ValueError(f"В конфигурации отсутствует обязательное значение '{key}'")
    return value


def _optional_string(value: Any) -> str | None:
    return str(value) if value not in (None, "") else None


def _optional_int(value: Any) -> int | None:
    return int(value) if value not in (None, "") else None
