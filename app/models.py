from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.schemas import OrderStatus


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(
        String(320),
        unique=True,
        nullable=False
    )
    balance: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        default=Decimal(0)
    )
    orders: Mapped[list["Order"]] = relationship(back_populates="user")


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False
    )
    amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False
    )
    status: Mapped[OrderStatus] = mapped_column(
        String(20),
        nullable=False,
        server_default=OrderStatus.PENDING.value
    )
    user: Mapped[User] = relationship(back_populates="orders")
