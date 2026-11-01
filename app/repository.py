import datetime as dt

from exceptions import OrderNotFoundError
from fastapi import Response, status

from schemas import OrderStatus


class OrderRepository:
    def __init__(self):
        self._orders = []
        self.last_created_id = 0

    def get_all(self) -> list[dict]:
        return self._orders

    def get_by_id(self, order_id: int) -> dict | None:
        for order in self._orders:
            if order['id'] == order_id:
                return order
        return None

    def add(self, order) -> dict:
        new_order = order.model_dump()
        new_order['id'] = self.last_created_id + 1
        self.last_created_id += 1
        new_order['created_at'] = dt.datetime.now()
        new_order['status'] = OrderStatus.pending
        self._orders.append(new_order)
        return new_order

    def update(self, order_id, update_data) -> dict | None:
        for order in self._orders:
            if order['id'] == order_id:
                order.update(update_data.model_dump(exclude_unset=True))
                return order
        return None

    def delete(self, order_id) -> Response | None:
        for order in self._orders:
            if order['id'] == order_id:
                self._orders.remove(order)
                return Response(status_code=status.HTTP_204_NO_CONTENT)
        return None
