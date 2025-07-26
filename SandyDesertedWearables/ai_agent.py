
# ai_agent.py - وكيل الذكاء الاصطناعي المتطور
import os
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.memory import ConversationBufferWindowMemory
from tools import ALL_TOOLS
from dotenv import load_dotenv

load_dotenv()

class SmartMediaAIAgent:
    def __init__(self):
        # إعداد النموذج
        self.llm = ChatOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENROUTER_API_KEY"),
            model="microsoft/phi-3-mini-128k-instruct:free",
            temperature=0.7
        )
        
        # إعداد الذاكرة
        self.memory = ConversationBufferWindowMemory(
            memory_key="chat_history",
            return_messages=True,
            k=10  # حفظ آخر 10 رسائل
        )
        
        # قالب التعليمات
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", self._get_system_instructions()),
            ("placeholder", "{chat_history}"),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}")
        ])
        
        # إنشاء الوكيل
        self.agent = create_openai_tools_agent(
            llm=self.llm,
            tools=ALL_TOOLS,
            prompt=self.prompt
        )
        
        # منفذ الوكيل
        self.executor = AgentExecutor(
            agent=self.agent,
            tools=ALL_TOOLS,
            memory=self.memory,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=5
        )
    
    def _get_system_instructions(self):
        return """
أنت Smart Media AI Assistant - وكيل ذكاء اصطناعي محترف ومتطور في تيليجرام.

🎯 **مهمتك الأساسية:**
- مساعدة المستخدمين في تحميل وتحويل ومعالجة الوسائط
- التفاعل بطريقة ذكية وودية ومحترفة
- استخدام الأدوات المتاحة لتنفيذ طلبات المستخدمين

🛠️ **الأدوات المتاحة لك:**
1. advanced_video_downloader - تحميل فيديوهات بجودات مختلفة
2. advanced_video_info - استخراج معلومات تفصيلية عن الفيديوهات  
3. file_converter - تحويل بين صيغ مختلفة
4. image_processor - معالجة وتحويل الصور
5. zip_manager - ضغط وفك ضغط الملفات
6. video_editor - تقطيع وتحرير الفيديوهات

📋 **قواعد التفاعل:**
- ابدأ دائماً بفهم طلب المستخدم بدقة
- إذا كان هناك رابط، استخرج معلوماته أولاً
- اعرض خيارات واضحة للمستخدم (جودات، صيغ، إلخ)
- استخدم الإيموجي لجعل التفاعل أكثر حيوية
- قدم تحديثات عن حالة العمليات الجارية
- اشرح للمستخدم ما تفعله خطوة بخطوة

💡 **أمثلة للتفاعل:**

عند استلام رابط:
"🔍 جاري فحص الرابط وجلب المعلومات..."
[استخدم advanced_video_info]
"📊 تم العثور على الفيديو! اختر نوع التحميل:
🎬 فيديو - جودة عالية (1080p)
📱 فيديو - جودة متوسطة (720p) 
🎵 صوت فقط (MP3)
ℹ️ معلومات مفصلة"

عند طلب تحويل:
"🔄 جاري تحويل الملف إلى الصيغة المطلوبة..."
[استخدم file_converter]
"✅ تم التحويل بنجاح! الملف جاهز للتحميل."

🚨 **تعليمات مهمة:**
- لا تحاول تنفيذ عمليات بدون استخدام الأدوات المحددة
- إذا فشلت أداة، حاول طريقة بديلة أو اشرح السبب
- احرص على إعطاء ردود مفيدة حتى في حالة الأخطاء
- تذكر تفاصيل المحادثة واستخدم الذاكرة بذكاء

🎨 **أسلوب التواصل:**
- كن ودوداً ومتفاعلاً
- استخدم الإيموجي بشكل مناسب
- اكتب بوضوح وبساطة
- قدم خيارات واضحة للمستخدم
- اشرح العمليات التقنية بطريقة مبسطة
        """
    
    def process_message(self, user_message: str, user_id: str = None) -> str:
        """معالجة رسالة المستخدم وإرجاع الرد"""
        try:
            # إضافة معرف المستخدم للسياق إذا كان متاحاً
            context = f"[المستخدم {user_id}]: {user_message}" if user_id else user_message
            
            response = self.executor.invoke({
                "input": context
            })
            
            return response.get('output', 'عذراً، حدث خطأ في المعالجة.')
            
        except Exception as e:
            return f"❌ خطأ في معالجة الطلب: {str(e)[:100]}..."
    
    def get_available_tools_info(self) -> str:
        """إرجاع معلومات عن الأدوات المتاحة"""
        tools_info = """
🛠️ **الأدوات المتاحة في النظام:**

📹 **تحميل الفيديوهات المتطور**
- دعم جميع المنصات (YouTube, TikTok, Instagram, إلخ)
- جودات متعددة (4K, 1080p, 720p, 480p)
- تحميل الصوت بصيغ مختلفة

🔄 **تحويل الملفات**
- تحويل بين صيغ الفيديو والصوت
- دعم MP4, MP3, WAV, AVI, MOV
- تحسين الجودة والحجم

🖼️ **معالجة الصور**  
- تغيير الحجم والضغط
- تحويل بين الصيغ
- تحسين الجودة

📦 **إدارة الملفات المضغوطة**
- ضغط الملفات في ZIP
- فك الضغط
- دعم ملفات متعددة

✂️ **تحرير الفيديو**
- تقطيع الفيديوهات
- استخراج مقاطع محددة
- تحرير بسيط

📊 **معلومات تفصيلية**
- تحليل الوسائط
- إحصائيات متقدمة
- معاينة قبل التحميل
        """
        return tools_info
    
    def clear_memory(self):
        """مسح ذاكرة المحادثة"""
        self.memory.clear()
        return "🧹 تم مسح ذاكرة المحادثة."

# إنشاء مثيل وحيد من الوكيل
smart_agent = SmartMediaAIAgent()
