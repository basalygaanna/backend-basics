from decimal import Decimal

import pytest
from sqlalchemy import event, select
from sqlalchemy.orm import selectinload, sessionmaker

from app.database import DATABASE_URL
from app.models import User, Order
from app.schemas import OrderStatus


def count_queries(engine, fn):
    Session = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    counter = {"n": 0}

    def _inc(*args, **kwargs):
        counter["n"] += 1

    with Session() as session:
        event.listen(engine, "before_cursor_execute", _inc)
        try:
            fn(session)
        finally:
            event.remove(engine, "before_cursor_execute", _inc)
    return counter["n"]


def seed(engine, users=5, orders_per_user=2):
    """Наполняет БД пользователями и заказами."""
    Session = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    with Session() as s:
        for i in range(users):
            u = User(email=f"n1_{i}@test.c", balance=Decimal("1000.00"))
            s.add(u)
            s.flush()
            for j in range(orders_per_user):
                s.add(Order(user_id=u.id, amount=Decimal("10.00"), status=OrderStatus.PENDING.value))
        s.commit()


def test_naive_n_plus_one(engine, clean_db):
    seed(engine, users=5, orders_per_user=2)

    def run(session):
        users = session.scalars(select(User)).all()
        for u in users:
            _ = [o.amount for o in u.orders]   # ← ленивая загрузка, N запросов

    n = count_queries(engine, run)
    print(f"\nnaive: {n} queries (ожидаем 1 + 5 = 6)")
    assert n == 6


def test_selectinload(engine, clean_db):
    seed(engine, users=5, orders_per_user=2)

    def run(session):
        users = session.scalars(
            select(User).options(selectinload(User.orders))
        ).all()
        for u in users:
            _ = [o.amount for o in u.orders]   # уже загружено, запросов нет

    n = count_queries(engine, run)
    print(f"\nselectinload: {n} queries (ожидаем 2)")
    assert n == 2