
# yt_dlp_wrapper.py - محمل الوسائط المتطور
import yt_dlp
import os
import json
import subprocess
from typing import Dict, List, Optional, Tuple

class AdvancedMediaDownloader:
    """محمل الوسائط المتطور مع إعدادات متقدمة"""
    
    def __init__(self):
        self.download_path = "downloads"
        self.temp_path = "temp"
        os.makedirs(self.download_path, exist_ok=True)
        os.makedirs(self.temp_path, exist_ok=True)
    
    def get_video_info(self, url: str) -> Dict:
        """جلب معلومات شاملة عن الفيديو"""
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)

                # استخراج المعلومات الأساسية
                basic_info = {
                    'title': info.get('title', 'غير متوفر'),
                    'duration': info.get('duration', 0),
                    'uploader': info.get('uploader', 'غير متوفر'),
                    'view_count': info.get('view_count', 0),
                    'like_count': info.get('like_count', 0),
                    'description': info.get('description', 'غير متوفر'),
                    'upload_date': info.get('upload_date', 'غير متوفر'),
                    'thumbnail': info.get('thumbnail', ''),
                    'website': info.get('extractor', 'غير معروف'),
                    'url': url
                }
                
                # استخراج الجودات المتاحة
                formats = info.get('formats', [])
                available_qualities = self._extract_qualities(formats)
                basic_info['available_qualities'] = available_qualities
                
                # معلومات تقنية إضافية
                basic_info['filesize'] = info.get('filesize', 0)
                basic_info['fps'] = info.get('fps', 0)
                basic_info['format_id'] = info.get('format_id', '')
                
                return basic_info
                
        except Exception as e:
            return {'error': f"خطأ في جلب المعلومات: {str(e)}"}
    
    def _extract_qualities(self, formats: List) -> Dict:
        """استخراج الجودات المتاحة من قائمة الصيغ"""
        qualities = {
            'video': [],
            'audio': [],
            'combined': []
        }
        
        for fmt in formats:
            if fmt.get('vcodec') != 'none' and fmt.get('height'):
                # فيديو
                quality_info = {
                    'quality': f"{fmt['height']}p",
                    'format_id': fmt['format_id'],
                    'ext': fmt.get('ext', 'mp4'),
                    'filesize': fmt.get('filesize', 0),
                    'fps': fmt.get('fps', 0),
                    'vcodec': fmt.get('vcodec', ''),
                    'acodec': fmt.get('acodec', 'none')
                }
                
                if fmt.get('acodec') != 'none':
                    qualities['combined'].append(quality_info)
                else:
                    qualities['video'].append(quality_info)
            
            elif fmt.get('acodec') != 'none' and fmt.get('vcodec') == 'none':
                # صوت فقط
                audio_info = {
                    'quality': f"{fmt.get('abr', 'unknown')}kbps",
                    'format_id': fmt['format_id'],
                    'ext': fmt.get('ext', 'mp3'),
                    'filesize': fmt.get('filesize', 0),
                    'acodec': fmt.get('acodec', ''),
                    'abr': fmt.get('abr', 0)
                }
                qualities['audio'].append(audio_info)
        
        # ترتيب حسب الجودة
        qualities['video'].sort(key=lambda x: int(x['quality'].replace('p', '')), reverse=True)
        qualities['combined'].sort(key=lambda x: int(x['quality'].replace('p', '')), reverse=True)
        qualities['audio'].sort(key=lambda x: x['abr'], reverse=True)
        
        return qualities
    
    def download_media(self, url: str, media_type: str = "video", 
                      quality: str = "best", output_format: str = "mp4") -> Dict:
        """تحميل الوسائط مع خيارات متقدمة"""
        try:
            # تحديد إعدادات التحميل
            ydl_opts = self._get_download_options(media_type, quality, output_format)
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # جلب معلومات الفيديو أولاً
                info = ydl.extract_info(url, download=False)
                filename = ydl.prepare_filename(info)
                
                # تحميل الملف
                ydl.download([url])
                
                return {
                    'success': True,
                    'filename': filename,
                    'title': info.get('title', 'Unknown'),
                    'duration': info.get('duration', 0),
                    'filesize': os.path.getsize(filename) if os.path.exists(filename) else 0,
                    'format': output_format,
                    'quality': quality
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f"خطأ في التحميل: {str(e)}"
            }
    
    def _get_download_options(self, media_type: str, quality: str, output_format: str) -> Dict:
        """تحديد خيارات التحميل حسب النوع والجودة"""
        base_opts = {
            'outtmpl': f'{self.download_path}/%(title)s.%(ext)s',
            'quiet': True,
            'no_warnings': True,
            'writeinfojson': False,
            'writesubtitles': False,
        }
        
        if media_type == "audio":
            base_opts.update({
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': output_format,
                    'preferredquality': '320' if quality == 'high' else '192',
                }]
            })
        else:
            # تحديد جودة الفيديو
            quality_map = {
                'ultra': 'best[height<=2160]',
                'high': 'best[height<=1080]',
                'medium': 'best[height<=720]',
                'low': 'best[height<=480]',
                'best': 'best'
            }
            
            base_opts['format'] = quality_map.get(quality, 'best')
            
            if output_format != 'best':
                base_opts['postprocessors'] = [{
                    'key': 'FFmpegVideoConvertor',
                    'preferedformat': output_format,
                }]
        
        return base_opts
    
    def batch_download(self, urls: List[str], **kwargs) -> List[Dict]:
        """تحميل متعدد للروابط"""
        results = []
        for url in urls:
            result = self.download_media(url, **kwargs)
            results.append({
                'url': url,
                'result': result
            })
        return results
    
    def get_playlist_info(self, url: str) -> Dict:
        """جلب معلومات قائمة التشغيل"""
        try:
            ydl_opts = {
                'quiet': True,
                'extract_flat': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                if 'entries' in info:
                    return {
                        'title': info.get('title', 'قائمة تشغيل'),
                        'count': len(info['entries']),
                        'uploader': info.get('uploader', 'غير معروف'),
                        'entries': [
                            {
                                'title': entry.get('title', 'غير متوفر'),
                                'url': entry.get('url', ''),
                                'duration': entry.get('duration', 0)
                            }
                            for entry in info['entries'][:10]  # أول 10 فيديوهات
                        ]
                    }
                else:
                    return {'error': 'ليست قائمة تشغيل'}
                    
        except Exception as e:
            return {'error': f"خطأ في معالجة قائمة التشغيل: {str(e)}"}
    
    def extract_audio_from_video(self, video_path: str, output_format: str = "mp3") -> str:
        """استخراج الصوت من ملف فيديو"""
        try:
            base_name = os.path.splitext(os.path.basename(video_path))[0]
            output_path = f"{self.download_path}/{base_name}.{output_format}"
            
            cmd = [
                'ffmpeg', '-i', video_path,
                '-vn', '-acodec', 'libmp3lame' if output_format == 'mp3' else 'copy',
                '-ab', '320k', output_path, '-y'
            ]
            
            subprocess.run(cmd, check=True, capture_output=True)
            return output_path
            
        except Exception as e:
            raise Exception(f"خطأ في استخراج الصوت: {str(e)}")
    
    def get_supported_sites(self) -> List[str]:
        """الحصول على قائمة المواقع المدعومة"""
        try:
            with yt_dlp.YoutubeDL() as ydl:
                extractors = ydl.list_extractors()
                return [extractor.IE_NAME for extractor in extractors[:50]]  # أول 50 موقع
        except:
            return ['youtube', 'tiktok', 'instagram', 'twitter', 'vimeo', 'facebook']

# إنشاء مثيل وحيد
downloader = AdvancedMediaDownloader()

# دوال للتوافق مع الكود القديم
def get_video_info(url: str) -> str:
    """دالة للتوافق مع الكود القديم"""
    info = downloader.get_video_info(url)
    
    if 'error' in info:
        return f"❌ {info['error']}"
    
    duration = info['duration']
    minutes = duration // 60
    seconds = duration % 60
    
    qualities = info.get('available_qualities', {})
    video_qualities = [q['quality'] for q in qualities.get('combined', [])]
    
    result = f"""
🎬 **معلومات الفيديو:**
📝 العنوان: {info['title']}
⏱️ المدة: {minutes}:{seconds:02d}
👤 القناة: {info['uploader']}
👁️ المشاهدات: {info['view_count']:,}
👍 الإعجابات: {info['like_count']:,}
🌐 المنصة: {info['website']}
🎯 الجودات المتاحة: {', '.join(video_qualities[:5])}
🔗 الرابط: {info['url']}
    """
    return result

def download_media(url: str, media_type: str, quality: str, output_format: str) -> str:
    """دالة للتوافق مع الكود القديم"""
    result = downloader.download_media(url, media_type, quality, output_format)
    
    if result['success']:
        return f"✅ تم تحميل {media_type} بجودة {quality} بنجاح!"
    else:
        return f"❌ {result['error']}"
