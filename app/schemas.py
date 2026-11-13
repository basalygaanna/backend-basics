from decimal import Decimal
from enum import Enum
from pydantic import BaseModel, ConfigDict, Field


class OrderStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    CANCELLED = "cancelled"


class OrderCreate(BaseModel):
    user_id: int = Field(description='ID пользователя', examples=[1, 2])
    amount: Decimal = Field(gt=0, description='Сумма заказа, должна быть > 0',
                            examples=[100.00, 250.50])


class OrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(description='ID заказа', examples=[1, 2])
    user_id: int = Field(description='ID пользователя', examples=[1, 2])
    amount: Decimal = Field(description='Сумма заказа',
                            examples=[100.00, 250.50])
    status: OrderStatus = Field(description='Статус заказа',
                        examples=['pending', 'paid'])

