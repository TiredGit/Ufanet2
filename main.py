"""
main.py — Основной файл запуска FastAPI-приложения
"""
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
"""Логгер сообщений"""


@asynccontextmanager
async def lifespan(app: FastAPI):
    """асинхронный контекстный менеджер, запускающий `consume()` из `kafka_consumer` при старте приложения и останавливающий его при завершении"""
    logger.info("Starting Kafka consumer task")
    task = asyncio.create_task(consume())
    try:
        yield
    finally:
        task.cancel()
        try:
            await asyncio.wait_for(task, timeout=3)
        except asyncio.TimeoutError:
            logger.error("Consumer task didn't stop in time")
        except Exception as e:
            logger.error(f"Unexpected error during shutdown: {e}")
        finally:
            logger.info("Consumer task stopped")


app = FastAPI(lifespan=lifespan)
"""Запускаемое приложение"""
templates = Jinja2Templates(directory="templates")
"""Отображает HTML-шаблоны с использованием Jinja2"""
templates.env.trim_blocks = True
templates.env.lstrip_blocks = True
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def get_event_list(request: Request, selected: Optional[str] = None):
    """HTTP GET-обработчик корневого пути `/`, рендерит шаблон `index.html` с событиями"""
    return templates.TemplateResponse(request, "index.html", {"events": get_events(selected)})



if __name__ == '__main__':
    uvicorn.run("main:app", port=8001, reload=True, host='0.0.0.0')
