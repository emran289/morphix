import logging
import requests
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# توکن‌ها
TELEGRAM_TOKEN = "YOUR_TELEGRAM_TOKEN"
HF_TOKEN = "YOUR_HF_TOKEN"

logging.basicConfig(level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "سلام! 🎨\nعکست رو بفرست تا به سبک سیمپسون تبدیلش کنم!"
    )

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⏳ دارم عکست رو تبدیل میکنم...")
    
    photo = update.message.photo[-1]
    file = await context.bot.get_file(photo.file_id)
    
    img_bytes = requests.get(file.file_path).content
    
    API_URL = "https://api-inference.huggingface.co/models/nitrosocke/Ghibli-Diffusion"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    
    response = requests.post(
        API_URL,
        headers=headers,
        data=img_bytes,
        params={"prompt": "simpson cartoon style, yellow skin, animated"}
    )
    
    if response.status_code == 200:
        await update.message.reply_photo(photo=response.content, caption="✅ سبک سیمپسون!")
    else:
        await update.message.reply_text("❌ خطا، دوباره امتحان کن")

app = Application.builder().token(TELEGRAM_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

print("بات شروع به کار کرد...")
app.run_polling()