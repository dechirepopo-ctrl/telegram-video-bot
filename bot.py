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

    if "instagram.com" in url and "?" in url:
        url = url.split("?")[0]

    status_msg = await update.message.reply_text("Downloading video, please wait...")

    output_filename = f"video_{update.message.chat_id}.mp4"

    ydl_opts = {
        'format': 'best',
        'outtmpl': output_filename,
        'quiet': True,
        'no_warnings': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
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
            await status_msg.edit_text("Could not find the video.")
            
    except Exception as e:
        logging.error(f"Error: {e}")
        await status_msg.edit_text("An error occurred while downloading.")

if __name__ == "__main__":
    TOKEN = "8958964646:AAfv2W0zGBiWLbMlAhT7z-A3sG7d2FXukQo"
    
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    app.run_polling()
