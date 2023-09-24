import time
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from src.router import router as events_router
from src.service import init_events_data


@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa
    await init_events_data()
    yield


app = FastAPI(lifespan=lifespan)  # noqa

origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


app.include_router(events_router)

if __name__ == '__main__':
    uvicorn.run(app=app, host="0.0.0.0", port=80)
