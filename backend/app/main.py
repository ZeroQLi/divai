from .config import settings
from .database import init_db, seed_from_csv
from .routers import submit, applications, applicants
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

@app.on_event("startup")
def on_startup():
    init_db()
    seed_from_csv()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.cors_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(submit.router, prefix="/api")
app.include_router(applications.router, prefix="/api")
app.include_router(applicants.router, prefix="/api")
