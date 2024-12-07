import os
import html
import json
import uuid
from typing import Dict

from telegram import (
    InlineQueryResultArticle,
    InputTextMessageContent,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update
)
from telegram.ext import (
    ApplicationBuilder,
    InlineQueryHandler,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
)
from telegram.constants import ParseMode

# File to store messages
MESSAGES_FILE = 'messages.json'

# In-memory store to keep track of secret messages
# Format: {unique_id: {"message": str, "target_username": str}}
SECRET_MESSAGES: Dict[str, Dict[str, str]] = {}

def load_messages():
    if os.path.exists(MESSAGES_FILE):
        with open(MESSAGES_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Ensure keys are strings and values are dicts
            if isinstance(data, dict):
                return data
    return {}

def save_messages():
    with open(MESSAGES_FILE, 'w', encoding='utf-8') as f:
        json.dump(SECRET_MESSAGES, f, ensure_ascii=False, indent=2)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Simple /start command handler."""
    await update.message.reply_text("Hi! I'm a whisper bot. Use inline mode in group chats.")

async def inline_query_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle inline queries. User should type something like: @YourBotName hello @username"""
    query = update.inline_query.query.strip()
    if not query:
        return

    # Attempt to parse out the target username.
    # We'll assume the last word that starts with '@' is the target.
    words = query.split()
    target_username = None
    for w in reversed(words):
        if w.startswith('@'):
            target_username = w
            break

    if target_username is None:
        # If no target username found, just show a message that instructs how to use.
        results = [
            InlineQueryResultArticle(
                id=str(uuid.uuid4()),
                title="How to whisper",
                input_message_content=InputTextMessageContent(
                    "Please mention a user with '@username' at the end of your message."
                )
            )
        ]
        await update.inline_query.answer(results=results, cache_time=0)
        return

    # Extract the secret message (everything except the target username)
    if words[-1] == target_username:
        message_parts = words[:-1]
    else:
        # find last occurrence of target_username and remove it
        idx = len(words) - 1 - words[::-1].index(target_username)
        message_parts = words[:idx] + words[idx+1:]
    secret_message = " ".join(message_parts).strip()

    if not secret_message:
        # If there's no secret message, prompt user.
        results = [
            InlineQueryResultArticle(
                id=str(uuid.uuid4()),
                title="No message provided",
                input_message_content=InputTextMessageContent(
                    "Please provide a message before the @username."
                )
            )
        ]
        await update.inline_query.answer(results=results, cache_time=0)
        return

    # Create a unique ID to store the message
    unique_id = str(uuid.uuid4())
    SECRET_MESSAGES[unique_id] = {
        "message": secret_message,
        "target_username": target_username.lower().strip('@')
    }

    # Save to file
    save_messages()

    # Display a "locked" message with a button
    # The initial message visible to everyone: a "🔒 whisper message"
    # The button will reveal the secret message to non-target users or show "соси" to the target user.
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Reveal", callback_data=unique_id)]
    ])

    results = [
        InlineQueryResultArticle(
            id=unique_id,
            title="Whisper",
            description="Send a private whisper message",
            input_message_content=InputTextMessageContent(
                f"🔒 A whisper message to everyone except @{target_username.strip('@')}."
            ),
            reply_markup=keyboard
        )
    ]

    await update.inline_query.answer(results=results, cache_time=0)


async def callback_query_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button presses."""
    query = update.callback_query
    user = query.from_user
    data = query.data

    if data not in SECRET_MESSAGES:
        await query.answer("Message not found.", show_alert=True)
        return

    secret_info = SECRET_MESSAGES[data]
    secret_message = secret_info["message"]
    target_username = secret_info["target_username"]

    if user.username and user.username.lower() == target_username:
        # Target user sees a private popup "соси" just for them
        await query.answer("соси", show_alert=False)
    else:
        # Non-target users see the secret message publicly (edit the chat message)
        await query.answer(secret_message, show_alert=True)


def main():
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN environment variable not set.")

    # Load previously stored messages
    global SECRET_MESSAGES
    SECRET_MESSAGES = load_messages()

    application = ApplicationBuilder().token(token).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(InlineQueryHandler(inline_query_handler))
    application.add_handler(CallbackQueryHandler(callback_query_handler))

    application.run_polling()


if __name__ == "__main__":
    main()
