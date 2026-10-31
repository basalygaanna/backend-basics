import datetime as dt

from fastapi import FastAPI, Depends, status, HTTPException, Query, Response
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Annotated
from enum import Enum

app = FastAPI(
    title="Учёт заказов кофейни",
    description="Сервис для бариста: создание заказов, отслеживание статуса и отмена.",
    version="1.0.0"
)
orders = []
last_created_id = 0


class Size(str, Enum):
    S = 's'
    M = 'm'
    L = 'l'


class Status(str, Enum):
    pending = 'В ожидании'
    ready = 'Готов'
    completed = 'Выполнен'


class Order(BaseModel):
    id: int = Field(gt=0, description='ID заказа', examples=[1, 2])
    drink: str = Field(min_length=1, description='Название напитка',
                       examples=['Латте', 'Раф'])
    size: Size = Field(description='Размер напитка', examples=['s', 'm'])
    quantity: int = Field(gt=0, description='Количество', examples=[4, 5])
    customer_name: str | None = Field(default=None, description='Имя клиента',
                                      examples=['Анна', 'Наталья'])
    status: Status = Field(description="Статус заказа",
                           examples=['В ожидании', 'Готов'])
    created_at: dt.datetime = Field(description="Время создания",
                                    examples=['2026-10-31T20:40:52.344Z',
                                              '2026-10-30T20:40:52.344Z]'])


class OrderCreate(BaseModel):
    drink: str = Field(min_length=1, description='Название напитка',
                       examples=['Латте', 'Раф'])
    size: Size = Field(description='Размер напитка', examples=['s', 'm'])
    quantity: int = Field(gt=0, description='Количество', examples=[4, 5])
    customer_name: str | None = Field(default=None, description='Имя клиента',
                                      examples=['Анна', 'Наталья'])


class OrderUpdate(BaseModel):
    drink: str | None = Field(default=None, min_length=1,
                              description='Название напитка',
                              examples=['Латте', 'Раф'])
    size: Size | None = None
    quantity: int | None = Field(default=None, gt=0, description='Количество',
                                 examples=[4, 5])
    customer_name: str | None = Field(default=None, description='Имя клиента',
                                      examples=['Анна', 'Наталья'])
    status: Status | None = None


class Settings(BaseSettings):
    app_name: str = "Учет заказов кофейни"
    default_page_size: int = 20
    max_page_size: int = 50

    model_config = SettingsConfigDict(env_file='.env', extra='ignore')


def get_settings() -> Settings:
    return Settings()


SettingsDep = Annotated[Settings, Depends(get_settings)]


@app.get(
    "/",
    tags=['Сервисы'],
    summary='Приветствие сервиса',
)
async def read_root():
    return {"message": "Добро пожаловать!"}


@app.post(
    "/orders",
    tags=['Заказы'],
    summary='Создание заказа',
    response_model=Order,
    status_code=status.HTTP_201_CREATED,
)
def create_order(order: OrderCreate):
    global last_created_id
    new_order = order.model_dump()
    new_order['id'] = last_created_id + 1
    last_created_id += 1
    new_order['created_at'] = dt.datetime.now()
    new_order['status'] = Status.pending
    orders.append(new_order)
    return new_order


@app.get(
    "/orders",
    tags=['Заказы'],
    summary='Получение списка заказов',
    response_model=list[Order],
)
def list_orders(
        settings: SettingsDep,
        status_filter: Status | None = Query(default=None,
                                             description='Фильтр по статусу'),
        sort_by: str | None = Query(default=None,
                                    description='Сортировка: created_at или drink'),
        limit: int | None = Query(default=None, ge=1,
                                  description='Количество записей'),
        offset: int = Query(default=0, ge=0, description='Смещение', )
):
    result = orders.copy()
    if status_filter:
        result = [i for i in result if i['status'] == status_filter]
    if sort_by == 'created_at':
        result.sort(key=lambda x: x['created_at'])
    elif sort_by == 'drink':
        result.sort(key=lambda x: x['drink'])
    return result[offset: offset + min(limit or settings.default_page_size,
                                       settings.max_page_size)]


@app.get(
    "/orders/{order_id}",
    tags=['Заказы'],
    summary='Получение заказа по id',
    response_model=Order,
)
def get_order(order_id: int):
    for order in orders:
        if order['id'] == order_id:
            return order
    raise HTTPException(status_code=404, detail='Заказ не найден')


@app.patch(
    "/orders/{order_id}",
    tags=['Заказы'],
    summary='Изменение части заказа',
    response_model=Order,
)
def change_order(order_id: int, part_order: OrderUpdate):
    for order in orders:
        if order['id'] == order_id:
            order.update(part_order.model_dump(exclude_unset=True))
            return order
    raise HTTPException(status_code=404, detail='Заказ не найден')


@app.delete(
    "/orders/{order_id}",
    tags=['Заказы'],
    summary='Удаление (отмена) заказа',
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_order(order_id: int):
    for order in orders:
        if order['id'] == order_id:
            orders.remove(order)
            return Response(status_code=status.HTTP_204_NO_CONTENT)
    raise HTTPException(status_code=404, detail='Заказ не найден')


@app.get(
    "/info",
    tags=['Сервисы'],
    summary='Информация о сервисе',
)
def get_info(settings: SettingsDep):
    return {'app_name': settings.app_name, 'quantity': len(orders)}
