from fastapi import APIRouter, status, Query

from ..schemas import Order, OrderCreate, OrderUpdate, OrderStatus
from ..dependencies import ServiceDep, PaginationDep

router = APIRouter(prefix="/orders", tags=["Заказы"])


@router.post(
    "/",
    summary='Создание заказа',
    response_model=Order,
    status_code=status.HTTP_201_CREATED,
)
def create_order(service: ServiceDep, order: OrderCreate):
    return service.create_order(order)


@router.get(
    "/",
    summary='Получение списка заказов',
    response_model=list[Order],
)
def list_orders(
        service: ServiceDep,
        pagination: PaginationDep,
        status_filter: OrderStatus | None = Query(default=None,
                                                  description='Фильтр по статусу'),
        sort_by: str | None = Query(default=None,
                                    description='Сортировка: created_at или drink'),
):
    return service.list_orders(status_filter, sort_by, pagination.limit,
                               pagination.offset)


@router.get(
    "/{order_id}",
    summary='Получение заказа по id',
    response_model=Order,
)
def get_order(service: ServiceDep, order_id: int):
    return service.get_order(order_id)


@router.patch(
    "/{order_id}",
    summary='Изменение части заказа',
    response_model=Order,
)
def change_order(service: ServiceDep, order_id: int, part_order: OrderUpdate):
    return service.change_order(order_id, part_order)


@router.delete(
    "/{order_id}",
    summary='Удаление (отмена) заказа',
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_order(service: ServiceDep, order_id: int):
    return service.delete_order(order_id)
