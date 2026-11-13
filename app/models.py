from sqlalchemy import Numeric, String, ForeignKey
from sqlalchemy.orm import Mapped, relationship, mapped_column
from decimal import Decimal
from typing import List

from app.database import Base
from app.schemas import OrderStatus


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(320), unique=True,
                                       nullable=False)
    balance: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False,
                                             default=0)
    orders: Mapped[List["Order"]] = relationship(back_populates="user")


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"),
                                         nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    status: Mapped[OrderStatus] = mapped_column(String(20), nullable=False,
                                                server_default=OrderStatus.PENDING.value)
    user: Mapped[User] = relationship(back_populates="orders")
