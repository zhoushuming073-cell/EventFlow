from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import settings
from app.routers import auth, cards, events, spaces


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时校验生产配置，缺失关键 secret 直接阻止启动
    settings.validate_production()
    yield


app = FastAPI(
    title="EventFlow API",
    description="极简事件记录器后端服务",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(auth.router)
app.include_router(spaces.router)
app.include_router(cards.router)
app.include_router(events.router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
