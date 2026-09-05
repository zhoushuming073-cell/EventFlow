from fastapi import FastAPI

from app.routers import auth, cards, events, spaces

app = FastAPI(
    title="EventFlow API",
    description="极简事件记录器后端服务",
    version="0.1.0",
)

app.include_router(auth.router)
app.include_router(spaces.router)
app.include_router(cards.router)
app.include_router(events.router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
