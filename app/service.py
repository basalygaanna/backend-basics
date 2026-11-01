from exceptions import OrderNotFoundError, OrderAlreadyCompleted
from repository import OrderRepository


class OrderService:
    def __init__(self, repository: OrderRepository):
        self.repository = repository

