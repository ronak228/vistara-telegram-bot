import os
import uuid
import asyncio
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("TOKEN")
PORT = int(os.environ.get("PORT", 10000))

user_state = {}

keyboard = [
    ["⭐ Activate Star"],
    ["📊 My Stars"],
    ["ℹ️ Help"]
]

reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running")

    def do_HEAD(self):
        self.send_response(200)
        self.end_headers()


def run_web_server():
    server = HTTPServer(("0.0.0.0", PORT), HealthHandler)
    server.serve_forever()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """
Welcome to Vistara Little Stars ⭐

Earn stars for every Vistara purchase and unlock rewards for your kids 🎁
"""
    await update.message.reply_text(text, reply_markup=reply_markup)


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.message.from_user.id
    text = update.message.text

    if text == "⭐ Activate Star":
        user_state[user_id] = "email"
        await update.message.reply_text("Enter your email address")
        return

    if text == "📊 My Stars":
        await update.message.reply_text("Your star balance will appear here.")
        return

    if text == "ℹ️ Help":
        await update.message.reply_text(
            "Press Activate Star → Enter email → Enter order ID → Upload screenshot."
        )
        return

    if user_state.get(user_id) == "email":
        context.user_data["email"] = text
        user_state[user_id] = "order"
        await update.message.reply_text("Enter your Order ID")
        return

    if user_state.get(user_id) == "order":
        context.user_data["order_id"] = text
        user_state[user_id] = "screenshot"
        await update.message.reply_text("Upload your order screenshot")
        return


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.message.from_user.id

    if user_state.get(user_id) != "screenshot":
        return

    photo = update.message.photo[-1]
    file = await photo.get_file()

    filename = f"order_{uuid.uuid4()}.jpg"
    await file.download_to_drive(filename)

    email = context.user_data.get("email")
    order_id = context.user_data.get("order_id")

    await update.message.reply_text(
        f"Submission received ✅\n\nEmail: {email}\nOrder ID: {order_id}\nVerification pending."
    )

    user_state[user_id] = None


def main():

    # start small web server (needed for Render)
    threading.Thread(target=run_web_server).start()

    # create asyncio event loop manually (Python 3.14 fix)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT, handle_text))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    print("Bot started...")

    app.run_polling()


if __name__ == "__main__":
    main()