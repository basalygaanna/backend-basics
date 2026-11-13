from decimal import Decimal

import pytest
from sqlalchemy.orm import sessionmaker

from app.database import DATABASE_URL
from app.models import User, Order
from app.repository import UserRepository, OrderRepository
from app.service import OrderService


def test_failure_rollback(engine, session, clean_db):
    user = User(email="atomic@test.c", balance=Decimal("1000.00"))
    session.add(user)
    session.commit()
    user_id = user.id

    service = OrderService(
        session=session,
        user_repo=UserRepository(session),
        order_repo=OrderRepository(session),
    )

    def failure(*args, **kwargs):
        raise RuntimeError("injected failure")

    service.order_repository.add = failure

    with pytest.raises(RuntimeError, match="injected failure"):
        service.create_order(user_id=user_id, amount=Decimal("100.00"))

    session.rollback()

    Session = sessionmaker(bind=engine, autoflush=False,
                           expire_on_commit=False)
    with Session() as fresh:
        fresh_user = fresh.get(User, user_id)
        orders = fresh.query(Order).filter(Order.user_id == user_id).all()

        assert fresh_user.balance == Decimal(
            "1000.00"), "баланс не должен измениться"
        assert orders == [], "заказ не должен сохраниться"
