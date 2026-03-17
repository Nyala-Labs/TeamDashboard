"""Nyala Labs Team Dashboard API."""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import init_db
from app.api import tasks, teams, users, events, meetings, recognition, timeline


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup/shutdown lifecycle."""
    await init_db()
    yield
    # shutdown: close connections etc.


app = FastAPI(
    title=settings.app_name,
    description="Team dashboard for Nyala Labs: tasks, recognition, timeline, meetings.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(teams.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(tasks.router, prefix="/api")
app.include_router(events.router, prefix="/api")
app.include_router(meetings.router, prefix="/api")
app.include_router(recognition.router, prefix="/api")
app.include_router(timeline.router, prefix="/api")


@app.get("/health")
def health():
    return {"status": "ok"}
