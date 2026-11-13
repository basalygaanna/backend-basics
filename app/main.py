from fastapi import FastAPI

from app.routers.orders import router

app = FastAPI(title="Orders API")
app.include_router(router)
