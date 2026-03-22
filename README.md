# ⚡ Telegram ExactTime Scheduler

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white)
![Telethon](https://img.shields.io/badge/Telethon-MTProto-blue?logo=telegram&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Windows-0078D6?logo=windows&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

**A GUI tool to send Telegram messages at a precise, exact time — down to the millisecond.**

*Syncs with Telegram's own server clock to eliminate timing errors caused by local PC clock drift.*

</div>

---

## 🎯 What Does It Do?

This tool lets you schedule a Telegram message to fire at an **exact target time** (e.g., `02:00:00.000 AM`) using Telegram's own MTProto API. Unlike Telegram's built-in scheduler (which only supports minute-level precision), this app fires your message with **millisecond accuracy**.

### ✅ Key Features
- 🕒 **Millisecond-precision scheduling** — set time to HH:MM:SS.mmm
- 🌐 **Server clock sync** — measures your PC's offset against Telegram's server and auto-corrects
- 🔐 **Secure credentials** — API keys are masked by default (show/hide toggle)
- 💾 **Saves your settings** — auto-saves last used target and message to `settings.json`
- 🔄 **Session persistence** — no need to log in every time (Telethon session files)
- ❌ **Cancel anytime** — cancel button stops the scheduler before it fires

---

## 🖥️ Screenshots

> *The GUI is simple and clean — just fill in your API credentials, target, message, and time.*

---

## ⚙️ How It Works

1. **Connect** — App connects to Telegram using your API credentials (MTProto via Telethon)
2. **Login** — Handles OTP and 2FA safely via GUI dialogs
3. **Pre-resolve target** — Resolves `@username` or phone number early (no delay at fire time)
4. **Clock sync** — Sends 3 test messages to `Saved Messages` to measure your PC's clock offset vs Telegram's server
5. **High-precision wait** — Uses a tiered sleep strategy:
   - `>2s` → coarse sleep
   - `>100ms` → 5ms intervals
   - `>1ms` → 0.5ms intervals
   - `<1ms` → tight CPU spin-wait
6. **Fire!** — Sends the message at the adjusted server time and reports results

---

## 🚀 Getting Started

### Prerequisites
- Python 3.8 or higher
- A Telegram account
- Your Telegram API credentials (see below)

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/EyachirArafat/telegram-exact-scheduler.git
cd telegram-exact-scheduler

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the app
python telegram_exact_scheduler.pyw
```

### Getting Your API Credentials

See the included [`How_To_Get_API_Credentials.md`](How_To_Get_API_Credentials.md) for step-by-step guide, or:

1. Go to [https://my.telegram.org/auth](https://my.telegram.org/auth)
2. Log in with your phone number
3. Click **"API development tools"**
4. Create an app (any name/platform)
5. Copy your **API ID** and **API Hash**

---

## 📁 Project Structure

```
telegram-exact-scheduler/
│
├── telegram_exact_scheduler.pyw   # Main application (windowless GUI)
├── requirements.txt               # Python dependencies
├── How_To_Get_API_Credentials.md # Guide to get Telegram API keys
├── settings.json                  # Auto-saved settings (DO NOT commit yours)
├── session_files/                 # Telethon session files (auto-created, gitignored)
└── .gitignore
```

---

## 🔒 Security & Privacy

> [!CAUTION]
> **Never share or commit `settings.json` or `session_files/`!**
> These files contain your Telegram credentials and active session tokens.
> They are already listed in `.gitignore` to prevent accidental upload.

---

## 📦 Dependencies

| Package | Purpose |
|---------|---------|
| `telethon` | Telegram MTProto API client |
| `tkinter` | GUI framework (included with Python) |

Install with:
```bash
pip install telethon
```

---

## 🏗️ Building an EXE (Windows Only)

You can package this into a standalone `.exe` using PyInstaller:

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name="TelegramExactScheduler" telegram_exact_scheduler.pyw
```

The `.exe` will be in the `dist/` folder.

---

## 📄 License

This project is licensed under the **MIT License** — free to use, modify, and distribute.

---

## 🙋 Author

Made with ❤️ for precise Telegram automation.

> If this tool helped you, consider giving it a ⭐ on GitHub!
