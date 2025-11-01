
"""
ELBASHA Ultra Speed Downloader - Kivy Mobile Version
Converted from Tkinter to work on Android/iOS
"""

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.progressbar import ProgressBar
from kivy.uix.spinner import Spinner
from kivy.uix.togglebutton import ToggleButton
from kivy.clock import Clock
from kivy.core.clipboard import Clipboard
from kivy.utils import platform
import threading
import os
import re
import sys
import subprocess
from pathlib import Path
from urllib.parse import urlparse
import time

# =====================================================
# Auto-Install Dependencies
# =====================================================
def install_dependencies():
    """Install missing dependencies"""
    required_packages = {
        'yt_dlp': 'yt-dlp',
        'requests': 'requests'
    }

    missing_packages = []
    for module_name, pip_name in required_packages.items():
        try:
            __import__(module_name)
        except ImportError:
            missing_packages.append(pip_name)

    if missing_packages:
        print(f"⏳ جاري تثبيت المكتبات: {', '.join(missing_packages)}")
        for package in missing_packages:
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                print(f"✓ تم تثبيت {package}")
            except Exception as e:
                print(f"✗ فشل تثبيت {package}: {str(e)}")

# Install on startup
print("🔍 فحص المكتبات...")
install_dependencies()

# Import after installation
try:
    import yt_dlp
    import requests
except ImportError as e:
    print(f"⚠️ تحذير: {str(e)}")


class DownloaderApp(App):

    def build(self):
        self.title = "ELBASHA Downloader"
        self.is_downloading = False
        self.cancel_flag = False

        # Set download folder based on platform
        if platform == 'android':
            from android.storage import primary_external_storage_path
            self.download_folder = os.path.join(
                primary_external_storage_path(), 
                'Download', 
                'ELBASHA'
            )
        else:
            self.download_folder = str(Path.home() / "Downloads" / "ELBASHA")

        os.makedirs(self.download_folder, exist_ok=True)

        # Main layout
        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Title
        title = Label(
            text='⚡ ELBASHA Downloader',
            size_hint=(1, 0.1),
            font_size='24sp',
            bold=True,
            color=(0, 1, 0, 1)
        )
        main_layout.add_widget(title)

        # URL input
        url_layout = BoxLayout(size_hint=(1, 0.08), spacing=5)
        url_layout.add_widget(Label(text='الرابط:', size_hint=(0.15, 1)))
        self.url_input = TextInput(
            hint_text='ضع الرابط هنا',
            multiline=False,
            size_hint=(0.85, 1)
        )
        url_layout.add_widget(self.url_input)
        main_layout.add_widget(url_layout)

        # Buttons row 1
        btn_layout1 = BoxLayout(size_hint=(1, 0.08), spacing=5)

        paste_btn = Button(
            text='📋 لصق',
            on_press=self.paste_url,
            background_color=(0, 1, 0, 1)
        )
        btn_layout1.add_widget(paste_btn)

        clear_btn = Button(
            text='✖ مسح',
            on_press=self.clear_url,
            background_color=(1, 0.3, 0.3, 1)
        )
        btn_layout1.add_widget(clear_btn)

        main_layout.add_widget(btn_layout1)

        # Mode selection
        mode_layout = BoxLayout(size_hint=(1, 0.08), spacing=5)
        mode_layout.add_widget(Label(text='النوع:', size_hint=(0.2, 1)))

        self.mode_buttons = {}
        for mode, text in [('video', '🎬 فيديو'), ('audio', '🎵 صوت'), ('file', '📥 ملف')]:
            btn = ToggleButton(
                text=text,
                group='mode',
                state='down' if mode == 'video' else 'normal',
                size_hint=(0.27, 1)
            )
            self.mode_buttons[mode] = btn
            mode_layout.add_widget(btn)

        main_layout.add_widget(mode_layout)

        # Quality selection
        quality_layout = BoxLayout(size_hint=(1, 0.08), spacing=5)
        quality_layout.add_widget(Label(text='الجودة:', size_hint=(0.2, 1)))

        self.quality_spinner = Spinner(
            text='best 🚀',
            values=['best 🚀', '1080p', '720p', '480p', '360p'],
            size_hint=(0.8, 1)
        )
        quality_layout.add_widget(self.quality_spinner)
        main_layout.add_widget(quality_layout)

        # Control buttons
        control_layout = BoxLayout(size_hint=(1, 0.1), spacing=10)

        self.start_btn = Button(
            text='▶ بدء التحميل',
            on_press=self.start_download,
            background_color=(0, 1, 0, 1),
            bold=True
        )
        control_layout.add_widget(self.start_btn)

        self.stop_btn = Button(
            text='⏹ إيقاف',
            on_press=self.stop_download,
            background_color=(1, 0.3, 0.3, 1),
            disabled=True,
            bold=True
        )
        control_layout.add_widget(self.stop_btn)

        main_layout.add_widget(control_layout)

        # Progress bar
        progress_layout = BoxLayout(orientation='vertical', size_hint=(1, 0.15), spacing=5)
        progress_layout.add_widget(Label(text='التقدم:', size_hint=(1, 0.3)))

        self.progress_bar = ProgressBar(max=100, size_hint=(1, 0.4))
        progress_layout.add_widget(self.progress_bar)

        self.progress_label = Label(text='0%', size_hint=(1, 0.3))
        progress_layout.add_widget(self.progress_label)

        main_layout.add_widget(progress_layout)

        # Speed label
        self.speed_label = Label(
            text='السرعة: 0 MB/s',
            size_hint=(1, 0.05),
            color=(0, 1, 0, 1)
        )
        main_layout.add_widget(self.speed_label)

        # Status log
        log_layout = BoxLayout(orientation='vertical', size_hint=(1, 0.35))
        log_layout.add_widget(Label(text='السجل:', size_hint=(1, 0.1)))

        scroll_view = ScrollView(size_hint=(1, 0.9))
        self.status_label = Label(
            text='جاهز للتحميل...',
            size_hint_y=None,
            markup=True
        )
        self.status_label.bind(texture_size=self.status_label.setter('size'))
        scroll_view.add_widget(self.status_label)
        log_layout.add_widget(scroll_view)

        main_layout.add_widget(log_layout)

        return main_layout

    def paste_url(self, instance):
        """Paste from clipboard"""
        try:
            clipboard_text = Clipboard.paste()
            if clipboard_text:
                self.url_input.text = clipboard_text
                self.log_status("✓ تم لصق الرابط")
            else:
                self.log_status("✗ الحافظة فارغة")
        except Exception as e:
            self.log_status(f"✗ خطأ: {str(e)}")

    def clear_url(self, instance):
        """Clear URL input"""
        self.url_input.text = ""
        self.log_status("✓ تم مسح الرابط")

    def log_status(self, message):
        """Add message to status log"""
        current = self.status_label.text
        timestamp = time.strftime("%H:%M:%S")
        self.status_label.text = f"{current}\n[{timestamp}] {message}"

    def get_selected_mode(self):
        """Get selected download mode"""
        for mode, btn in self.mode_buttons.items():
            if btn.state == 'down':
                return mode
        return 'video'

    def update_progress(self, progress, speed_mbps=0):
        """Update progress bar and labels"""
        self.progress_bar.value = min(progress, 100)
        self.progress_label.text = f"{min(progress, 100):.1f}%"
        self.speed_label.text = f"السرعة: {speed_mbps:.2f} MB/s ⚡"

    def start_download(self, instance):
        """Start download process"""
        url = self.url_input.text.strip()

        if not url:
            self.log_status("✗ الرجاء إدخال رابط")
            return

        if self.is_downloading:
            self.log_status("ℹ️ يوجد تحميل قيد التنفيذ")
            return

        self.cancel_flag = False
        self.is_downloading = True
        self.start_btn.disabled = True
        self.stop_btn.disabled = False
        self.progress_bar.value = 0
        self.progress_label.text = "0%"

        # Start download in background thread
        download_thread = threading.Thread(
            target=self.download_worker,
            args=(url,),
            daemon=True
        )
        download_thread.start()

    def stop_download(self, instance):
        """Stop current download"""
        if self.is_downloading:
            self.cancel_flag = True
            self.log_status("⏹ جاري إيقاف التحميل...")
            self.stop_btn.disabled = True

    def download_worker(self, url):
        """Background download worker"""
        try:
            mode = self.get_selected_mode()

            if mode == 'file':
                self.download_direct_file(url)
            else:
                self.download_media(url, mode)

            if not self.cancel_flag:
                Clock.schedule_once(lambda dt: self.log_status("✓ اكتمل التحميل!"))
                Clock.schedule_once(lambda dt: self.update_progress(100))

        except Exception as e:
            if not self.cancel_flag:
                Clock.schedule_once(lambda dt: self.log_status(f"✗ خطأ: {str(e)}"))

        finally:
            self.is_downloading = False
            Clock.schedule_once(lambda dt: setattr(self.start_btn, 'disabled', False))
            Clock.schedule_once(lambda dt: setattr(self.stop_btn, 'disabled', True))

    def download_media(self, url, mode):
        """Download video/audio using yt-dlp"""
        import yt_dlp

        Clock.schedule_once(lambda dt: self.log_status(f"🚀 بدء تحميل {mode}..."))

        quality = self.quality_spinner.text.split()[0]

        ydl_opts = {
            'outtmpl': os.path.join(self.download_folder, '%(title)s.%(ext)s'),
            'progress_hooks': [self.yt_dlp_progress_hook],
            'quiet': False,
        }

        if mode == 'audio':
            ydl_opts['format'] = 'bestaudio/best'
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '320',
            }]
        else:
            if quality == 'best':
                ydl_opts['format'] = 'bestvideo+bestaudio/best'
            else:
                ydl_opts['format'] = f'bestvideo[height<={quality[:-1]}]+bestaudio/best'

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            if self.cancel_flag:
                return
            ydl.download([url])

    def yt_dlp_progress_hook(self, d):
        """Progress callback for yt-dlp"""
        if self.cancel_flag:
            raise Exception("تم الإلغاء")

        if d['status'] == 'downloading':
            if 'total_bytes' in d:
                progress = (d['downloaded_bytes'] / d['total_bytes']) * 100
                speed = d.get('speed', 0)
                speed_mbps = (speed / (1024 * 1024)) if speed else 0

                Clock.schedule_once(
                    lambda dt: self.update_progress(progress, speed_mbps)
                )

        elif d['status'] == 'finished':
            Clock.schedule_once(lambda dt: self.log_status("⚙️ جاري المعالجة..."))

    def download_direct_file(self, url):
        """Download direct file"""
        import requests

        Clock.schedule_once(lambda dt: self.log_status("🚀 بدء التحميل..."))

        parsed_url = urlparse(url)
        filename = os.path.basename(parsed_url.path)

        if not filename:
            filename = f"download_{int(time.time())}"

        filename = re.sub(r'[<>:"/\\|?*]', '', filename)
        filepath = os.path.join(self.download_folder, filename)

        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()

        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0
        start_time = time.time()

        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024*1024):
                if self.cancel_flag:
                    f.close()
                    if os.path.exists(filepath):
                        os.remove(filepath)
                    return

                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)

                    elapsed = time.time() - start_time
                    speed_mbps = (downloaded / (1024*1024)) / elapsed if elapsed > 0 else 0

                    if total_size > 0:
                        progress = (downloaded / total_size) * 100
                        Clock.schedule_once(
                            lambda dt: self.update_progress(progress, speed_mbps)
                        )

        Clock.schedule_once(lambda dt: self.log_status(f"✓ تم حفظ: {filename}"))


if __name__ == '__main__':
    DownloaderApp().run()
