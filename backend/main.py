from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.upload_routes import router as upload_router
from api.routes import router

app = FastAPI(
    title="LeadForge AI"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
app.include_router(upload_router)
