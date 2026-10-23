import os
import yt_dlp
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "مرحباً بك! 🎬\n\nأرسل لي أي رابط فيديو (يوتيوب، تيك توك، إنستغرام) وسأقوم بتحميله لك فوراً."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    if not url.startswith("http"):
        return

    status_msg = await update.message.reply_text("⏳ جاري التحميل...")

    ydl_opts = {
        'format': 'best',
        'outtmpl': 'video.mp4',
        'quiet': True,
        'no_warnings': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
            
        if os.path.exists("video.mp4"):
            with open("video.mp4", "rb") as f:
                await update.message.reply_video(f)
            os.remove("video.mp4")
        else:
            await update.message.reply_text("❌ لم نتمكن من العثور على الفيديو.")
            
        await status_msg.delete()
    except Exception as e:
        await status_msg.edit_text("❌ حدث خطأ أثناء تحميل الفيديو.")

if __name__ == "__main__":
    import os
    TOKEN = os.getenv("TELEGRAM_TOKEN") # أو ضع التوكن مباشرة هنا بين علامتي تنصيص
    app = ApplicationBuilder().token("ضع_توكن_البوت_هنا").build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    app.add_handler(MessageHandler(filters.COMMAND, start))
    app.run_polling()
