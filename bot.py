import os
import logging
import yt_dlp
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

# إعداد التسجيل للتحقق من أي أخطاء
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# دالة الاستجابة للأمر /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "مرحباً بك! 🎬\n\nأرسل لي أي رابط فيديو (يوتيوب، تيك توك، إنستغرام) وسأقوم بتحميله لك فوراً."
    )

# دالة تحميل الفيديو ومعالجة الروابط
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    url = update.message.text.strip()
    if not url.startswith("http"):
        return

    # تنظيف رابط إنستغرام من رموز التتبع الإضافية
    if "instagram.com" in url and "?" in url:
        url = url.split("?")[0]

    status_msg = await update.message.reply_text("⏳ جاري تحميل الفيديو، يرجى الانتظار...")

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
            await status_msg.edit_text("❌ لم نتمكن من العثور على الفيديو.")
            
    except Exception as e:
        logging.error(f"Download Error: {e}")
        await status_msg.edit_text("❌ عذراً، حدث خطأ أثناء تحميل الفيديو. تأكد من صحة الرابط.")

if __name__ == "__main__":
    # استبدل النص التالي بتوكن البوت الخاص بك من BotFather
    TOKEN = "ضع_توكن_البوت_هنا"
    
    app = ApplicationBuilder().token(TOKEN).build()
    
    # ربط الأمر /start أولاً لضمان سرعة الاستجابة
    app.add_handler(CommandHandler("start", start))
    
    # ربط معالج النصوص والروابط
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    app.run_polling()
