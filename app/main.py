from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from .routers.orders import router
from .exceptions import OrderAlreadyCompleted, OrderNotFoundError
from .dependencies import SettingsDep, ServiceDep

app = FastAPI(
    title="Учёт заказов кофейни",
    description="Сервис для бариста: создание заказов, отслеживание статуса и отмена.",
    version="1.0.0"
)

app.include_router(router)


@app.exception_handler(OrderNotFoundError)
async def order_not_found_handler(request: Request, exc: OrderNotFoundError):
    return JSONResponse(
        status_code=404,
        content={"detail": str(exc)}
    )


@app.exception_handler(OrderAlreadyCompleted)
async def order_already_completed_handler(request: Request,
                                          exc: OrderAlreadyCompleted):
    return JSONResponse(
        status_code=409,
        content={"detail": str(exc)}
    )


@app.get(
    "/",
    tags=['Сервисы'],
    summary='Приветствие сервиса',
)
async def read_root():
    return {"message": "Добро пожаловать!"}


@app.get(
    "/info",
    tags=['Сервисы'],
    summary='Информация о сервисе',
)
def get_info(settings: SettingsDep, service: ServiceDep):
    return {'app_name': settings.app_name,
            'quantity': service.get_quantity()}
