
# tools.py - الأدوات المتطورة للنظام
import os
import zipfile
import json
from typing import Dict, Any, Optional
from langchain.tools import BaseTool
from pydantic import BaseModel, Field
import yt_dlp
import moviepy.editor as mp
from PIL import Image
import requests
import subprocess

class VideoDownloadInput(BaseModel):
    url: str = Field(description="رابط الفيديو المراد تحميله")
    quality: str = Field(description="جودة التحميل: high, medium, low")
    format_type: str = Field(description="نوع الملف: video, audio")

class VideoInfoInput(BaseModel):
    url: str = Field(description="رابط الفيديو للحصول على معلوماته")

class FileConvertInput(BaseModel):
    file_path: str = Field(description="مسار الملف المراد تحويله")
    target_format: str = Field(description="الصيغة المطلوبة: mp3, mp4, wav, avi")

class ImageProcessInput(BaseModel):
    image_path: str = Field(description="مسار الصورة")
    operation: str = Field(description="العملية: resize, compress, convert")
    params: Dict[str, Any] = Field(description="معاملات العملية")

class ZipOperationInput(BaseModel):
    operation: str = Field(description="نوع العملية: create, extract")
    files: list = Field(description="قائمة الملفات")
    output_path: str = Field(description="مسار الإخراج")

# أداة تحميل الفيديو المتطورة
class AdvancedVideoDownloader(BaseTool):
    name = "advanced_video_downloader"
    description = "تحميل فيديوهات من أي منصة بجودات مختلفة وإعدادات متقدمة"
    args_schema = VideoDownloadInput
    
    def _run(self, url: str, quality: str = "high", format_type: str = "video") -> str:
        try:
            download_path = "downloads"
            os.makedirs(download_path, exist_ok=True)
            
            # تحديد إعدادات الجودة
            quality_settings = {
                "high": "best[height<=1080]",
                "medium": "best[height<=720]", 
                "low": "best[height<=480]",
                "ultra": "best[height<=2160]"
            }
            
            if format_type == "audio":
                format_selector = "bestaudio/best"
                outtmpl = f'{download_path}/%(title)s.%(ext)s'
                postprocessors = [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }]
            else:
                format_selector = quality_settings.get(quality, "best")
                outtmpl = f'{download_path}/%(title)s.%(ext)s'
                postprocessors = []
            
            ydl_opts = {
                'format': format_selector,
                'outtmpl': outtmpl,
                'postprocessors': postprocessors,
                'quiet': True,
                'no_warnings': True,
                'writeinfojson': True,
                'writesubtitles': True,
                'writeautomaticsub': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
                
            return f"✅ تم تحميل {format_type} بجودة {quality} بنجاح!"
            
        except Exception as e:
            return f"❌ خطأ في التحميل: {str(e)}"

# أداة معلومات الفيديو المتطورة
class AdvancedVideoInfo(BaseTool):
    name = "advanced_video_info"
    description = "استخراج معلومات تفصيلية عن الفيديو"
    args_schema = VideoInfoInput
    
    def _run(self, url: str) -> str:
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                title = info.get('title', 'غير متوفر')
                duration = info.get('duration', 0)
                uploader = info.get('uploader', 'غير متوفر')
                view_count = info.get('view_count', 0)
                like_count = info.get('like_count', 0)
                description = info.get('description', 'غير متوفر')[:200]
                upload_date = info.get('upload_date', 'غير متوفر')
                
                # استخراج الجودات المتاحة
                formats = info.get('formats', [])
                available_qualities = set()
                for fmt in formats:
                    if fmt.get('height'):
                        available_qualities.add(f"{fmt['height']}p")
                
                minutes = duration // 60
                seconds = duration % 60
                
                result = f"""
🎬 **معلومات الفيديو المتطورة:**
📝 العنوان: {title}
⏱️ المدة: {minutes}:{seconds:02d}
👤 القناة: {uploader}
👁️ المشاهدات: {view_count:,}
👍 الإعجابات: {like_count:,}
📅 تاريخ النشر: {upload_date}
🎯 الجودات المتاحة: {', '.join(sorted(available_qualities, reverse=True))}
📄 الوصف: {description}...
🔗 الرابط: {url}
                """
                return result
                
        except Exception as e:
            return f"❌ خطأ في جلب المعلومات: {str(e)}"

# أداة تحويل الملفات
class FileConverter(BaseTool):
    name = "file_converter"
    description = "تحويل الملفات بين صيغ مختلفة"
    args_schema = FileConvertInput
    
    def _run(self, file_path: str, target_format: str) -> str:
        try:
            if not os.path.exists(file_path):
                return "❌ الملف غير موجود"
            
            base_name = os.path.splitext(file_path)[0]
            output_path = f"{base_name}.{target_format}"
            
            # تحويل الفيديو/الصوت
            if target_format in ['mp3', 'wav', 'aac']:
                clip = mp.VideoFileClip(file_path)
                clip.audio.write_audiofile(output_path)
                clip.close()
            elif target_format in ['mp4', 'avi', 'mov']:
                clip = mp.VideoFileClip(file_path)
                clip.write_videofile(output_path)
                clip.close()
            else:
                return f"❌ صيغة غير مدعومة: {target_format}"
            
            return f"✅ تم تحويل الملف إلى {target_format}: {output_path}"
            
        except Exception as e:
            return f"❌ خطأ في التحويل: {str(e)}"

# أداة معالجة الصور
class ImageProcessor(BaseTool):
    name = "image_processor"
    description = "معالجة وتحويل الصور"
    args_schema = ImageProcessInput
    
    def _run(self, image_path: str, operation: str, params: Dict[str, Any]) -> str:
        try:
            if not os.path.exists(image_path):
                return "❌ الصورة غير موجودة"
            
            img = Image.open(image_path)
            output_path = f"processed_{os.path.basename(image_path)}"
            
            if operation == "resize":
                size = params.get('size', (800, 600))
                img = img.resize(size)
            elif operation == "compress":
                quality = params.get('quality', 85)
                img.save(output_path, optimize=True, quality=quality)
                return f"✅ تم ضغط الصورة: {output_path}"
            elif operation == "convert":
                format_type = params.get('format', 'JPEG')
                output_path = f"{os.path.splitext(image_path)[0]}.{format_type.lower()}"
                img.save(output_path, format=format_type)
                return f"✅ تم تحويل الصورة إلى {format_type}: {output_path}"
            
            img.save(output_path)
            return f"✅ تم معالجة الصورة: {output_path}"
            
        except Exception as e:
            return f"❌ خطأ في معالجة الصورة: {str(e)}"

# أداة ضغط الملفات
class ZipManager(BaseTool):
    name = "zip_manager"
    description = "ضغط وفك ضغط الملفات"
    args_schema = ZipOperationInput
    
    def _run(self, operation: str, files: list, output_path: str) -> str:
        try:
            if operation == "create":
                with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                    for file_path in files:
                        if os.path.exists(file_path):
                            zip_file.write(file_path, os.path.basename(file_path))
                return f"✅ تم إنشاء ملف مضغوط: {output_path}"
            
            elif operation == "extract":
                with zipfile.ZipFile(files[0], 'r') as zip_file:
                    zip_file.extractall(output_path)
                return f"✅ تم فك الضغط في: {output_path}"
            
        except Exception as e:
            return f"❌ خطأ في عملية الضغط: {str(e)}"

# أداة تقطيع الفيديو
class VideoEditor(BaseTool):
    name = "video_editor"
    description = "تقطيع وتحرير الفيديوهات"
    
    def _run(self, video_path: str, start_time: int, end_time: int) -> str:
        try:
            clip = mp.VideoFileClip(video_path)
            trimmed_clip = clip.subclip(start_time, end_time)
            
            output_path = f"trimmed_{os.path.basename(video_path)}"
            trimmed_clip.write_videofile(output_path)
            
            clip.close()
            trimmed_clip.close()
            
            return f"✅ تم تقطيع الفيديو: {output_path}"
            
        except Exception as e:
            return f"❌ خطأ في تقطيع الفيديو: {str(e)}"

# قائمة جميع الأدوات
ALL_TOOLS = [
    AdvancedVideoDownloader(),
    AdvancedVideoInfo(),
    FileConverter(),
    ImageProcessor(),
    ZipManager(),
    VideoEditor()
]
