<div align="center">
# 🚀 Youtube Downloader
### *Modern, High-Performance Python Solution & Developer Suite*

<p align="center">
  [![Architect](https://img.shields.io/badge/Architect-Hsini%20Mohamed-0055ff?style=for-the-badge&logo=github&logoColor=white)](https://hsini.dev)
  [![Portfolio](https://img.shields.io/badge/Portfolio-hsini.dev-00c853?style=for-the-badge&logo=google-chrome&logoColor=white)](https://hsini.dev)
  [![Language](https://img.shields.io/badge/Language-Python-3776AB?style=for-the-badge)](https://github.com/hsinidev)
  [![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)
</p>

</div>

---
## 🌟 Executive Overview

**Youtube Downloader** is a production-grade **Python** platform engineered for high reliability, clean architectural separation, and frictionless developer workflow.

## ⚡ Key Highlights & Capabilities

- **Scalable Architecture**: Modular, decoupled components adhering to clean code principles.
- **Optimized Runtime**: Ultra-fast execution with minimal memory and CPU overhead.
- **Developer Tooling**: Standardized linting, formatting, and rapid local iteration setup.
- **Production Ready**: Built-in error resilience, validation, and structured logging.

---
## 🏗️ Architecture & Technology Stack

- **Primary Language**: `Python`
- **Design Pattern**: Modular Clean Architecture / Domain-Driven Design
- **License**: MIT Open Source Attribution

## 📖 Deep-Dive Technical Documentation

# 🎬 Basma — Advanced YouTube Downloader

A premium, feature-rich desktop GUI application for downloading YouTube videos, playlists, and full channels. Built with Python, CustomTkinter, and yt-dlp.

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


This project is for personal and educational use.  
Built with ❤️ by [Hsini Mohamed](https://hsini.dev)

---
## 🚀 Quick Start & Installation

### 1. Clone the Repository
```bash
git clone https://github.com/hsinidev/youtube-downloader.git
cd youtube-downloader
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Launch the Application
```bash
python main.py
```


---

## 👨‍💻 System Architect & Author

<table align="center" style="border: none; background: transparent; width: 100%;">
  <tr>
    <td align="center" width="160" style="border: none; padding: 12px;">
      <img src="https://avatars.githubusercontent.com/u/232697467?v=4" width="120" height="120" style="border-radius: 50%; box-shadow: 0 8px 24px rgba(99,102,241,0.3); border: 2.5px solid #6366f1;" alt="Hsini Mohamed" />
      <br /><br />
      <b>Hsini Mohamed</b><br />
      <sub>Morocco 🇲🇦</sub>
    </td>
    <td style="border: none; padding: 12px; vertical-align: middle;">
      <h3 style="margin-top: 0;">🚀 System Architect & Full-Stack Engineer</h3>
      <p style="font-size: 0.95rem; line-height: 1.6; color: #475569;">
        Specializing in high-performance autonomous AI systems, deterministic multi-agent swarms, enterprise cloud architecture, and modern full-stack engineering.
      </p>
      <p>
        <a href="https://hsini.dev"><img src="https://img.shields.io/badge/Portfolio-hsini.dev-2563eb?style=flat-square&logo=google-chrome&logoColor=white" alt="Portfolio" /></a>
        <a href="mailto:contact@hsini.dev"><img src="https://img.shields.io/badge/Email-contact@hsini.dev-ea4335?style=flat-square&logo=gmail&logoColor=white" alt="Email" /></a>
        <a href="https://github.com/hsinidev"><img src="https://img.shields.io/badge/GitHub-@hsinidev-181717?style=flat-square&logo=github&logoColor=white" alt="GitHub" /></a>
        <a href="https://linkedin.com/in/hsinidev/"><img src="https://img.shields.io/badge/LinkedIn-hsinidev-0077b5?style=flat-square&logo=linkedin&logoColor=white" alt="LinkedIn" /></a>
      </p>
    </td>
  </tr>
</table>

---

## 📄 License & Attribution

This project is distributed under the **MIT License**. See [`LICENSE`](LICENSE) for complete terms.

<div align="center">
  <sub>⚡ Designed, architected, and maintained with engineering precision by <b><a href="https://hsini.dev">Hsini Mohamed</a></b>.</sub>
</div>
