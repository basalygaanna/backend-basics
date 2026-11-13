# SQLAlchemy и Alembic

API заказов на FastAPI + SQLAlchemy + PostgreSQL + Alembic

## Стек и требования

- Python 3.12


## Инструкции по запуску

### 1. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 2. PostgreSQL

Убедитесь, что служба PostgreSQL запущена. Создайте БД `app`:

```bash
psql -h localhost -U postgres
CREATE DATABASE app;
\q
```

### 3. Переменные окружения

В `.env` (или в `app/database.py`) укажите строку подключения:

```
DATABASE_URL=postgresql+psycopg://postgres:<пароль>@localhost:5432/app
```

В `alembic.ini` пропишите тот же URL в `sqlalchemy.url`.

### 4. Миграции

```bash
python -m alembic upgrade head
```

Проверка:

```bash
python -m alembic current
# → bbc4f5d2ce6e (head)
```

### 5. Запуск приложения

```bash
uvicorn app.main:app --reload
```

Swagger: http://127.0.0.1:8000/docs

### 6. Тесты

```bash
python -m pytest tests/ -v
```

---

## 1. Модели и репозитории

### Модели (`app/models.py`)

- `User`: `id` (PK), `email` (String(320), unique, NOT NULL), `balance` (Numeric(12,2), NOT NULL), `orders` (relationship).
- `Order`: `id` (PK), `user_id` (FK → users.id, NOT NULL), `amount` (Numeric(12,2), NOT NULL), `status` (String(20), NOT NULL, server_default='pending'), `user` (relationship).

Связи: `User.orders` ↔ `Order.user` через `relationship(back_populates=...)`.

### Репозитории (`app/repository.py`)

- `UserRepository`: `create`, `get_by_email`, `get_by_id`.
- `OrderRepository`: `add`.

Репозитории получают внедрённую `Session`, не создают сессий, не вызывают `commit()`/`rollback()`. Проверки положительности суммы, наличия пользователя и достаточности баланса — в `OrderService`, не в репозиториях.

---

## 2. Начальная миграция

Файл: `alembic/versions/8da9291f4fa0_initial_users_and_orders.py`

Создаёт таблицы `users` и `orders` с PK, FK `orders.user_id → users.id`, типами `Numeric(12,2)`, `String(320)`, ограничениями `NOT NULL` / `UNIQUE(email)`.

Применение на пустой БД:

```bash
python -m alembic upgrade head
```

Проверка через psql:

```sql
\dt
\d users
\d orders
```

После миграции приложение создаёт пользователя и заказ через `POST /orders/` — проверено, запись появляется в БД.

---

## 3. Миграция status

Файл: `alembic/versions/bbc4f5d2ce6e_add_order_status.py`

- `nullable=False` + `server_default='pending'` — существующие заказы получают `pending`, миграция не падает.

В `alembic/env.py` выполнено `import app.models` **до** `target_metadata = Base.metadata`, поэтому autogenerate видит модели и корректно определяет изменение `orders.status`.

Сгенерированная миграция проверена вручную. Autogenerate — черновик, его результат требует ревью.

### Проверка цикла на БД с существующими заказами

До миграции в `orders` были строки (созданы вручную через psql).

```bash
python -m alembic upgrade head
```

```sql
SELECT id, status FROM orders;
-- у всех строк status = 'pending'
```

```bash
python -m alembic downgrade -1
```

```sql
\d orders
-- колонки status нет
```

```bash
python -m alembic upgrade head
```

```sql
SELECT id, status FROM orders;
-- снова 'pending'
```

**Вывод:** `downgrade` безвозвратно удаляет колонку вместе со значениями. Повторный `upgrade` восстанавливает только `pending`, а не исходные данные. Цикл **не является обратимым восстановлением данных без потерь**.

---

## 4. Атомарное создание заказа

### Граница транзакции

В `OrderService.create_order` (`app/service.py`):

 - списание `User.balance` и вставка `Order` — **в одной транзакции**
 - `commit`/`rollback` — только в сервисе, не в репозиториях.

### Тест injected failure (`tests/test_order.py`)

Результат:

```
tests/test_order.py::test_failure_rollback PASSED
```

Тест подменяет `OrderRepository.add` на функцию, бросающую `RuntimeError`, — ошибка происходит **после** списания баланса и **до** вставки заказа. После исключения проверка выполняется в **новой сессии**: баланс остался `1000.00`, заказов `0`. Это доказывает, что списание и вставка откатились вместе.

---

## 5. Проблема N+1

Эксперимент: **5 пользователей × 2 заказа**, свежая сессия для каждого варианта, счётчик `before_cursor_execute` на engine, сброс перед каждым замером.

### Наивный вариант

```python
users = session.scalars(select(User)).all()
for u in users:
    _ = [o.amount for o in u.orders]
```

Результат: **6 запросов** (1 на `users` + 5 на `orders` по одному на пользователя).

### selectinload

```python
users = session.scalars(
    select(User).options(selectinload(User.orders))
).all()
for u in users:
    _ = [o.amount for o in u.orders]
```

Результат: **2 запроса** (основной + один пакетный `IN`).


### Вывод pytest

```
tests/test_n_plus_one.py::test_naive_n_plus_one
naive: 6 queries (ожидаем 1 + 5 = 6)
PASSED

tests/test_n_plus_one.py::test_selectinload
selectinload: 2 queries (ожидаем 2)
PASSED

2 passed
```

`selectinload` устраняет N+1: связь `User.orders` загружается заранее двумя запросами вместо `1 + N`.

---

## 6. Результаты тестов

```
$ python -m pytest tests/ -v

tests/test_order.py::test_failure_rollback PASSED
tests/test_n_plus_one.py::test_naive_n_plus_one PASSED
tests/test_n_plus_one.py::test_selectinload PASSED

3 passed
```

## Часть 2. Ревью пяти фрагментов

Формат для каждого: **дефект → нарушенный инвариант → последствие → исправление → проверка**.

### Задание 1. Ошибка сессии и rollback

Фрагмент: после провалившегося `flush()` в `except` печатается сообщение, затем `session.add(another)` и `session.commit()`.

- **Дефект:** после ошибки `flush()` транзакция «сломана», следующий `commit()` выбросит `PendingRollbackError`.
- **Инвариант:** перед продолжением работы с сессией после ошибки нужен явный `rollback()`.
- **Последствие:** `second` не сохраняется, ошибка вводит в заблуждение.
- **Исправление:** в `except` вызвать `session.rollback()` до следующей операции.
- **Проверка:** после `rollback()` выполнить новую операцию (`add` + `commit`) — должно пройти без ошибок.

**Различие `rollback` и `close`:**
- `rollback` завершает неудачную транзакцию, сессия остаётся рабочей.
- `close` освобождает ресурсы, откатывает незавершённое, отсоединяет ORM-объекты. Сессию **можно использовать снова** (SQLAlchemy допускает повторное использование после `close()`). Но при **продолжении** текущей единицы работы нужен именно `rollback()`, а не `close()`.

### Задание 2. Атомарная транзакция

Фрагмент: `user.balance -= amount; session.commit(); order = ...; session.add(order); session.commit()`.

- **Дефект:** два `commit()` — списание и вставка не атомарны.
- **Инвариант:** списание баланса и создание заказа — одна транзакция.
- **Последствие:** при ошибке между коммитами деньги списаны, заказа нет.
- **Исправление:** одна граница `with session.begin():` вокруг обоих шагов, `commit` только в конце.
- **Проверка:** тест с injected failure между списанием и `add`; проверка **новой сессией** — ни уменьшенного баланса, ни нового заказа.

### Задание 3. Граница репозитория и unit of work

Фрагмент: `OrderRepository.add` вызывает `self.session.commit()`; в конце `create_order` — `session.rollback()`; нет проверок суммы, пользователя, баланса.

- **Дефект 1:** `commit()` в репозитории — репозиторий управляет транзакцией, ломает unit of work.
- **Дефект 2:** `rollback()` в конце use case после `commit` — откатывать уже нечего.
- **Дефект 3:** нет валидации `amount > 0`, нет проверки пользователя и баланса.
- **Инвариант:** репозитории получают общую внедрённую `Session`, не создают сессии, не вызывают `commit()`/`rollback()`. Граница транзакции — в use case.
- **Последствие:** невозможность собрать несколько шагов в одну атомарную операцию; некорректные данные (отрицательная сумма, перерасход).
- **Исправление:** убрать `commit` из репозитория; `commit`/`rollback` — только в сервисе через `with session.begin()`; добавить проверки в сервис.
- **Проверка:** тест на атомарность + тест на валидацию (отрицательная сумма → исключение).

### Задание 4. Ревью Alembic-миграции

Фрагмент:
```python
def upgrade():
    op.add_column("orders", sa.Column("status", sa.String(20), nullable=False))
def downgrade():
    op.drop_column("users", "status")
# env.py
target_metadata = Base.metadata
```

**Дефект 1 — `nullable=False` без `server_default`.**
- Дефект: добавление `NOT NULL`-колонки без значения по умолчанию.
- Инвариант: миграция должна применяться на таблице с существующими строками.
- Последствие: `upgrade` падает — существующим строкам нечего присвоить.
- Исправление: `server_default='pending'` (и/или `op.execute("UPDATE orders SET status='pending' WHERE status IS NULL")`).
- Проверка: `upgrade` на таблице с заказами проходит, у всех строк `status='pending'`.

**Дефект 2 — `downgrade` удаляет не ту таблицу.**
- Дефект: `op.drop_column("users", "status")` вместо `orders`.
- Инвариант: `downgrade` должен откатывать именно то изменение, что сделал `upgrade`.
- Последствие: `downgrade` падает (в `users` нет `status`) или портит чужую таблицу.
- Исправление: `op.drop_column("orders", "status")`.
- Проверка: `downgrade -1` → колонки `status` в `orders` нет, `users` не тронута.

**Дефект 3 — модели не зарегистрированы в `Base.metadata` до `context.configure`.**
- Дефект: `target_metadata = Base.metadata` без `import app.models` до этого.
- Инвариант: `Base.metadata` должен содержать все модели к моменту сравнения.
- Последствие: autogenerate создаёт пустую миграцию — не видит таблиц.
- Исправление: `import app.models` **до** `target_metadata = Base.metadata` в `env.py`.
- Проверка: `python -c "from app.database import Base; import app.models; print(Base.metadata.tables.keys())"` → `dict_keys(['users', 'orders'])`.

**Дефект 4 — autogenerate как «готовая» миграция.**
- Дефект: считать, что autogenerate выполняет миграцию данных.
- Инвариант: autogenerate — черновик, миграция данных пишется вручную.
- Последствие: существующие строки не получают `pending`, если `server_default` не прописан.
- Исправление: проверить `server_default`, при необходимости добавить `op.execute(...)`.
- Проверка: после `upgrade` у всех существующих строк `status='pending'`.

**Потеря данных при `downgrade`:** `downgrade` удаляет колонку вместе со значениями; повторный `upgrade` даёт только `pending`, а не исходные данные. Цикл необратим без потерь.- **Важно:** `downgrade` удаляет значения статуса, повторный `upgrade` даёт только `pending`, а не исходные данные.

### Задание 5. Проблема N+1

- **Дефект:** наивный вариант `for u in users: u.orders` даёт `1 + N` запросов (ленивая загрузка).
- **Инвариант:** число запросов не должно расти линейно с числом пользователей.
- **Последствие:** на больших данных — деградация производительности.
- **Исправление:** `select(User).options(selectinload(User.orders))` — 2 запроса (основной + `IN`).
- **Проверка:** эксперимент с 5 пользователями, свежая сессия и сброс счётчика для каждого варианта. Наивный — 6 (`1 + 5`), `selectinload` — 2. Подтверждается SQL-логом: 5× `WHERE user_id = ?` против одного `WHERE user_id IN (...)`.

---


