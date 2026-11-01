class OrderNotFoundError(Exception):
    def __init__(self, order_id):
        super().__init__(f'Заказ {order_id} не найден')


class OrderAlreadyCompleted(Exception):
    def __init__(self, order_id):
        super().__init__(f'Заказ {order_id} уже выполнен и не может быть изменен')

