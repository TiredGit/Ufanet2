import logging
import uvicorn
import asyncio
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager

from storage import get_events
from kafka_consumer import consume

from typing import Optional


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Kafka consumer task")
    task = asyncio.create_task(consume())
    yield
    task.cancel()
    logger.info("Stopping Kafka consumer task")


app = FastAPI(lifespan=lifespan)
templates = Jinja2Templates(directory="templates")
templates.env.trim_blocks = True
templates.env.lstrip_blocks = True
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def get_event_list(request: Request, selected: Optional[str] = None):
    return templates.TemplateResponse("index.html", {"request": request, "events": get_events(selected)})



if __name__ == '__main__':
    uvicorn.run("main:app", port=8001, reload=True)