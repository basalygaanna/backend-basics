from app.exceptions import OrderException, UserNotFoundException
from app.models import Order
from app.schemas import OrderStatus


class OrderService:
    def __init__(self, session, user_repo, order_repo) -> None:
        self.session = session
        self.user_repository = user_repo
        self.order_repository = order_repo

    def create_order(self, user_id, amount) -> Order:
        if amount <= 0:
            raise OrderException("Сумма не может быть отрицательной")
        with self.session.begin():
            user = self.user_repository.get_by_id(user_id)
            if user is None:
                raise UserNotFoundException(user_id)

            if user.balance < amount:
                raise OrderException("Недостаточно средств")
            user.balance -= amount
            order = Order(user_id=user.id,
                          amount=amount, status=OrderStatus.PENDING)
            self.order_repository.add(order)
            self.session.flush()

        return order
