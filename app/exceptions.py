class UserNotFoundException(Exception):
    def __init__(self, user_id):
        super().__init__(f'Пользователь {user_id} не найден')


class OrderException(Exception):
     """Ошибка заказа."""
