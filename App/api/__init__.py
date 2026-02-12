import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from App.bot.telegram_bot import create_telegram_app

from .routes import router

logger = logging.getLogger(__name__)


# turn on and shut down telegram bot when the API server starts and stops, respectively
@asynccontextmanager
async def lifespan(app: FastAPI):
    telegram_app = create_telegram_app()
    await telegram_app.initialize()
    await telegram_app.start()
    await telegram_app.updater.start_polling(drop_pending_updates=True)
    logger.info("Telegram bot started polling")
    yield
    await telegram_app.updater.stop()
    await telegram_app.stop()
    await telegram_app.shutdown()
    logger.info("Telegram bot stopped")


app = FastAPI(title="Pachico", lifespan=lifespan)
app.include_router(router)
