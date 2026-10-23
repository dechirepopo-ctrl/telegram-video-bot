import os
import logging
import yt_dlp
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

logging.basicConfig(level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! Send me any video link (YouTube, TikTok, Instagram) and I will download it for you.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    url = update.message.text.strip()
    if not url.startswith("http"):
        return

    # تنظيف الرابط من معاملات التتبع
    if "?" in url:
        url = url.split("?")[0]

    status_msg = await update.message.reply_text("⏳ Downloading video, please wait...")

    output_filename = f"video_{update.message.chat_id}.mp4"

    # خيارات متقدمة لتجاوز حماية إنستغرام وتيك توك
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': output_filename,
        'quiet': True,
        'no_warnings': True,
        'check_formats': False,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'referer': 'https://www.instagram.com/',
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
            
        if os.path.exists(output_filename):
            with open(output_filename, "rb") as f:
                await update.message.reply_video(video=f)
            os.remove(output_filename)
            await status_msg.delete()
        else:
            await status_msg.edit_text("❌ Could not find or process the video.")
            
    except Exception as e:
        logging.error(f"Download Error: {e}")
        # مسح أي ملف مؤقت في حال الفشل
        if os.path.exists(output_filename):
            os.remove(output_filename)
        await status_msg.edit_text("❌ Failed to download this video. Try a YouTube or TikTok link instead!")

if __name__ == "__main__":
    TOKEN = "8958964646:AAfv2W0zGBiWLbMlAhT7z-A3sG7d2FXukQo"
    
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    app.run_polling()
