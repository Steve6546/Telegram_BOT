
import os
import json
import telebot
from telebot import types
from dotenv import load_dotenv
import re
import asyncio
from ai_agent import smart_agent

# تحميل المتغيرات من ملف .env
load_dotenv()

# --- إعداد البوت ---
try:
    with open("config.json", "r", encoding='utf-8') as f:
        config = json.load(f)
    TELEGRAM_TOKEN = config["TELEGRAM_TOKEN"]
    if not TELEGRAM_TOKEN:
        raise ValueError("التوكين غير موجود في config.json")
except (FileNotFoundError, json.JSONDecodeError, KeyError, ValueError) as e:
    print(f"❌ خطأ في قراءة ملف config.json: {e}")
    exit(1)

bot = telebot.TeleBot(TELEGRAM_TOKEN)

# تخزين حالة المستخدمين المتطورة
user_states = {}
user_preferences = {}

# --- وظائف مساعدة ---
def extract_url(text):
    """استخراج رابط من النص"""
    url_patterns = [
        r'https?://(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/|vimeo\.com/|twitter\.com/|x\.com/|instagram\.com/|tiktok\.com/)[^\s]+',
        r'https?://[^\s]+'
    ]
    
    for pattern in url_patterns:
        urls = re.findall(pattern, text)
        if urls:
            return urls[0]
    return None

def create_main_menu():
    """إنشاء القائمة الرئيسية المتطورة"""
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    
    # خيارات التنزيل الأساسية
    btn_download = types.InlineKeyboardButton("📹 تحميل فيديو", callback_data="mode_download")
    btn_info = types.InlineKeyboardButton("ℹ️ معلومات الوسائط", callback_data="mode_info")
    
    # خيارات المعالجة المتقدمة  
    btn_convert = types.InlineKeyboardButton("🔄 تحويل الملفات", callback_data="mode_convert")
    btn_edit = types.InlineKeyboardButton("✂️ تحرير الفيديو", callback_data="mode_edit")
    
    # خيارات إضافية
    btn_image = types.InlineKeyboardButton("🖼️ معالجة الصور", callback_data="mode_image")
    btn_zip = types.InlineKeyboardButton("📦 ضغط الملفات", callback_data="mode_zip")
    
    # خيارات النظام
    btn_tools = types.InlineKeyboardButton("🛠️ جميع الأدوات", callback_data="show_tools")
    btn_help = types.InlineKeyboardButton("❓ المساعدة", callback_data="show_help")
    
    keyboard.add(btn_download, btn_info)
    keyboard.add(btn_convert, btn_edit)
    keyboard.add(btn_image, btn_zip)
    keyboard.add(btn_tools, btn_help)
    
    return keyboard

def create_download_options():
    """إنشاء خيارات التحميل المتطورة"""
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    
    # جودات الفيديو
    btn_4k = types.InlineKeyboardButton("🎬 4K Ultra", callback_data="download_ultra")
    btn_hd = types.InlineKeyboardButton("📹 HD 1080p", callback_data="download_high")
    btn_sd = types.InlineKeyboardButton("📱 HD 720p", callback_data="download_medium")
    btn_low = types.InlineKeyboardButton("📺 SD 480p", callback_data="download_low")
    
    # خيارات الصوت
    btn_audio_high = types.InlineKeyboardButton("🎵 صوت عالي الجودة", callback_data="download_audio_high")
    btn_audio_normal = types.InlineKeyboardButton("🎶 صوت عادي", callback_data="download_audio_normal")
    
    # خيارات إضافية
    btn_info = types.InlineKeyboardButton("📊 معلومات تفصيلية", callback_data="get_detailed_info")
    btn_back = types.InlineKeyboardButton("⬅️ العودة", callback_data="back_to_main")
    
    keyboard.add(btn_4k, btn_hd)
    keyboard.add(btn_sd, btn_low)
    keyboard.add(btn_audio_high, btn_audio_normal)
    keyboard.add(btn_info, btn_back)
    
    return keyboard

def create_processing_options():
    """إنشاء خيارات المعالجة المتقدمة"""
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    
    # تحويل الصيغ
    btn_to_mp3 = types.InlineKeyboardButton("🎵 إلى MP3", callback_data="convert_mp3")
    btn_to_mp4 = types.InlineKeyboardButton("📹 إلى MP4", callback_data="convert_mp4")
    btn_to_wav = types.InlineKeyboardButton("🎼 إلى WAV", callback_data="convert_wav")
    btn_to_avi = types.InlineKeyboardButton("🎬 إلى AVI", callback_data="convert_avi")
    
    # عمليات التحرير
    btn_trim = types.InlineKeyboardButton("✂️ تقطيع", callback_data="edit_trim")
    btn_extract = types.InlineKeyboardButton("📤 استخراج جزء", callback_data="edit_extract")
    
    # ضغط ومعالجة
    btn_compress = types.InlineKeyboardButton("🗜️ ضغط الحجم", callback_data="process_compress")
    btn_enhance = types.InlineKeyboardButton("✨ تحسين الجودة", callback_data="process_enhance")
    
    btn_back = types.InlineKeyboardButton("⬅️ العودة", callback_data="back_to_main")
    
    keyboard.add(btn_to_mp3, btn_to_mp4)
    keyboard.add(btn_to_wav, btn_to_avi)
    keyboard.add(btn_trim, btn_extract)
    keyboard.add(btn_compress, btn_enhance)
    keyboard.add(btn_back)
    
    return keyboard

# --- الأوامر الأساسية ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    """رسالة ترحيبية متطورة"""
    welcome_text = """
🤖 **مرحباً بك في Smart Media AI Assistant!**

✨ أنا وكيل ذكاء اصطناعي متطور مدعوم بتقنيات LangChain

🎯 **ما يمكنني فعله:**
📹 تحميل فيديوهات بجودة 4K من أي منصة
🔄 تحويل بين جميع صيغ الوسائط
✂️ تحرير ومعالجة الفيديوهات
🖼️ معالجة وتحسين الصور
📦 ضغط وإدارة الملفات
🧠 فهم طلباتك والرد بذكاء

🚀 **ابدأ الآن:**
أرسل رابط أو اختر من القائمة أدناه
    """
    
    keyboard = create_main_menu()
    bot.send_message(message.chat.id, welcome_text, reply_markup=keyboard, parse_mode='Markdown')

@bot.message_handler(commands=['help'])
def send_help(message):
    """عرض المساعدة المتطورة"""
    help_text = smart_agent.get_available_tools_info()
    keyboard = create_main_menu()
    bot.send_message(message.chat.id, help_text, reply_markup=keyboard, parse_mode='Markdown')

@bot.message_handler(commands=['tools'])
def show_tools(message):
    """عرض جميع الأدوات المتاحة"""
    tools_info = smart_agent.get_available_tools_info()
    bot.send_message(message.chat.id, tools_info, parse_mode='Markdown')

@bot.message_handler(commands=['clear'])
def clear_memory(message):
    """مسح ذاكرة المحادثة"""
    user_id = message.from_user.id
    result = smart_agent.clear_memory()
    if user_id in user_states:
        del user_states[user_id]
    if user_id in user_preferences:
        del user_preferences[user_id]
    bot.send_message(message.chat.id, result)

# --- معالجة الأزرار التفاعلية ---
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    """معالجة جميع الأزرار التفاعلية"""
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    data = call.data
    
    bot.answer_callback_query(call.id)
    
    # القائمة الرئيسية
    if data == "back_to_main":
        keyboard = create_main_menu()
        bot.edit_message_text(
            "🏠 القائمة الرئيسية - اختر الخدمة المطلوبة:",
            chat_id=chat_id,
            message_id=call.message.message_id,
            reply_markup=keyboard
        )
        return
    
    # عرض الأدوات
    elif data == "show_tools":
        tools_info = smart_agent.get_available_tools_info()
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton("⬅️ العودة", callback_data="back_to_main"))
        bot.edit_message_text(
            tools_info,
            chat_id=chat_id,
            message_id=call.message.message_id,
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
        return
    
    # عرض المساعدة
    elif data == "show_help":
        help_text = """
🆘 **كيفية الاستخدام:**

1️⃣ **لتحميل فيديو:**
   أرسل الرابط مباشرة أو اضغط "📹 تحميل فيديو"

2️⃣ **للحصول على معلومات:**
   اضغط "ℹ️ معلومات الوسائط" بعد إرسال الرابط

3️⃣ **لتحويل الملفات:**
   اضغط "🔄 تحويل الملفات" واتبع التعليمات

4️⃣ **للتحرير المتقدم:**
   استخدم "✂️ تحرير الفيديو" للقص والتعديل

💡 **نصائح:**
- يمكنك الكتابة بلغة طبيعية وسأفهم طلبك
- جرب الأوامر: /tools, /clear, /help
- أدعم أكثر من 1000 منصة مختلفة

🤖 تذكر: أنا ذكاء اصطناعي متطور، تفاعل معي بحرية!
        """
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton("⬅️ العودة", callback_data="back_to_main"))
        bot.edit_message_text(
            help_text,
            chat_id=chat_id,
            message_id=call.message.message_id,
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
        return
    
    # معالجة أزرار التحميل
    elif data.startswith("download_"):
        if user_id not in user_states or 'url' not in user_states[user_id]:
            bot.send_message(chat_id, "❌ لم يتم اكتشاف رابط. أرسل رابط أولاً.")
            return
        
        url = user_states[user_id]['url']
        quality_map = {
            "download_ultra": ("ultra", "فيديو 4K"),
            "download_high": ("high", "فيديو HD 1080p"),
            "download_medium": ("medium", "فيديو HD 720p"),
            "download_low": ("low", "فيديو SD 480p"),
            "download_audio_high": ("audio_high", "صوت عالي الجودة"),
            "download_audio_normal": ("audio_normal", "صوت عادي")
        }
        
        if data in quality_map:
            quality, description = quality_map[data]
            bot.send_message(chat_id, f"⚡ جاري تحميل {description}...")
            
            # استخدام الذكاء الاصطناعي للتحميل
            if "audio" in quality:
                ai_response = smart_agent.process_message(
                    f"حمل الصوت من هذا الرابط بجودة عالية: {url}",
                    str(user_id)
                )
            else:
                ai_response = smart_agent.process_message(
                    f"حمل فيديو من هذا الرابط بجودة {quality}: {url}",
                    str(user_id)
                )
            
            bot.send_message(chat_id, ai_response)
    
    # معالجة أزرار التحويل
    elif data.startswith("convert_"):
        format_map = {
            "convert_mp3": "mp3",
            "convert_mp4": "mp4", 
            "convert_wav": "wav",
            "convert_avi": "avi"
        }
        
        if data in format_map:
            target_format = format_map[data]
            bot.send_message(chat_id, f"🔄 أرسل الملف المراد تحويله إلى {target_format.upper()}")
            user_states[user_id] = {'mode': 'convert', 'format': target_format}
    
    # معالجة أزرار أخرى...
    elif data == "mode_download":
        keyboard = create_download_options()
        bot.edit_message_text(
            "📹 اختر جودة التحميل المطلوبة:",
            chat_id=chat_id,
            message_id=call.message.message_id,
            reply_markup=keyboard
        )
    
    elif data == "mode_convert":
        keyboard = create_processing_options()
        bot.edit_message_text(
            "🔄 اختر نوع التحويل المطلوب:",
            chat_id=chat_id,
            message_id=call.message.message_id,
            reply_markup=keyboard
        )

# --- معالجة الرسائل النصية ---
@bot.message_handler(func=lambda message: True, content_types=['text'])
def handle_message(message):
    """معالجة الرسائل النصية باستخدام الذكاء الاصطناعي"""
    user_text = message.text
    user_id = message.from_user.id
    chat_id = message.chat.id
    
    if not user_text:
        bot.send_message(chat_id, "❌ لا أستطيع معالجة هذه الرسالة.")
        return

    # تحديث حالة المستخدم إذا لم تكن موجودة
    if user_id not in user_states:
        user_states[user_id] = {}

    # استخراج الرابط من النص
    url = extract_url(user_text)
    
    if url:
        # حفظ الرابط في حالة المستخدم
        user_states[user_id]['url'] = url
        
        # إرسال رسالة ترحيبية مع خيارات
        welcome_msg = f"""
🔗 **تم اكتشاف رابط!**

📊 جاري فحص الرابط وجلب المعلومات...
        """
        bot.send_message(chat_id, welcome_msg, parse_mode='Markdown')
        
        # استخدام الذكاء الاصطناعي لجلب المعلومات
        ai_response = smart_agent.process_message(
            f"احصل على معلومات تفصيلية عن هذا الرابط: {url}",
            str(user_id)
        )
        
        bot.send_message(chat_id, ai_response, parse_mode='Markdown')
        
        # عرض خيارات التحميل
        keyboard = create_download_options()
        bot.send_message(
            chat_id,
            "🎯 **اختر نوع العملية المطلوبة:**",
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
    else:
        # استخدام الذكاء الاصطناعي للرد
        bot.send_message(chat_id, "🤖 جاري فهم طلبك...")
        
        ai_response = smart_agent.process_message(user_text, str(user_id))
        
        # إرسال رد الذكاء الاصطناعي
        bot.send_message(chat_id, ai_response)
        
        # إضافة القائمة الرئيسية إذا كان الرد لا يحتوي على إجراءات
        if len(ai_response) < 200 and "❌" not in ai_response:
            keyboard = create_main_menu()
            bot.send_message(
                chat_id,
                "💡 **أو يمكنك استخدام القائمة التفاعلية:**",
                reply_markup=keyboard,
                parse_mode='Markdown'
            )

# --- معالجة الملفات المرسلة ---
@bot.message_handler(content_types=['document', 'video', 'audio', 'photo'])
def handle_file(message):
    """معالجة الملفات المرسلة"""
    user_id = message.from_user.id
    chat_id = message.chat.id
    
    file_info = None
    file_type = ""
    
    if message.document:
        file_info = bot.get_file(message.document.file_id)
        file_type = "مستند"
    elif message.video:
        file_info = bot.get_file(message.video.file_id)
        file_type = "فيديو"
    elif message.audio:
        file_info = bot.get_file(message.audio.file_id)
        file_type = "صوت"
    elif message.photo:
        file_info = bot.get_file(message.photo[-1].file_id)
        file_type = "صورة"
    
    if file_info:
        # تحميل الملف
        downloaded_file = bot.download_file(file_info.file_path)
        
        # حفظ الملف محلياً
        file_name = f"uploads/{file_info.file_path.split('/')[-1]}"
        os.makedirs("uploads", exist_ok=True)
        
        with open(file_name, 'wb') as new_file:
            new_file.write(downloaded_file)
        
        # استخدام الذكاء الاصطناعي لمعالجة الملف
        ai_response = smart_agent.process_message(
            f"تم رفع {file_type} جديد: {file_name}. ما العمليات المتاحة؟",
            str(user_id)
        )
        
        bot.reply_to(message, f"📁 تم استلام {file_type}!\n\n{ai_response}")
        
        # عرض خيارات المعالجة
        keyboard = create_processing_options()
        bot.send_message(
            chat_id,
            "🛠️ **خيارات المعالجة المتاحة:**",
            reply_markup=keyboard,
            parse_mode='Markdown'
        )

# --- تشغيل البوت ---
if __name__ == "__main__":
    print("🚀 تم تشغيل Smart Media AI Assistant Bot!")
    print("✨ نظام الذكاء الاصطناعي المتطور مع LangChain جاهز!")
    print("🛠️ جميع الأدوات محمّلة ومتاحة...")
    
    # إنشاء المجلدات المطلوبة
    os.makedirs("downloads", exist_ok=True)
    os.makedirs("uploads", exist_ok=True)
    os.makedirs("processed", exist_ok=True)
    
    try:
        bot.polling(non_stop=True)
    except Exception as e:
        print(f"❌ خطأ في تشغيل البوت: {e}")
