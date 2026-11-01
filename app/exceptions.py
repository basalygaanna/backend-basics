class OrderNotFoundError(Exception):
    """Заказ не найден"""


class OrderAlreadyCompleted(Exception):
    """Заказ уже выполнен или отменен"""
