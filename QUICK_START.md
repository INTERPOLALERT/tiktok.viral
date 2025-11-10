# CreatorStudio AI - Quick Start Guide for Windows

## 🚀 Super Easy Installation (2 Steps!)

### Step 1: Install Dependencies
Double-click **`INSTALL.BAT`**

This will:
- Check if Python is installed
- Upgrade pip to latest version
- Install all required dependencies automatically
- Takes 2-5 minutes depending on your internet speed

### Step 2: Start the Application
Double-click **`START.BAT`**

That's it! The application will launch.

---

## 📋 Detailed Instructions

### First Time Setup

1. **Install Python** (if not already installed)
   - Download from: https://www.python.org/downloads/
   - **IMPORTANT**: Check "Add Python to PATH" during installation
   - Requires Python 3.9 or higher

2. **Run Installation**
   - Double-click `INSTALL.BAT`
   - Wait for installation to complete
   - You'll see "Installation Complete!" when done

3. **Launch Application**
   - Double-click `START.BAT`
   - The CreatorStudio AI window will open

4. **Configure API Keys** (Optional but recommended)
   - Click on the "Settings" tab
   - Enter your OpenAI API key
   - Click "Save Settings"

5. **Start Creating!**
   - Explore the Dashboard
   - Create your first project
   - Generate content with AI

---

## 🎯 What Each File Does

### INSTALL.BAT
- Checks Python installation
- Installs all dependencies from `requirements.txt`
- Only needs to be run once (unless updating dependencies)

### START.BAT
- Checks if dependencies are installed
- Launches the CreatorStudio AI application
- Shows helpful error messages if issues occur
- Use this every time you want to run the app

---

## 🔧 Alternative: Manual Commands

If you prefer using Command Prompt:

```batch
# Install dependencies
python -m pip install -r requirements.txt

# Run the application
python main.py
```

---

## ⚠️ Troubleshooting

### "Python is not recognized"
**Problem**: Python not in PATH

**Solution**:
1. Reinstall Python from python.org
2. Check "Add Python to PATH" during installation
3. OR add Python to PATH manually

### "Failed to install dependencies"
**Problem**: Internet connection or pip issue

**Solution**:
```batch
# Try upgrading pip first
python -m pip install --upgrade pip

# Then run install again
INSTALL.BAT
```

### "Application crashes on startup"
**Problem**: Missing dependencies or corrupted installation

**Solution**:
```batch
# Reinstall dependencies
python -m pip install -r requirements.txt --force-reinstall
```

### "Import Error" messages
**Problem**: Dependencies not fully installed

**Solution**:
Run `INSTALL.BAT` again

---

## 📁 File Structure

```
CreatorStudio AI/
├── INSTALL.BAT          ← Run this first (installs dependencies)
├── START.BAT            ← Run this to launch app
├── QUICK_START.md       ← This file
├── main.py              ← Main application file
├── requirements.txt     ← List of dependencies
├── README.md            ← Full documentation
└── src/                 ← Application source code
```

---

## 🎨 First Time Using the App?

### Quick Tour:

1. **Dashboard** - Overview of your content and stats
2. **Video Studio** - Create and edit videos
3. **Image Studio** - Generate and edit images with AI
4. **Script Writer** - AI-powered content writing
5. **Audio Studio** - Text-to-speech and audio editing
6. **Social Media** - Schedule posts across platforms
7. **Analytics** - Track performance and insights
8. **Trends** - Discover trending topics
9. **Projects** - Organize your content
10. **Settings** - Configure the application

### Try This First:
1. Go to **Script Writer** tab
2. Enter a topic (e.g., "How to grow on TikTok")
3. Click "Generate Script"
4. See AI create a full script in seconds!

---

## 💡 Pro Tips

- **No API Key Yet?** The app works without AI features, you can explore the UI
- **Save Often**: Enable auto-save in Settings
- **Organize**: Create projects for different campaigns
- **Explore**: Try each module to see all features
- **Learn**: Check README.md for detailed documentation

---

## 🆘 Need Help?

1. **Check Logs**: Look in `logs/` folder for error details
2. **Read README.md**: Comprehensive documentation
3. **TECHNICAL_DOCUMENTATION.md**: For developers
4. **SECURITY_AUDIT.md**: Security information

---

## 🎉 You're Ready!

1. Run `INSTALL.BAT`
2. Run `START.BAT`
3. Start creating amazing content!

**Enjoy CreatorStudio AI!** 🚀
