import os
import uvicorn
import yaml
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, Response

from src.app.home.api import router as home_router

app = FastAPI(
    title="Conflow API",
    description="Conflow API",
    version="0.1.0",
)

app.include_router(home_router)

if __name__ == "__main__":
     uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
