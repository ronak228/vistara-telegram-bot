import os
import uuid
import asyncio
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("TOKEN")

user_state = {}

keyboard = [
    ["⭐ Activate Star"],
    ["📊 My Stars"],
    ["ℹ️ Help"]
]

reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


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
            "Press Activate Star, enter email, enter order ID, then upload screenshot."
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


async def main():

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT, handle_text))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    print("Bot started...")

    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    await app.idle()


if __name__ == "__main__":
    asyncio.run(main())