class OrderRepository:
    def __init__(self):
        self._orders = []

    def get_all(self) -> list[dict]:
        return self._orders.copy()

    def get_by_id(self, order_id: int) -> dict | None:
        for order in self._orders:
            if order['id'] == order_id:
                return order
        return None

    def add(self, order) -> dict:
        self._orders.append(order)
        return order

    def update(self, order_id, update_data) -> dict | None:
        for order in self._orders:
            if order['id'] == order_id:
                order.update(update_data)
                return order
        return None

    def delete(self, order_id) -> None:
        for order in self._orders:
            if order['id'] == order_id:
                self._orders.remove(order)
                break
        return None
