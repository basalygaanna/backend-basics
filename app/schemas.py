import datetime as dt

from pydantic import BaseModel, Field
from enum import Enum


class DrinkSize(str, Enum):
    S = 's'
    M = 'm'
    L = 'l'


class OrderStatus(str, Enum):
    pending = 'В ожидании'
    ready = 'Готов'
    completed = 'Выполнен'


class Order(BaseModel):
    id: int = Field(gt=0, description='ID заказа', examples=[1, 2])
    drink: str = Field(min_length=1, description='Название напитка',
                       examples=['Латте', 'Раф'])
    size: DrinkSize = Field(description='Размер напитка', examples=['s', 'm'])
    quantity: int = Field(gt=0, description='Количество', examples=[4, 5])
    customer_name: str | None = Field(default=None, description='Имя клиента',
                                      examples=['Анна', 'Наталья'])
    status: OrderStatus = Field(description="Статус заказа",
                                examples=['В ожидании', 'Готов'])
    created_at: dt.datetime = Field(description="Время создания",
                                    examples=['2026-10-31T20:40:52.344Z',
                                              '2026-10-30T20:40:52.344Z]'])


class OrderCreate(BaseModel):
    drink: str = Field(min_length=1, description='Название напитка',
                       examples=['Латте', 'Раф'])
    size: DrinkSize = Field(description='Размер напитка', examples=['s', 'm'])
    quantity: int = Field(gt=0, description='Количество', examples=[4, 5])
    customer_name: str | None = Field(default=None, description='Имя клиента',
                                      examples=['Анна', 'Наталья'])


class OrderUpdate(BaseModel):
    drink: str | None = Field(default=None, min_length=1,
                              description='Название напитка',
                              examples=['Латте', 'Раф'])
    size: DrinkSize | None = None
    quantity: int | None = Field(default=None, gt=0, description='Количество',
                                 examples=[4, 5])
    customer_name: str | None = Field(default=None, description='Имя клиента',
                                      examples=['Анна', 'Наталья'])
    status: OrderStatus | None = None
