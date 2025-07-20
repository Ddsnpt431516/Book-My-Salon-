import logging
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

logging.basicConfig(level=logging.INFO)

CITY, SALON, CONFIRM = range(3)

salon_data = {
    "परभणी": [
        {"name": "जनसेवा सलून", "phone": "9876543210"},
    ],
    "नांदेड": [
        {"name": "स्टाईल हेअर स्टुडिओ", "phone": "9123456789"},
    ],
    "हिंगोली": [
        {"name": "झकास हेअर स्टाईल", "phone": "9988776655"},
    ],
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        f"नमस्कार {user.first_name}! 🙏\n\nWelcome to *Book My Salon* 💇‍♂️💅\nकृपया तुमचे शहर निवडा:",
        reply_markup=ReplyKeyboardMarkup(
            [[KeyboardButton(city)] for city in salon_data.keys()],
            one_time_keyboard=True,
            resize_keyboard=True
        ),
    )
    return CITY

async def select_city(update: Update, context: ContextTypes.DEFAULT_TYPE):
    city = update.message.text
    context.user_data["city"] = city

    salons = salon_data.get(city, [])
    buttons = [[KeyboardButton(s["name"])] for s in salons]
    await update.message.reply_text(
        f"{city} मधील सलून निवडा:",
        reply_markup=ReplyKeyboardMarkup(buttons, one_time_keyboard=True, resize_keyboard=True)
    )
    return SALON

async def select_salon(update: Update, context: ContextTypes.DEFAULT_TYPE):
    salon = update.message.text
    context.user_data["salon"] = salon
    city = context.user_data["city"]

    phone = next((s["phone"] for s in salon_data[city] if s["name"] == salon), "N/A")
    context.user_data["phone"] = phone

    await update.message.reply_text(
        f"तुम्ही '{salon}' हे सलून बुक करू इच्छिता का?\nफोन: {phone}",
        reply_markup=ReplyKeyboardMarkup(
            [[KeyboardButton("हो"), KeyboardButton("नाही")]],
            one_time_keyboard=True,
            resize_keyboard=True
        )
    )
    return CONFIRM

async def confirm_booking(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "हो":
        salon = context.user_data["salon"]
        phone = context.user_data["phone"]
        await update.message.reply_text(
            f"✅ तुमचं '{salon}' सलूनचं बुकिंग झाले आहे!\n📞 कृपया संपर्क करा: {phone}"
        )
    else:
        await update.message.reply_text("❌ बुकिंग रद्द करण्यात आले आहे.")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🙏 धन्यवाद! भेट दिल्याबद्दल आभार.")
    return ConversationHandler.END

def main():
    import os
    TOKEN = os.getenv("BOT_TOKEN")  # Render किंवा GitHub साठी env variable वापर

    app = ApplicationBuilder().token(TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, select_city)],
            SALON: [MessageHandler(filters.TEXT & ~filters.COMMAND, select_salon)],
            CONFIRM: [MessageHandler(filters.TEXT & ~filters.COMMAND, confirm_booking)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv)
    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
