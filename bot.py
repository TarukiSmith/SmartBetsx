from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
import requests
import random
import string

# -------------------------
# Vendos token, wallet dhe VIP link këtu
TOKEN = "8751046417:AAG7TCj1svd_w64Jb0ngX2a_JzIHxy4iTv8"
WALLET = "TWSHHQ8g3GgnyGpQaQn3dXkC3xtjVatkyR"
VIP_BASE_LINK = "https://t.me/+aAfAGSsKDRgzOGUx"
USDT_AMOUNT = 5
# -------------------------

ASK_NAME, ASK_COUNTRY, WAIT_PAYMENT = range(3)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Welcome! Write your nickname:")
    return ASK_NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['name'] = update.message.text
    await update.message.reply_text("🌍 Write your country:")
    return ASK_COUNTRY

async def get_country(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['country'] = update.message.text
    name = context.user_data['name']

    await update.message.reply_text(
        f"✅ Hello {name} from {context.user_data['country']}!\n\n"
        f"💰 Send {USDT_AMOUNT} USDT (TRC20) to:\n{WALLET}\n\n"
        "After payment, send the TX ID here."
    )
    return WAIT_PAYMENT

def verify_trc20_tx(tx_id):
    url = f"https://apilist.tronscan.org/api/transaction-info?hash={tx_id}"
    try:
        r = requests.get(url, timeout=10)
        data = r.json()
        if data.get("ret") and len(data["ret"]) > 0:
            return True
        return False
    except:
        return False

async def handle_tx(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tx_id = update.message.text.strip()

    if verify_trc20_tx(tx_id):
        unique_code = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
        vip_link = f"{VIP_BASE_LINK}?start={unique_code}"

        await update.message.reply_text(
            f"🎉 Payment confirmed!\n\nJoin VIP:\n{vip_link}"
        )
    else:
        await update.message.reply_text(
            "❌ Payment not verified. Check TX ID and try again."
        )

    return ConversationHandler.END

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ASK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            ASK_COUNTRY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_country)],
            WAIT_PAYMENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_tx)],
        },
        fallbacks=[]
    )

    app.add_handler(conv)

    print("Bot running... 🚀")
    app.run_polling()
