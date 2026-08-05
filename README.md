# 🎬 Basma — Advanced YouTube Downloader

A premium, feature-rich desktop GUI application for downloading YouTube videos, playlists, and full channels. Built with Python, CustomTkinter, and yt-dlp.

> Developed by **Hsini Mohamed** — Full-Stack Developer & SaaS Architect  
> 🌐 [hsini.dev](https://hsini.dev) · 🐙 [GitHub](https://github.com/hsinidev) · 🔗 [LinkedIn](https://linkedin.com/in/hsinidev)

---

## ✨ Features

- 📥 Download **single videos**, **playlists**, or **entire YouTube channels**
- 🎞️ Outputs a **single merged MP4 file** (video + audio combined)
- 🎵 Optional **Audio Only (MP3)** mode
- 🎚️ Quality selection: Best, 1080p, 720p, 480p, Audio Only
- 📋 Download limit: All / Latest 1, 5, 10, or 20 videos
- ✅ **Incremental download** — skips already-downloaded files using an archive
- ⚡ **Workspace presets** — auto-loads channel URLs from `eng/` and `fr/` folders
- 📊 Real-time progress bar, speed, and ETA display
- 🖥️ Live system log console
- 🌙 Built-in Light / Dark mode toggle
- ℹ️ Help / About popup with developer info

---

## 🖥️ Requirements

### Python
- **Python 3.10+** — [Download here](https://www.python.org/downloads/)

### ffmpeg (Required for merged MP4 output)
ffmpeg must be installed for video+audio to be merged into one file.

- **Windows**: Download from [ffmpeg.org](https://ffmpeg.org/download.html) or install via [Chocolatey](https://chocolatey.org/):
  ```bash
  choco install ffmpeg
  ```
- **macOS**:
  ```bash
  brew install ffmpeg
  ```
- **Linux (Debian/Ubuntu)**:
  ```bash
  sudo apt install ffmpeg
  ```

> ⚠️ Without ffmpeg, yt-dlp will save video and audio as **separate files**.  
> The app will show a warning in the log console if ffmpeg is not detected.

---

## 📦 Installation

### 1. Clone or download this project

```bash
git clone https://github.com/hsinidev/basma.git
cd basma
```

Or just copy the project folder to your machine.

### 2. Install Python dependencies

```bash
pip install -r requirements.txt
```

This installs:
| Package | Purpose |
|---------|---------|
| `yt-dlp` | YouTube downloading engine |
| `customtkinter` | Modern dark-mode GUI framework |
| `Pillow` | Profile image rendering in the Help dialog |

### 3. Run the application

**Windows (double-click):**
```
run_downloader.bat
```

**Or from terminal:**
```bash
python downloader_gui.py
```

---

## 🚀 How to Use

1. **Paste a URL** in the *Target URL* field — any of the following work:
   - Single video: `https://www.youtube.com/watch?v=...`
   - Playlist: `https://www.youtube.com/playlist?list=...`
   - Channel: `https://www.youtube.com/channel/...` or `https://www.youtube.com/@ChannelName`

2. **Choose a Save Location** (defaults to `downloads/` inside the project folder)

3. **Select Quality / Format**:
   - `Best Quality` — highest available resolution
   - `1080p Max` / `720p Max` / `480p Max` — capped resolution
   - `Audio Only (MP3)` — extracts audio only

4. **Set a Download Limit** (optional) — e.g., "Latest 5 Videos" for testing

5. **Enable Incremental Download** (recommended for channels) — skips already-downloaded videos on repeat runs

6. Click **Start Download** — watch real-time progress in the log console

7. Use **Stop / Cancel** to interrupt at any time

---

## 📁 Project Structure

```
basma/
├── downloader_gui.py        # Main application
├── requirements.txt         # Python dependencies
├── run_downloader.bat       # Windows launcher
├── README.md                # This file
├── profile.png              # Developer profile photo (optional)
├── downloads/               # Default download output folder (auto-created)
├── eng/
│   └── youtub urls.txt      # English channel preset URL
└── fr/
    └── youtub urls.txt      # French channel preset URL
```

---

## 🔧 Adding Workspace Presets

To pre-load channel URLs into the sidebar dropdown, add a URL to the text files:

- `eng/youtub urls.txt` → English channel URL (one URL per file)
- `fr/youtub urls.txt` → French channel URL (one URL per file)

The app reads these on startup and adds them to the **Quick Presets** dropdown automatically.

---

## ❓ Troubleshooting

| Problem | Solution |
|---------|----------|
| `ModuleNotFoundError: No module named 'yt_dlp'` | Run `pip install -r requirements.txt` |
| `ModuleNotFoundError: No module named 'customtkinter'` | Run `pip install customtkinter` |
| Video and audio saved as separate files | Install ffmpeg and ensure it's on PATH |
| `WARNING: ffmpeg not found` shown in log | See [ffmpeg installation](#-requirements) above |
| Download fails immediately | Check the URL is correct and publicly accessible |
| App won't start on Windows | Make sure you're running Python 3.10+ via `python --version` |

---

## 📄 License

This project is for personal and educational use.  
Built with ❤️ by [Hsini Mohamed](https://hsini.dev)
