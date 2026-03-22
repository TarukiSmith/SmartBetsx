import random
import string
import asyncio
import aiohttp
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, filters,
    ContextTypes, ConversationHandler
)

# --- Të dhënat e tua ---
TOKEN = "8751046417:AAG7TCj1svd_w64Jb0ngX2a_JzIHxy4iTv8"
WALLET = "TWSHHQ8g3GgnyGpQaQn3dXkC3xtjVatkyR"
VIP_BASE_LINK = "https://t.me/+aAfAGSsKDRgzOGUx"
USDT_AMOUNT = 5

# Conversation states
ASK_NAME, ASK_COUNTRY, WAIT_PAYMENT = range(3)

# --- Handlers ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Welcome! Write your nickname:")
    return ASK_NAME

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Conversation cancelled.")
    return ConversationHandler.END

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['name'] = update.message.text.strip()
    await update.message.reply_text("🌍 Write your country:")
    return ASK_COUNTRY

async def get_country(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['country'] = update.message.text.strip()
    name = context.user_data['name']

    await update.message.reply_text(
        f"✅ Hello {name} from {context.user_data['country']}!\n\n"
        f"💰 Send {USDT_AMOUNT} USDT (TRC20) to:\n{WALLET}\n\n"
        "After payment, send the TX ID here."
    )
    return WAIT_PAYMENT

# Async TRC20 verification
async def verify_trc20_tx(tx_id: str) -> bool:
    url = f"https://apilist.tronscan.org/api/transaction-info?hash={tx_id}"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as resp:
                data = await resp.json()
                if data.get("ret") and len(data["ret"]) > 0:
                    return True
        return False
    except Exception as e:
        print(f"Error verifying TX: {e}")
        return False

async def handle_tx(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tx_id = update.message.text.strip()
    is_paid = await verify_trc20_tx(tx_id)

    if is_paid:
        unique_code = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        vip_link = f"{VIP_BASE_LINK}?start={unique_code}"

        await update.message.reply_text(
            f"🎉 Payment confirmed!\n\nJoin VIP:\n{vip_link}"
        )
    else:
        await update.message.reply_text(
            "❌ Payment not verified. Check TX ID and try again."
        )

    return ConversationHandler.END

# Error logging
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    print(f"Update {update} caused error: {context.error}")

# --- Main ---
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ASK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            ASK_COUNTRY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_country)],
            WAIT_PAYMENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_tx)],
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )

    app.add_handler(conv_handler)
    app.add_error_handler(error_handler)

    print("Bot running... 🚀")
    app.run_polling()

if __name__ == "__main__":
    main()
