# Android UI Test Automation: Expense Tracker

Самостоятельный проект UI-автоматизации Android-приложения учёта личных расходов. Репозиторий содержит небольшой исходный код стабильного demo SUT, но его основной объём и смысл — воспроизводимый Python-фреймворк Appium-тестов.

SUT покрывает вход, создание, изменение, удаление и фильтрацию расходов. Данные хранятся локально в `SharedPreferences`, поэтому сценарий проверяет реальную персистентность приложения, а не имитацию API. Внешний публичный APK не нужен: фиксированная версия SUT собирается из исходников этого репозитория.

## Что проверяется

- успешный и неуспешный вход;
- добавление расхода и его отображение с суммой и категорией;
- редактирование и удаление с подтверждением;
- фильтрация по категории;
- обязательные поля и невалидные денежные значения;
- сохранение расхода и сессии после перезапуска процесса;
- корректный logout;
- связный e2e-путь от входа до удаления расхода и выхода.

Каждый тест генерирует уникальное название расхода. Перед каждым сценарием Appium останавливает приложение, очищает его данные и запускает снова, поэтому тесты не зависят от порядка запуска и синхронизируются только по состоянию интерфейса.

## Архитектура

```text
src/expense_automation/
├── config.py                 # YAML + env + CLI конфигурация и W3C capabilities
├── data.py, models.py         # изолированные тестовые данные и доменная модель
├── pages/                     # Screen Object: Login, Expenses, ExpenseForm
├── components/                # CategoryPicker, ConfirmationDialog, AppLifecycle
└── utils/diagnostics.py       # артефакты падения без секретов
conftest.py                    # driver lifecycle, reset, UI-авторизация, pytest hook
tests/
├── test_auth.py
├── test_expenses.py
└── test_e2e.py
sut/                           # компактный локальный Android SUT на Kotlin
config/devices.yaml            # профили эмулятора и физического устройства
```

Тесты знают только бизнес-действия Screen Object, а не локаторы. Повторяемые нативные диалоги вынесены в компоненты. Синхронизация выполняется через `WebDriverWait` и ожидаемые состояния; статических пауз в тестовом коде нет.

## Prerequisites

- Python 3.12+;
- Node.js 20+ и Appium 2;
- JDK 17;
- Android SDK Platform 35, Build-Tools 35 и Android Emulator;
- Android SDK Platform-Tools (`adb` в `PATH`);
- Allure CLI — только для локального просмотра отчёта.

На macOS удобно установить системные зависимости через Android Studio (SDK Manager) и выбранный менеджер пакетов. После установки задайте `ANDROID_HOME` или `ANDROID_SDK_ROOT` и добавьте `$ANDROID_HOME/platform-tools`, `$ANDROID_HOME/emulator` и `$ANDROID_HOME/cmdline-tools/latest/bin` в `PATH`.

## Быстрый старт с чистого окружения

Из корня репозитория:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
make install

npm install --global appium@2
make appium-setup

make build-sut
cp .env.example .env
```

`make build-sut` запускает проверенный Gradle Wrapper и создаёт `sut/app/build/outputs/apk/debug/app-debug.apk`. Версии Android Gradle Plugin, Kotlin и Gradle закреплены в файлах SUT; это исключает зависимость от меняющегося внешнего тестового приложения.

### Создание и запуск эмулятора

Ниже пример для API 35. Имя `Expense_API_35` можно выбрать другое — оно не является частью конфигурации тестов.

```bash
sdkmanager --install "platform-tools" "platforms;android-35" "build-tools;35.0.0" \
  "emulator" "system-images;android-35;google_apis;arm64-v8a"
avdmanager create avd --name Expense_API_35 \
  --package "system-images;android-35;google_apis;arm64-v8a"
emulator -avd Expense_API_35 -no-snapshot -no-boot-anim
adb wait-for-device
```

На Intel/Linux вместо `arm64-v8a` обычно нужен `x86_64`. Для физического устройства включите USB debugging и убедитесь, что оно видно в `adb devices`.

### Appium 2 и UiAutomator2

В отдельном терминале запустите сервер:

```bash
appium
```

Один раз на машину установите драйвер:

```bash
appium driver install uiautomator2
appium driver list --installed
```

### Запуск тестов

```bash
# Короткий критический набор
make test-smoke

# Регрессия без e2e-маркера
make test-regression

# Связный пользовательский сценарий
make test-e2e

# Любой набор с конкретным APK или профилем физического устройства
pytest -m "smoke or e2e" --device real_device --apk /absolute/path/app-debug.apk
```

Основные маркеры: `smoke`, `regression`, `auth`, `e2e`. Они независимы и комбинируются обычным синтаксисом Pytest, например `pytest -m "regression and not e2e"`.

Для отчёта Allure передайте `--alluredir=allure-results` (Makefile уже это делает) и затем выполните:

```bash
make allure
```

## Конфигурация

Базовый файл — [`config/devices.yaml`](config/devices.yaml). Приоритет значений: YAML → переменные окружения → CLI. Пример значений окружения находится в [`.env.example`](.env.example); файл `.env` намеренно не подгружается автоматически, чтобы тестовый запуск не получал неявных секретов — экспортируйте нужные переменные в shell или используйте свой менеджер окружения.

| Задача | Способ |
| --- | --- |
| URL Appium | `APPIUM_URL` или `--appium-url` |
| APK | `APK_PATH` или `--apk` |
| Android/API | `ANDROID_VERSION` или `--android-version` |
| serial устройства | `UDID` или `--udid` |
| явное ожидание | `EXPLICIT_TIMEOUT` или `--explicit-timeout` |
| Appium command timeout | `NEW_COMMAND_TIMEOUT` или `--new-command-timeout` |
| ADB command timeout, мс | `ADB_EXEC_TIMEOUT` |
| установка UiAutomator2, мс | `SERVER_INSTALL_TIMEOUT` |
| запуск UiAutomator2, мс | `SERVER_LAUNCH_TIMEOUT` |
| оставить данные для отладки | `--keep-app-data` |

`real_device` — шаблон профиля. Перед его применением укажите serial: `UDID=<serial> pytest --device real_device -m smoke`. Демо-учётная запись предсказуема и предназначена только для SUT: `qa.user@example.test` / `Expense123!`. Пароль не выводится в шаги Allure и редактируется из page source/logcat при сборе артефактов.

### Один девайс и масштабирование

По умолчанию проект намеренно запускается последовательно на одном устройстве: это самый устойчивый режим, один Appium-сеанс и reset перед каждым тестом. Для нескольких устройств создайте отдельный YAML-профиль на каждый `UDID`, назначьте уникальные `system_port` и `mjpeg_server_port`, поднимите по Appium-серверу на устройство и распределите тесты между процессами CI. Из-за отдельных storage и генерируемых test data сценарии к этому готовы; `pytest-xdist` можно добавить, когда инфраструктура предоставляет изолированные устройства.

## Стратегия локаторов

Приоритет локаторов:

1. `accessibility id` для действий и экранов (`login-submit`, `expense-save`, `logout`);
2. Android `resource-id` для стабильных структурных элементов внутри SUT;
3. точный текст через UiAutomator для бизнес-данных и системных диалогов.

Абсолютные XPath не используются. Все accessibility id живут в `sut/app/src/main/res/values/strings.xml`, поэтому контракт приложения с тестами легко увидеть и поддерживать.

## Очистка данных и диагностика

Фикстура `reset_application` выполняет `terminateApp`, `mobile: clearApp` и `activateApp` перед каждым тестом. Это очищает `SharedPreferences` и возвращает SUT к login screen. Флаг `--keep-app-data` существует только для ручного расследования и не должен использоваться в CI.

Если setup или test-call падает, hook Pytest сохраняет в `artifacts/<timestamp>_<test>/` и прикрепляет в Allure:

- screenshot;
- текущий XML page source;
- последние 400 строк `adb logcat`;
- реально согласованные capabilities.

Значения ключей `password`, `token`, `secret`, `authorization`, `cookie` маскируются; пароль demo-аккаунта дополнительно вырезается из текстовых артефактов. Все файлы игнорируются Git.

## Проверки качества и CI

```bash
make check
```

Это выполняет Ruff (включая формат) и строгую проверку типов Mypy для фреймворка. Workflow [`.github/workflows/android-ui.yml`](.github/workflows/android-ui.yml) сначала запускает эти проверки, затем собирает SUT, устанавливает Appium 2 + UiAutomator2 и выполняет `smoke` на headless Android API 35. Зависимости Python и Gradle кэшируются штатными GitHub Actions. Allure Results, `artifacts` и лог Appium выгружаются всегда, в том числе при падении.

Проект не публикует результаты тестов, screenshots или фиктивные бейджи и не выполняет публикацию на GitHub.
