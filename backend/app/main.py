from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.auth import router as auth_router
from app.api.activate import router as activate_router
from app.api.profile import router as profile_router
from app.api.websocket import router as websocket_router
from app.db.database import Base, engine
from app.db.init_db import seed


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    seed()
    yield


app = FastAPI(title="Proxy Service", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(activate_router)
app.include_router(profile_router)
app.include_router(websocket_router)


@app.get("/")
def root():
    return {"status": "ok"}