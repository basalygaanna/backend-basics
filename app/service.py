import datetime as dt

from .exceptions import OrderNotFoundError, OrderAlreadyCompleted
from .repository import OrderRepository
from .schemas import OrderCreate, OrderUpdate, OrderStatus
from .config import Settings


class OrderService:
    def __init__(self, repository: OrderRepository, settings: Settings):
        self.repository = repository
        self.settings = settings
        self.last_created_id = 0

    def get_quantity(self) -> int:
        return len(self.repository.get_all())

    def create_order(self, order: OrderCreate) -> dict:
        new_order = order.model_dump()
        new_order['id'] = self.last_created_id + 1
        self.last_created_id += 1
        new_order['created_at'] = dt.datetime.now()
        new_order['status'] = OrderStatus.pending
        return self.repository.add(new_order)

    def list_orders(
            self,
            status_filter: OrderStatus | None = None,
            sort_by: str | None = None,
            limit: int | None = None,
            offset: int = 0
    ) -> list[dict]:
        result = self.repository.get_all()
        if status_filter:
            result = [i for i in result if i['status'] == status_filter]
        if sort_by == 'created_at':
            result.sort(key=lambda x: x['created_at'])
        elif sort_by == 'drink':
            result.sort(key=lambda x: x['drink'])
        return result[
               offset: offset + min(limit or self.settings.default_page_size,
                                    self.settings.max_page_size)]

    def get_order(self, order_id: int) -> dict:
        res = self.repository.get_by_id(order_id)
        if res:
            return res
        raise OrderNotFoundError(order_id)

    def change_order(self, order_id: int, part_order: OrderUpdate) -> dict:
        order = self.repository.get_by_id(order_id)
        if not order:
            raise OrderNotFoundError(order_id)
        if order['status'] == OrderStatus.completed:
            raise OrderAlreadyCompleted(order_id)
        return self.repository.update(order_id, part_order.model_dump(
            exclude_unset=True))

    def delete_order(self, order_id: int):
        order = self.repository.get_by_id(order_id)
        if not order:
            raise OrderNotFoundError(order_id)
        if order['status'] == OrderStatus.completed:
            raise OrderAlreadyCompleted(order_id)
        self.repository.delete(order_id)
        return None
