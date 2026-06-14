import logging
import requests
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
HF_TOKEN = os.environ.get("HF_TOKEN")

logging.basicConfig(level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "سلام! 🎨 من Morphix هستم!\n\nعکست رو بفرست تا به سبک سیمپسون تبدیلش کنم!"
    )

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⏳ دارم پردازش میکنم، صبر کن...")
    
    photo = update.message.photo[-1]
    file = await context.bot.get_file(photo.file_id)
    img_bytes = requests.get(file.file_path).content

    API_URL = "https://api-inference.huggingface.co/models/Salesforce/blip-image-captioning-base"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    
    caption_resp = requests.post(API_URL, headers=headers, data=img_bytes)
    
    if caption_resp.status_code == 200:
        caption = caption_resp.json()[0].get("generated_text", "a person")
    else:
        caption = "a person"

    GEN_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2-1"
    prompt = f"{caption}, simpsons cartoon style, yellow skin, animated, matt groening style"
    
    gen_resp = requests.post(GEN_URL, headers=headers, json={"inputs": prompt})
    
    if gen_resp.status_code == 200:
        await update.message.reply_photo(photo=gen_resp.content, caption="✅ سبک سیمپسون!")
    else:
        await update.message.reply_text(f"❌ خطا: {gen_resp.status_code}")

app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
app.run_polling()
