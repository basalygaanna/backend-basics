from collections.abc import Iterator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.repository import OrderRepository, UserRepository
from app.service import OrderService


def get_db() -> Iterator[Session]:
    with SessionLocal() as session:
        yield session


SessionDep = Annotated[Session, Depends(get_db)]


def get_order_service(session: SessionDep) -> OrderService:
    return OrderService(
        session=session,
        user_repo=UserRepository(session),
        order_repo=OrderRepository(session),
    )


OrderServiceDep = Annotated[OrderService, Depends(get_order_service)]
