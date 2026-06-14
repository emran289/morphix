import logging
import requests
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
HF_TOKEN = os.environ.get("HF_TOKEN")

logging.basicConfig(level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! 🎨 عکست رو بفرست!")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⏳ دارم پردازش میکنم...")
    
    photo = update.message.photo[-1]
    file = await context.bot.get_file(photo.file_id)
    img_bytes = requests.get(file.file_path).content

    API_URL = "https://api-inference.huggingface.co/models/microsoft/resnet-50"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    
    resp = requests.post(API_URL, headers=headers, data=img_bytes, timeout=30)
    
    if resp.status_code == 200:
        result = resp.json()
        label = result[0]["label"] if result else "unknown"
        
        GEN_URL = "https://api-inference.huggingface.co/models/openskyml/dalle-3-xl"
        prompt = f"{label} in simpsons cartoon style, yellow skin"
        gen_resp = requests.post(GEN_URL, headers=headers, json={"inputs": prompt}, timeout=60)
        
        if gen_resp.status_code == 200:
            await update.message.reply_photo(photo=gen_resp.content)
        else:
            await update.message.reply_text(f"خطا در ساخت عکس: {gen_resp.status_code}")
    else:
        await update.message.reply_text(f"خطا: {resp.status_code}")

app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
app.run_polling()
