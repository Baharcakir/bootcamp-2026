from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .db import init_db
from .routers import analysis, coach, exams, students, tutor


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="Çarpan API",
    description="TYT Matematik netini yükselten yapay zeka koçu — netlerinin çarpanı",
    version="0.1.0",
    lifespan=lifespan,
)

# MVP: arayüz ayrı porttan konuştuğu için CORS açık; canlıya alırken daraltılacak (D4).
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)

app.include_router(students.router)
app.include_router(exams.router)
app.include_router(tutor.router)
app.include_router(analysis.router)
app.include_router(coach.router)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
