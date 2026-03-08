from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = "8788128784:AAHWpOnlnOfKE_RR-VHxZ5ky8iIJYsav9ck"

# temporary memory to store user states
user_state = {}

main_keyboard = [
    ["⭐ Activate Star"],
    ["📊 My Stars"],
    ["ℹ️ Help"]
]

reply_markup = ReplyKeyboardMarkup(main_keyboard, resize_keyboard=True)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_message = """
Welcome to Vistara Little Stars ⭐

Earn stars for every Vistara purchase and unlock rewards for your kids 🎁
"""
    await update.message.reply_text(welcome_message, reply_markup=reply_markup)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text

    # STEP 1: user pressed Activate Star
    if text == "⭐ Activate Star":
        user_state[user_id] = "waiting_email"
        await update.message.reply_text(
            "Please enter your email address to continue."
        )
        return

    # STEP 2: user enters email
    if user_state.get(user_id) == "waiting_email":
        user_state[user_id] = "waiting_order"
        context.user_data["email"] = text

        await update.message.reply_text(
            "Thank you. Now please enter your Order ID."
        )
        return

    # STEP 3: user enters order ID
    if user_state.get(user_id) == "waiting_order":
        user_state[user_id] = "waiting_screenshot"
        context.user_data["order_id"] = text

        await update.message.reply_text(
            "Great. Please upload the screenshot of your purchase."
        )
        return

    if text == "📊 My Stars":
        await update.message.reply_text(
            "Your star balance will appear here after database integration."
        )
        return

    if text == "ℹ️ Help":
        await update.message.reply_text(
            """
Steps to earn stars ⭐

1. Press Activate Star
2. Enter your email
3. Enter your order ID
4. Upload purchase screenshot
"""
        )
        return

    await update.message.reply_text(
        "Please use the buttons below.",
        reply_markup=reply_markup
    )


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    if user_state.get(user_id) == "waiting_screenshot":
        photo_file = await update.message.photo[-1].get_file()
        await photo_file.download_to_drive("purchase_proof.jpg")

        email = context.user_data.get("email")
        order_id = context.user_data.get("order_id")

        await update.message.reply_text(
            f"Submission received ✅\n\nEmail: {email}\nOrder ID: {order_id}\n\nVerification pending."
        )

        user_state[user_id] = None


app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT, handle_message))
app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

print("Bot is running...")

app.run_polling()