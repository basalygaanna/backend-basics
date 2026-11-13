from typing import Iterator, Annotated
from fastapi import Depends
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.service import OrderService
from app.repository import UserRepository, OrderRepository


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
