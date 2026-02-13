import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from App.bot.telegram_bot import create_telegram_app

from .routes import router

logger = logging.getLogger(__name__)


# turn on and shut down telegram bot when the API server starts and stops, respectively
@asynccontextmanager
async def lifespan(app: FastAPI):
    telegram_app = create_telegram_app()
    await telegram_app.initialize()
    await telegram_app.start()

    if telegram_app.updater is None:
        logger.error("Telegram bot updater is not initialized")
        raise RuntimeError("Telegram bot updater is not initialized")

    await telegram_app.updater.start_polling(drop_pending_updates=True)
    logger.info("Telegram bot started polling")
    yield
    await telegram_app.updater.stop()
    await telegram_app.stop()
    await telegram_app.shutdown()
    logger.info("Telegram bot stopped")


app = FastAPI(title="Pachico", lifespan=lifespan)

CORS_ORIGINS = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:3000,http://localhost:3001,http://localhost:3002",
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

os.makedirs("exports", exist_ok=True)
app.mount("/exports", StaticFiles(directory="exports"), name="exports")
