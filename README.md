RAGEMP Toolbox 🛠️

A cleaner, improved README version — now including release info for RageMP Toolbox.exe.

Overview

RAGEMP Toolbox is a Windows-based utility for RAGE Multiplayer and GTA V modding/troubleshooting.
It provides automatic GTA V path detection, a safe Redux mod patcher with backup support, microphone management, troubleshooting tools, and full English/German language support.

🚀 Release — RageMP Toolbox.exe

The standalone executable RageMP Toolbox.exe is available in the GitHub Releases section.

👉 Download: http://github.com/fzer0x/ragemp-toolbox/releases/latest
(replace <user>/<repo> with your repository path)

⚠️ Security Note: Always download the .exe only from the official GitHub repository.



✨ Key Features

GTA V Path Detection

Auto-detects installation paths (Steam, Epic Games, Rockstar Launcher)

Supports manual path entry

Stores configuration in Windows registry

Redux Mod Patcher

Safe file patching with automatic backups

Relative path patching for mod folders

Backup restore functionality

Microphone Management

Device detection with PyAudio

Save preferred microphone to registry

Easy device switching

Troubleshooting Tools

Connection Fix → repairs config.xml issues

LocalPrefs Cleaner → removes broken config files

Windows Compatibility Fix → fixes issues on Windows 7/8

Modern UI

Dark theme with gradients

Real-time logs & progress indicators

Language switch (EN/DE)

📦 Installation
Option 1: Executable (Recommended)

Download RageMP Toolbox.exe from Releases

Run directly (no Python required)

Option 2: From Source
git clone https://github.com/fzer0x/ragemp-toolbox.git
cd ragemp-toolbox
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python main.py

🐛 Troubleshooting

Admin Rights: Some fixes require Administrator privileges

GTA V Not Found: Use manual path if auto-detect fails

Microphone Missing: Check device permissions & connections

Patch Errors: Ensure correct Redux folder structure & enough disk space

Logs: logs/app.log

🤝 Contributing

Fork → Branch → Commit → Pull Request

Follow PEP 8

Add comments for complex logic

Maintain EN/DE translation support

📄 License

MIT License — see LICENSE