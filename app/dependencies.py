from fastapi import Depends, Query
from typing import Annotated
from functools import lru_cache
from pydantic import BaseModel, Field

from .config import Settings, get_settings
from .repository import OrderRepository
from .service import OrderService


class PaginationParams(BaseModel):
    limit: int | None = Field(default=None, ge=1, description='Количество записей')
    offset: int = Field(default=0, ge=0, description='Смещение')


@lru_cache()
def get_repository() -> OrderRepository:
    return OrderRepository()


def get_service(
        repository: Annotated[OrderRepository, Depends(get_repository)],
        settings: Annotated[Settings, Depends(get_settings)]
) -> OrderService:
    return OrderService(repository=repository, settings=settings)


def pagination_params(
    limit: int | None = Query(default=None, ge=1, description='Количество записей'),
    offset: int = Query(default=0, ge=0, description='Смещение'),
) -> PaginationParams:
    return PaginationParams(limit=limit, offset=offset)


SettingsDep = Annotated[Settings, Depends(get_settings)]
ServiceDep = Annotated[OrderService, Depends(get_service)]
PaginationDep = Annotated[PaginationParams, Depends(pagination_params)]
