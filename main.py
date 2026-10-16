import os
import threading
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, ContextTypes, CallbackQueryHandler
)

TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "0"))

app = Flask(__name__)

@app.route("/")
def home():
    return "Nahid Coin Bot is running!"

coins = {
    "100 Coins": 20,
    "500 Coins": 90,
    "1000 Coins": 170
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton(f"{name} — ৳{price}", callback_data=name)]
        for name, price in coins.items()
    ]
    await update.message.reply_text(
        "🪙 Welcome to Nahid Coin Bot!\n\nChoose your coin package:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def choose_coin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    name = query.data
    await query.message.reply_text(
        f"📦 Package: {name}\n"
        f"💰 Price: ৳{coins[name]}\n\n"
        "অর্ডার করতে অ্যাডমিনের সঙ্গে যোগাযোগ করো।"
    )

async def setprice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("⛔ Admin only!")
        return

    if len(context.args) != 2:
        await update.message.reply_text(
            "ব্যবহার: /setprice 100 25"
        )
        return

    try:
        amount = int(context.args[0])
        price = int(context.args[1])
        if amount <= 0 or price < 0:
            raise ValueError
        coins[f"{amount} Coins"] = price
        await update.message.reply_text(
            f"✅ {amount} Coins-এর নতুন দাম ৳{price}"
        )
    except ValueError:
        await update.message.reply_text(
            "সঠিকভাবে লিখো: /setprice 100 25"
        )

async def main():
    bot = Application.builder().token(TOKEN).build()
    bot.add_handler(CommandHandler("start", start))
    bot.add_handler(CommandHandler("setprice", setprice))
    bot.add_handler(CallbackQueryHandler(choose_coin))
    await bot.initialize()
    await bot.start()
    await bot.updater.start_polling()
    await bot.updater.idle()

def run_bot():
    import asyncio
    asyncio.run(main())

if __name__ == "__main__":
    threading.Thread(target=run_bot, daemon=True).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
