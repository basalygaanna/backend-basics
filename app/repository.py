from sqlalchemy import select

from app.models import User, Order


class UserRepository:
    def __init__(self, session):
        self.session = session

    def create(self, user: User):
        self.session.add(user)

    def get_by_email(self, email: str) -> User | None:
        return self.session.scalars(
            select(User).where(User.email == email)
        ).one_or_none()

    def get_by_id(self, user_id: int) -> User | None:
        return self.session.get(User, user_id)


class OrderRepository:
    def __init__(self, session):
        self.session = session

    def add(self, order: Order) -> None:
        self.session.add(order)
