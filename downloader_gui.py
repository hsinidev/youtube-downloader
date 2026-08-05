import os
import sys
import threading
import queue
import time
import tkinter as tk
from tkinter import filedialog
import webbrowser
import customtkinter
import yt_dlp
from PIL import Image

# Set appearance mode and default color theme
customtkinter.set_appearance_mode("Dark")
customtkinter.set_default_color_theme("blue")

class CancelledException(Exception):
    """Custom exception raised when user clicks Stop/Cancel."""
    pass

class QueueLogger:
    """Redirects yt-dlp logs to our thread-safe GUI message queue."""
    def __init__(self, msg_queue):
        self.msg_queue = msg_queue

    def debug(self, msg):
        if "[download]" in msg and "%" in msg:
            pass
        else:
            self.msg_queue.put(("log", msg))

    def info(self, msg):
        self.msg_queue.put(("log", msg))

    def warning(self, msg):
        self.msg_queue.put(("log", f"WARNING: {msg}"))

    def error(self, msg):
        self.msg_queue.put(("log", f"ERROR: {msg}"))


class DownloaderApp(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # Window Settings
        self.title("Basma - Advanced Multi-URL Downloader")
        self.geometry("1050x700")
        self.minsize(1050, 700)

        # Threading state variables
        self.download_queue = queue.Queue()
        self.download_thread = None
        self.cancel_requested = False

        # Load workspace presets
        self.presets = self.load_workspace_presets()

        # Detect ffmpeg availability
        self.ffmpeg_path = self.find_ffmpeg()

        # Build GUI
        self.create_widgets()
        
        # Start queue polling loop
        self.poll_queue()

        # Log ffmpeg status after GUI is ready
        if self.ffmpeg_path:
            self.after(500, lambda: self.write_log(
                f"✅ ffmpeg detected: {self.ffmpeg_path}\n"
                f"   Video+Audio will be merged into a single MP4 file.\n"
            ))
        else:
            self.after(500, lambda: self.write_log(
                "⚠️  WARNING: ffmpeg not found!\n"
                "   Video+Audio will be saved as SEPARATE files.\n"
                "   Install ffmpeg from https://ffmpeg.org/download.html\n"
            ))

    def find_ffmpeg(self):
        """Locate ffmpeg executable; returns path string or None.
        Works both when running from source and inside a PyInstaller bundle."""
        import shutil, sys

        # 1. Check next to the EXE / script first (bundled distribution)
        if getattr(sys, 'frozen', False):
            # Running inside a PyInstaller bundle
            exe_dir = os.path.dirname(sys.executable)
        else:
            exe_dir = os.path.dirname(os.path.abspath(__file__))

        bundled = os.path.join(exe_dir, "ffmpeg.exe")
        if os.path.exists(bundled):
            return bundled

        # 2. Check system PATH
        found = shutil.which("ffmpeg")
        if found:
            return found

        # 3. Common Windows install locations (Pinokio, Chocolatey, manual)
        candidates = [
            r"C:\pinokio\bin\miniconda\Library\bin\ffmpeg.exe",
            r"C:\pinokio\bin\miniconda\bin\ffmpeg.exe",
            r"C:\ffmpeg\bin\ffmpeg.exe",
            r"C:\ProgramData\chocolatey\bin\ffmpeg.exe",
            r"C:\Program Files\ffmpeg\bin\ffmpeg.exe",
            r"C:\Program Files (x86)\ffmpeg\bin\ffmpeg.exe",
        ]
        for path in candidates:
            if os.path.exists(path):
                return path
        return None

    def load_workspace_presets(self):
        """Scans the workspace for available YouTube URL files and loads them as presets."""
        presets = []
        base_dir = os.path.dirname(os.path.abspath(__file__))
        
        # English channel search
        eng_file = os.path.join(base_dir, "eng", "youtub urls.txt")
        if os.path.exists(eng_file):
            try:
                with open(eng_file, "r", encoding="utf-8") as f:
                    url = f.read().strip()
                    if url:
                        presets.append(("Pocoyo (English)", url))
            except Exception as e:
                print(f"Error reading eng preset: {e}")

        # French channel search
        fr_file = os.path.join(base_dir, "fr", "youtub urls.txt")
        if os.path.exists(fr_file):
            try:
                with open(fr_file, "r", encoding="utf-8") as f:
                    url = f.read().strip()
                    if url:
                        presets.append(("Petit Ours Brun (French)", url))
            except Exception as e:
                print(f"Error reading fr preset: {e}")

        return presets

    def open_url(self, url):
        """Opens the specified URL in the user's default browser."""
        webbrowser.open_new_tab(url)

    def create_widgets(self):
        # Main Layout Grid (1 row, 2 columns)
        self.grid_columnconfigure(0, weight=0, minsize=220)  # Sidebar
        self.grid_columnconfigure(1, weight=1)              # Main Content
        self.grid_rowconfigure(0, weight=1)

        # =====================================================================
        # 1. SIDEBAR FRAME (PRESETS + THEME TOGGLE)
        # =====================================================================
        self.sidebar_frame = customtkinter.CTkFrame(self, corner_radius=0, width=220)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        self.sidebar_frame.grid_propagate(False)
        # Allow row 99 to expand so toggle is pushed to the bottom
        self.sidebar_frame.grid_rowconfigure(99, weight=1)

        # Sidebar title
        self.sidebar_title = customtkinter.CTkLabel(
            self.sidebar_frame,
            text="⚡ Quick Presets",
            font=customtkinter.CTkFont(size=14, weight="bold")
        )
        self.sidebar_title.pack(pady=(30, 10))

        # Separator
        customtkinter.CTkFrame(self.sidebar_frame, height=2, fg_color="gray30").pack(fill="x", padx=20, pady=(0, 20))

        # Preset Loader in Sidebar
        self.preset_label = customtkinter.CTkLabel(
            self.sidebar_frame, 
            text="Workspace Presets:", 
            font=customtkinter.CTkFont(weight="bold")
        )
        self.preset_label.pack(anchor="w", padx=20, pady=(0, 5))

        preset_options = ["Custom URL (Paste below)"] + [f"{name} ({url})" for name, url in self.presets]
        self.preset_dropdown = customtkinter.CTkComboBox(
            self.sidebar_frame, 
            values=preset_options,
            command=self.preset_selected
        )
        self.preset_dropdown.pack(fill="x", padx=20, pady=(0, 20))
        self.preset_dropdown.set(preset_options[0])

        # ── Theme Toggle (pinned to bottom of sidebar) ──────────────────────
        # Spacer that absorbs all remaining vertical space
        self.sidebar_spacer = customtkinter.CTkFrame(self.sidebar_frame, fg_color="transparent")
        self.sidebar_spacer.pack(fill="both", expand=True)

        customtkinter.CTkFrame(self.sidebar_frame, height=2, fg_color="gray30").pack(fill="x", padx=20, pady=(0, 10))

        self.theme_label = customtkinter.CTkLabel(
            self.sidebar_frame,
            text="Appearance Mode:",
            font=customtkinter.CTkFont(size=11),
            text_color="gray60"
        )
        self.theme_label.pack(pady=(0, 6))

        self.theme_switch = customtkinter.CTkSwitch(
            self.sidebar_frame,
            text="🌙 Dark  /  ☀️ Light",
            font=customtkinter.CTkFont(size=12),
            command=self.toggle_theme,
            onvalue="Light",
            offvalue="Dark"
        )
        self.theme_switch.pack(pady=(0, 24))
        # Start in OFF position = Dark mode (matches app default)
        self.theme_switch.deselect()

        # =====================================================================
        # 2. MAIN CONTENT FRAME (DOWNLOADER ACTIONS)
        # =====================================================================
        self.main_content_frame = customtkinter.CTkScrollableFrame(self, fg_color="transparent")
        self.main_content_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=0)
        
        # Configure internal grid of main container
        self.main_content_frame.grid_columnconfigure(0, weight=1)

        # Header Title + Help Button
        self.header_frame = customtkinter.CTkFrame(self.main_content_frame, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(15, 10))
        self.header_label = customtkinter.CTkLabel(
            self.header_frame, 
            text="Basma Video Downloader", 
            font=customtkinter.CTkFont(size=26, weight="bold")
        )
        self.header_label.pack(side="left")

        self.help_btn = customtkinter.CTkButton(
            self.header_frame,
            text="❓ Help / About",
            width=130,
            height=34,
            fg_color="gray25",
            hover_color="gray35",
            font=customtkinter.CTkFont(size=12, weight="bold"),
            command=self.show_about_dialog
        )
        self.help_btn.pack(side="right", padx=(10, 0))

        # Inputs Panel
        self.input_panel = customtkinter.CTkFrame(self.main_content_frame)
        self.input_panel.grid(row=1, column=0, sticky="ew", padx=10, pady=10)
        self.input_panel.grid_columnconfigure(1, weight=1)

        # URL Entry Row
        self.url_label = customtkinter.CTkLabel(self.input_panel, text="Target URL:", font=customtkinter.CTkFont(weight="bold"))
        self.url_label.grid(row=0, column=0, padx=15, pady=15, sticky="w")
        self.url_entry = customtkinter.CTkEntry(
            self.input_panel, 
            placeholder_text="Paste any video, playlist, or channel URL here..."
        )
        self.url_entry.grid(row=0, column=1, columnspan=2, padx=15, pady=15, sticky="ew")

        # Save Directory Row
        self.dest_label = customtkinter.CTkLabel(self.input_panel, text="Save Location:", font=customtkinter.CTkFont(weight="bold"))
        self.dest_label.grid(row=1, column=0, padx=15, pady=(0, 15), sticky="w")
        
        default_dest = os.path.join(os.path.dirname(os.path.abspath(__file__)), "downloads")
        self.dest_entry = customtkinter.CTkEntry(self.input_panel)
        self.dest_entry.insert(0, default_dest)
        self.dest_entry.grid(row=1, column=1, padx=(15, 5), pady=(0, 15), sticky="ew")
        
        self.browse_btn = customtkinter.CTkButton(self.input_panel, text="Browse", width=80, command=self.browse_directory)
        self.browse_btn.grid(row=1, column=2, padx=(5, 15), pady=(0, 15), sticky="e")

        # Settings Panel (2x2 Grid)
        self.settings_panel = customtkinter.CTkFrame(self.main_content_frame)
        self.settings_panel.grid(row=2, column=0, sticky="ew", padx=10, pady=10)
        self.settings_panel.grid_columnconfigure((1, 3), weight=1)

        # Quality Dropdown
        self.quality_label = customtkinter.CTkLabel(self.settings_panel, text="Quality / Format:", font=customtkinter.CTkFont(weight="bold"))
        self.quality_label.grid(row=0, column=0, padx=15, pady=15, sticky="w")
        self.quality_dropdown = customtkinter.CTkComboBox(
            self.settings_panel,
            values=["Best Quality (1080p+)", "1080p Max", "720p Max", "480p Max", "Audio Only (MP3)"]
        )
        self.quality_dropdown.grid(row=0, column=1, padx=10, pady=15, sticky="ew")
        self.quality_dropdown.set("Best Quality (1080p+)")

        # Limit Dropdown
        self.limit_label = customtkinter.CTkLabel(self.settings_panel, text="Download Limit:", font=customtkinter.CTkFont(weight="bold"))
        self.limit_label.grid(row=0, column=2, padx=15, pady=15, sticky="w")
        self.limit_dropdown = customtkinter.CTkComboBox(
            self.settings_panel,
            values=["All Videos", "Latest 1 Video", "Latest 5 Videos", "Latest 10 Videos", "Latest 20 Videos"]
        )
        self.limit_dropdown.grid(row=0, column=3, padx=10, pady=15, sticky="ew")
        self.limit_dropdown.set("All Videos")

        # Archive Checkbox
        self.archive_check = customtkinter.CTkCheckBox(
            self.settings_panel, 
            text="Enable Incremental Download (Skip previously downloaded files)", 
            hover=True
        )
        self.archive_check.grid(row=1, column=0, columnspan=4, padx=15, pady=(0, 15), sticky="w")
        self.archive_check.select()

        # Action / Control buttons
        self.control_panel = customtkinter.CTkFrame(self.main_content_frame)
        self.control_panel.grid(row=3, column=0, sticky="ew", padx=10, pady=10)
        self.control_panel.grid_columnconfigure(0, weight=1)

        self.start_btn = customtkinter.CTkButton(
            self.control_panel, 
            text="Start Download", 
            font=customtkinter.CTkFont(size=14, weight="bold"), 
            height=40, 
            command=self.start_download
        )
        self.start_btn.grid(row=0, column=0, padx=(15, 10), pady=15, sticky="ew")

        self.stop_btn = customtkinter.CTkButton(
            self.control_panel, 
            text="Stop / Cancel", 
            font=customtkinter.CTkFont(size=14, weight="bold"), 
            height=40, 
            fg_color="#C0392B", 
            hover_color="#962D22", 
            state="disabled", 
            command=self.stop_download
        )
        self.stop_btn.grid(row=0, column=1, padx=(10, 15), pady=15, sticky="e")

        # Progress tracking elements
        self.progress_title_label = customtkinter.CTkLabel(self.control_panel, text="Status: Idle", anchor="w")
        self.progress_title_label.grid(row=1, column=0, columnspan=2, padx=15, pady=(5, 2), sticky="ew")

        self.progressbar = customtkinter.CTkProgressBar(self.control_panel)
        self.progressbar.grid(row=2, column=0, columnspan=2, padx=15, pady=(0, 5), sticky="ew")
        self.progressbar.set(0)

        self.stats_label = customtkinter.CTkLabel(
            self.control_panel, 
            text="Speed: 0.0 MB/s  |  ETA: --:--:--  |  0.0%", 
            font=customtkinter.CTkFont(family="Courier", size=12)
        )
        self.stats_label.grid(row=3, column=0, columnspan=2, padx=15, pady=(0, 15), sticky="w")

        # System Log Frame
        self.log_panel = customtkinter.CTkFrame(self.main_content_frame)
        self.log_panel.grid(row=4, column=0, sticky="ew", padx=10, pady=(10, 15))
        self.log_panel.grid_columnconfigure(0, weight=1)

        self.log_title = customtkinter.CTkLabel(self.log_panel, text="System Log Console:", font=customtkinter.CTkFont(weight="bold"))
        self.log_title.grid(row=0, column=0, padx=15, pady=(10, 5), sticky="w")

        # Setting fixed height for the scrollable log textbox to prevent dynamic layout shifts
        self.log_textbox = customtkinter.CTkTextbox(self.log_panel, font=customtkinter.CTkFont(family="Courier", size=12), height=200)
        self.log_textbox.grid(row=1, column=0, padx=15, pady=(0, 15), sticky="ew")
        self.log_textbox.configure(state="disabled")

    def fallback_avatar(self, parent):
        """Displays a simple emoji/text representation if profile image fails to load."""
        lbl = customtkinter.CTkLabel(
            parent,
            text="👨‍💻",
            font=customtkinter.CTkFont(size=72)
        )
        lbl.pack(pady=10)

    def show_about_dialog(self):
        """Opens a polished modal popup showing developer info and app details."""
        dialog = customtkinter.CTkToplevel(self)
        dialog.title("About / Developer Info")
        dialog.geometry("420x580")
        dialog.resizable(False, False)
        dialog.grab_set()  # Make modal
        dialog.focus_set()

        # Center dialog over main window
        self.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() // 2) - 210
        y = self.winfo_y() + (self.winfo_height() // 2) - 290
        dialog.geometry(f"+{x}+{y}")

        # App name header
        customtkinter.CTkLabel(
            dialog,
            text="Basma Video Downloader",
            font=customtkinter.CTkFont(size=20, weight="bold")
        ).pack(pady=(28, 2))

        customtkinter.CTkLabel(
            dialog,
            text="Version 2.0  •  Advanced YouTube Downloader",
            font=customtkinter.CTkFont(size=12),
            text_color="gray60"
        ).pack(pady=(0, 20))

        # Divider
        customtkinter.CTkFrame(dialog, height=2, fg_color="gray30").pack(fill="x", padx=30, pady=(0, 20))

        # DEVELOPER PROFILE section
        customtkinter.CTkLabel(
            dialog,
            text="DEVELOPER",
            font=customtkinter.CTkFont(size=11, weight="bold"),
            text_color="gray55"
        ).pack()

        # Profile image
        base_dir = os.path.dirname(os.path.abspath(__file__))
        photo_path = os.path.join(base_dir, "profile.png")
        if os.path.exists(photo_path):
            try:
                raw_img = Image.open(photo_path)
                profile_img = customtkinter.CTkImage(
                    light_image=raw_img,
                    dark_image=raw_img,
                    size=(110, 110)
                )
                customtkinter.CTkLabel(dialog, image=profile_img, text="").pack(pady=(12, 4))
                dialog._profile_img_ref = profile_img  # prevent GC
            except Exception:
                self.fallback_avatar(dialog)
        else:
            self.fallback_avatar(dialog)

        # Dev name & title
        customtkinter.CTkLabel(
            dialog,
            text="Hsini Mohamed",
            font=customtkinter.CTkFont(size=18, weight="bold")
        ).pack(pady=(4, 2))

        customtkinter.CTkLabel(
            dialog,
            text="Full-Stack Developer & SaaS Architect",
            font=customtkinter.CTkFont(size=12),
            text_color="gray65"
        ).pack(pady=(0, 18))

        # Social links
        links_frame = customtkinter.CTkFrame(dialog, fg_color="transparent")
        links_frame.pack(fill="x", padx=40, pady=(0, 10))

        customtkinter.CTkButton(
            links_frame,
            text="🌐  Portfolio  —  hsini.dev",
            anchor="w",
            fg_color="gray22",
            hover_color="gray32",
            command=lambda: self.open_url("https://hsini.dev")
        ).pack(fill="x", pady=4)

        customtkinter.CTkButton(
            links_frame,
            text="🐙  GitHub  —  github.com/hsinidev",
            anchor="w",
            fg_color="gray22",
            hover_color="gray32",
            command=lambda: self.open_url("https://github.com/hsinidev")
        ).pack(fill="x", pady=4)

        customtkinter.CTkButton(
            links_frame,
            text="🔗  LinkedIn  —  linkedin.com/in/hsinidev",
            anchor="w",
            fg_color="gray22",
            hover_color="gray32",
            command=lambda: self.open_url("https://linkedin.com/in/hsinidev/")
        ).pack(fill="x", pady=4)

        # Close button
        customtkinter.CTkFrame(dialog, height=2, fg_color="gray30").pack(fill="x", padx=30, pady=(18, 10))
        customtkinter.CTkButton(
            dialog,
            text="Close",
            width=120,
            command=dialog.destroy
        ).pack(pady=(0, 20))

    def toggle_theme(self):
        """Switches the entire app between Dark and Light mode in one step."""
        mode = self.theme_switch.get()  # "Light" or "Dark"
        customtkinter.set_appearance_mode(mode)
        if mode == "Light":
            self.theme_switch.configure(text="☀️ Light  /  🌙 Dark")
        else:
            self.theme_switch.configure(text="🌙 Dark  /  ☀️ Light")

    def preset_selected(self, selection):
        """Fills the target URL if a preset is selected."""
        for name, url in self.presets:
            if selection.startswith(name):
                self.url_entry.delete(0, "end")
                self.url_entry.insert(0, url)
                return

    def browse_directory(self):
        """Allows browsing directory paths."""
        selected_dir = filedialog.askdirectory(initialdir=self.dest_entry.get())
        if selected_dir:
            self.dest_entry.delete(0, "end")
            self.dest_entry.insert(0, selected_dir)

    def write_log(self, text):
        """Appends log text safely to the display console."""
        self.log_textbox.configure(state="normal")
        self.log_textbox.insert("end", f"{text}\n")
        self.log_textbox.configure(state="disabled")
        self.log_textbox.see("end")

    def progress_hook(self, d):
        """Handles yt-dlp progress callbacks safely inside the background thread."""
        if self.cancel_requested:
            raise CancelledException("User clicked cancel")

        if d['status'] == 'downloading':
            filename = os.path.basename(d.get('filename', ''))
            
            # Format percentage
            total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate') or 0
            downloaded_bytes = d.get('downloaded_bytes', 0)
            
            percent = 0.0
            if total_bytes > 0:
                percent = (downloaded_bytes / total_bytes) * 100
            elif d.get('_percent_str'):
                try:
                    percent = float(d.get('_percent_str').replace('%', '').strip())
                except ValueError:
                    percent = 0.0
            
            # Format download speed
            speed = d.get('speed')
            speed_str = "Unknown speed"
            if speed:
                if speed > 1024 * 1024:
                    speed_str = f"{speed / (1024 * 1024):.2f} MB/s"
                else:
                    speed_str = f"{speed / 1024:.2f} KB/s"

            # Format ETA
            eta = d.get('eta')
            eta_str = "--:--:--"
            if eta:
                eta_str = time.strftime('%H:%M:%S', time.gmtime(eta))

            self.download_queue.put(("progress", {
                "filename": filename,
                "percent": percent,
                "speed": speed_str,
                "eta": eta_str
            }))
        elif d['status'] == 'finished':
            self.download_queue.put(("progress", {
                "filename": "Finalizing post-processing...",
                "percent": 100.0,
                "speed": "0.0 MB/s",
                "eta": "00:00:00"
            }))

    def start_download(self):
        url = self.url_entry.get().strip()
        output_dir = self.dest_entry.get().strip()

        if not url:
            self.write_log("ERROR: Please enter a target URL.")
            return
        if not output_dir:
            self.write_log("ERROR: Please specify a destination directory.")
            return

        # Lock UI controls
        self.start_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        self.preset_dropdown.configure(state="disabled")
        self.url_entry.configure(state="disabled")
        self.dest_entry.configure(state="disabled")
        self.browse_btn.configure(state="disabled")
        self.quality_dropdown.configure(state="disabled")
        self.limit_dropdown.configure(state="disabled")
        self.archive_check.configure(state="disabled")

        # Initialize Thread variables
        self.cancel_requested = False
        self.progressbar.set(0)
        self.progress_title_label.configure(text="Status: Connecting...")
        self.stats_label.configure(text="Speed: Connecting...  |  ETA: Connecting...  |  0.0%")
        self.write_log(f"\n--- Starting Download Job ---")
        self.write_log(f"URL: {url}")
        self.write_log(f"Destination: {output_dir}")

        try:
            os.makedirs(output_dir, exist_ok=True)
        except Exception as e:
            self.write_log(f"ERROR creating directory: {e}")
            self.reset_ui()
            return

        # Detect node.exe: check next to EXE first (bundled), then common paths
        import sys as _sys
        if getattr(_sys, 'frozen', False):
            _exe_dir = os.path.dirname(_sys.executable)
        else:
            _exe_dir = os.path.dirname(os.path.abspath(__file__))

        node_candidates = [
            os.path.join(_exe_dir, "node.exe"),          # bundled next to EXE
            r"C:\pinokio\bin\miniconda\node.exe",
            r"C:\Program Files\nodejs\node.exe",
            r"C:\Program Files (x86)\nodejs\node.exe",
        ]
        active_node_path = None
        for path in node_candidates:
            if os.path.exists(path):
                active_node_path = path
                break

        ydl_opts = {
            'logger': QueueLogger(self.download_queue),
            'progress_hooks': [self.progress_hook],
            'ignoreerrors': True,
            'no_color': True,
            'quiet': True,
            # Use Android + iOS player APIs — NO JavaScript runtime required.
            # Works on any PC without Node.js or Deno installed.
            'extractor_args': {
                'youtube': {
                    'player_client': ['android', 'ios', 'web'],
                }
            },
            'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
        }

        # If node.exe is available, also enable JS runtime for best compat
        if active_node_path:
            ydl_opts['js_runtimes'] = {'node': {'path': active_node_path}}


        # Quality Selection mapping — prefer pre-muxed MP4 (no ffmpeg needed),
        # fall back to separate streams + ffmpeg merge.
        quality = self.quality_dropdown.get()

        if "Audio Only" in quality:
            # Audio-only: always extract to mp3
            ydl_opts['format'] = 'bestaudio/best'
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]
        else:
            # Video modes — try pre-muxed MP4 first (already 1 file, no merge needed)
            # then fall back to separate best streams and merge with ffmpeg
            if "Best Quality" in quality:
                fmt = (
                    'bestvideo[ext=mp4]+bestaudio[ext=m4a]'
                    '/bestvideo[ext=mp4]+bestaudio'
                    '/bestvideo+bestaudio[ext=m4a]'
                    '/bestvideo+bestaudio'
                    '/best[ext=mp4]/best'
                )
            elif "1080p" in quality:
                fmt = (
                    'bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]'
                    '/bestvideo[height<=1080]+bestaudio'
                    '/best[height<=1080][ext=mp4]/best[height<=1080]/best'
                )
            elif "720p" in quality:
                fmt = (
                    'bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]'
                    '/bestvideo[height<=720]+bestaudio'
                    '/best[height<=720][ext=mp4]/best[height<=720]/best'
                )
            elif "480p" in quality:
                fmt = (
                    'bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]'
                    '/bestvideo[height<=480]+bestaudio'
                    '/best[height<=480][ext=mp4]/best[height<=480]/best'
                )
            else:
                fmt = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best'

            ydl_opts['format'] = fmt
            ydl_opts['merge_output_format'] = 'mp4'

            # Tell yt-dlp where ffmpeg is if we found it
            if self.ffmpeg_path:
                ydl_opts['ffmpeg_location'] = os.path.dirname(self.ffmpeg_path)

        # Limit Selection mapping
        limit_sel = self.limit_dropdown.get()
        if "1 Video" in limit_sel:
            ydl_opts['playlistend'] = 1
        elif "5 Videos" in limit_sel:
            ydl_opts['playlistend'] = 5
        elif "10 Videos" in limit_sel:
            ydl_opts['playlistend'] = 10
        elif "20 Videos" in limit_sel:
            ydl_opts['playlistend'] = 20

        # Enable download Archive
        if self.archive_check.get():
            ydl_opts['download_archive'] = os.path.join(output_dir, 'downloaded_archive.txt')

        # Launch Background Worker
        self.download_thread = threading.Thread(
            target=self.run_download_thread, 
            args=(url, ydl_opts), 
            daemon=True
        )
        self.download_thread.start()

    def run_download_thread(self, url, ydl_opts):
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            if self.cancel_requested:
                self.download_queue.put(("cancelled", None))
            else:
                self.download_queue.put(("finished", None))

        except CancelledException:
            self.download_queue.put(("cancelled", None))
        except Exception as e:
            self.download_queue.put(("error", str(e)))

    def stop_download(self):
        self.cancel_requested = True
        self.stop_btn.configure(state="disabled")
        self.write_log("Download cancellation requested. Waiting for cleanup...")

    def reset_ui(self):
        self.start_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        
        self.preset_dropdown.configure(state="normal")
        self.url_entry.configure(state="normal")
        self.dest_entry.configure(state="normal")
        self.browse_btn.configure(state="normal")
        self.quality_dropdown.configure(state="normal")
        self.limit_dropdown.configure(state="normal")
        self.archive_check.configure(state="normal")

    def poll_queue(self):
        try:
            while True:
                msg_type, data = self.download_queue.get_nowait()
                
                if msg_type == "log":
                    self.write_log(data)
                
                elif msg_type == "progress":
                    filename = data["filename"]
                    percent = data["percent"]
                    speed = data["speed"]
                    eta = data["eta"]
                    
                    self.progress_title_label.configure(text=f"Downloading: {filename}")
                    self.progressbar.set(percent / 100.0)
                    self.stats_label.configure(text=f"Speed: {speed}  |  ETA: {eta}  |  {percent:.1f}%")
                
                elif msg_type == "finished":
                    self.write_log("Job completed successfully!")
                    self.progress_title_label.configure(text="Status: Download Completed!")
                    self.progressbar.set(1.0)
                    self.stats_label.configure(text="Speed: Finished  |  ETA: 00:00:00  |  100.0%")
                    self.reset_ui()
                
                elif msg_type == "cancelled":
                    self.write_log("Job cancelled by the user.")
                    self.progress_title_label.configure(text="Status: Download Cancelled")
                    self.progressbar.set(0)
                    self.stats_label.configure(text="Speed: Stopped  |  ETA: --:--:--  |  0.0%")
                    self.reset_ui()
                
                elif msg_type == "error":
                    self.write_log(f"ERROR encountered: {data}")
                    self.progress_title_label.configure(text="Status: Download Failed")
                    self.progressbar.set(0)
                    self.reset_ui()

                self.download_queue.task_done()
        except queue.Empty:
            pass
        
        self.after(100, self.poll_queue)

if __name__ == "__main__":
    app = DownloaderApp()
    app.mainloop()
