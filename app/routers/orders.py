from fastapi import APIRouter, status, HTTPException

from app.dependencies import OrderServiceDep
from app.exceptions import UserNotFoundException, OrderException
from app.schemas import OrderCreate, OrderResponse

router = APIRouter(prefix="/orders", tags=["Заказы"])


@router.post(
    "/",
    summary='Создание заказа',
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_order(data: OrderCreate, service: OrderServiceDep, ):
    try:
        order = service.create_order(
            user_id=data.user_id,
            amount=data.amount,
        )
    except UserNotFoundException as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except OrderException as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    return OrderResponse.model_validate(order)
