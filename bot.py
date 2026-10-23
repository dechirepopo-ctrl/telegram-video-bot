
import logging
import os
import yt_dlp
from telegram import Update
from telegram.ext import ContextTypes

# إعداد التسجيل لرؤية الأخطاء في Render Logs
logging.basicConfig(level=logging.INFO)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    url = update.message.text.strip()
    
    # التأكد من أن النص يبدأ برابط
    if not (url.startswith("http://") or url.startswith("https://")):
        return

    # تنظيف رابط إنستغرام من الاستعلامات الإضافية التي قد تسبب مشاكل
    if "instagram.com" in url and "?" in url:
        url = url.split("?")[0]

    status_msg = await update.message.reply_text("⏳ جاري جلب الفيديو...")

    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': 'downloaded_video.%(ext)s',
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True,
        # إضافة وكيل مستخدم لمنع الحظر
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        with open(filename, 'rb') as video_file:
            await update.message.reply_video(video=video_file)
            
        # حذف الفيديو المحفوظ بعد الإرسال لتوفير المساحة
        if os.path.exists(filename):
            os.remove(filename)
            
        await status_msg.delete()

    except Exception as e:
        logging.error(f"Error downloading video: {e}")
        await status_msg.edit_text(f"❌ لم نتمكن من العثور على الفيديو أو تنزيله.\nالتفاصيل: {str(e)[:100]}")
