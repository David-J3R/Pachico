import asyncio
import logging

from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from App.config import config
from App.service import invoke_agent

logger = logging.getLogger(__name__)

MAX_MESSAGE_LENGTH = 4096


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message:
        await update.message.reply_text(
            "Hey! I'm Pachico, your personal nutrition assistant.\n\n"
            "Tell me what you ate, ask for charts, or export your food log.\n"
            "Type /help for examples."
        )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message:
        await update.message.reply_text(
            "Here's what I can do:\n\n"
            'Log food: "I had 2 eggs and toast for breakfast"\n'
            'Review data: "How many calories did I eat today?"\n'
            'Charts: "Show me a calorie chart for this week"\n'
            'Export: "Export my food log as CSV"\n'
        )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message is None or update.effective_chat is None:
        return  # Ignore non-message updates
    text = update.message.text
    chat_id = update.effective_chat.id

    # Start a typing indicator that refreshes every 4 seconds
    # This lets the user know the bot is working on a response, especially for longer operations.
    # Visual example: Pachico is typing...
    stop_typing = (
        asyncio.Event()
    )  # Create an event to signal when to stop the typing indicator

    async def typing_loop() -> None:
        while not stop_typing.is_set():
            try:
                await context.bot.send_chat_action(
                    chat_id=chat_id, action=ChatAction.TYPING
                )
            except Exception:
                pass
            try:
                await asyncio.wait_for(stop_typing.wait(), timeout=4.0)
            except asyncio.TimeoutError:
                continue

    typing_task = asyncio.create_task(typing_loop())

    try:
        response = await asyncio.to_thread(invoke_agent, text, str(chat_id))

        # Send file attachments
        for path in response.file_paths:
            if path.endswith(".png"):
                await update.message.reply_photo(photo=open(path, "rb"))
            elif path.endswith(".csv"):
                await update.message.reply_document(document=open(path, "rb"))

        # Send text response, chunked if needed
        reply_text = response.text
        if reply_text:
            for i in range(0, len(reply_text), MAX_MESSAGE_LENGTH):
                await update.message.reply_text(reply_text[i : i + MAX_MESSAGE_LENGTH])

    except Exception:
        logger.exception("Error handling message")
        await update.message.reply_text(
            "Sorry, something went wrong. Please try again."
        )
    finally:
        stop_typing.set()
        await typing_task


def create_telegram_app() -> Application:
    """Build and return the Telegram Application (does not start polling)."""
    app = Application.builder().token(config.TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    return app
