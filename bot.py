import os
import uuid
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("TOKEN")

# store user state temporarily
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

Use the menu below to begin.
"""
    await update.message.reply_text(text, reply_markup=reply_markup)


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    message = update.message.text

    if message == "⭐ Activate Star":
        user_state[user_id] = "email"
        await update.message.reply_text("Please enter your email address:")
        return

    if message == "📊 My Stars":
        await update.message.reply_text(
            "Your star balance will appear here after database integration."
        )
        return

    if message == "ℹ️ Help":
        help_text = """
Steps to earn stars ⭐

1. Press Activate Star
2. Enter your email
3. Enter your order ID
4. Upload your purchase screenshot
"""
        await update.message.reply_text(help_text)
        return

    # email step
    if user_state.get(user_id) == "email":
        if "@" not in message:
            await update.message.reply_text("Please enter a valid email address.")
            return

        context.user_data["email"] = message
        user_state[user_id] = "order"

        await update.message.reply_text("Now enter your Order ID:")
        return

    # order id step
    if user_state.get(user_id) == "order":
        context.user_data["order_id"] = message
        user_state[user_id] = "screenshot"

        await update.message.reply_text("Please upload the screenshot of your order.")
        return

    await update.message.reply_text("Please use the buttons below.", reply_markup=reply_markup)


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    if user_state.get(user_id) != "screenshot":
        return

    photo = update.message.photo[-1]
    file = await photo.get_file()

    file_name = f"screenshot_{uuid.uuid4()}.jpg"
    await file.download_to_drive(file_name)

    email = context.user_data.get("email")
    order_id = context.user_data.get("order_id")

    await update.message.reply_text(
        f"""Submission received ✅

Email: {email}
Order ID: {order_id}

Verification pending."""
    )

    user_state[user_id] = None


def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT, handle_text))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    print("Bot started...")
    app.run_polling()


if __name__ == "__main__":
    main()