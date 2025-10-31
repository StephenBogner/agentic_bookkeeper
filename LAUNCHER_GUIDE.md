# Agentic Bookkeeper Launcher Guide

Quick reference for launching the Agentic Bookkeeper application.

---

## Quick Start

### Windows

Double-click `run_bookkeeper.bat` or run from command prompt:

```cmd
run_bookkeeper.bat
```

### Linux/Mac

Run from terminal:

```bash
./run_bookkeeper.sh
```

---

## What the Launcher Does

The launcher scripts automatically:

1. ✅ Check if virtual environment exists
2. ✅ Activate the virtual environment
3. ✅ Verify the application is installed
4. ✅ Check for configuration files (.env)
5. ✅ Display startup information
6. ✅ Launch the application GUI

---

## Before First Run

### Installation Required

Before using the launcher, you must install the application:

**Windows:**
```cmd
install.bat
```

**Linux/Mac:**
```bash
./install.sh
```

### Configuration Recommended

For the application to work properly, configure your API keys:

1. Copy the sample configuration:
   ```bash
   cp samples/config/.env.sample .env
   ```

2. Edit `.env` and add your API key(s):
   ```
   LLM_PROVIDER=openai
   OPENAI_API_KEY=your-api-key-here
   ```

3. See [docs/user/ENV_SETUP_GUIDE.md](docs/user/ENV_SETUP_GUIDE.md) for detailed instructions

---

## Troubleshooting

### "Virtual environment not found"

**Solution:** Run the installation script first
- Windows: `install.bat`
- Linux/Mac: `./install.sh`

### "Package not installed"

**Solution:** Reinstall the application
```bash
# Activate virtual environment first
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Then reinstall
pip install -e .
```

### ".env file not found" Warning

**Solution:** This is just a warning. The application will start, but you'll need to configure API keys through the GUI Settings dialog or create a `.env` file manually.

### Application won't start

**Check:**
1. Python 3.8+ is installed: `python --version`
2. Virtual environment is activated
3. All dependencies are installed: `pip list | grep agentic-bookkeeper`
4. No other instance is running

### Permission Denied (Linux/Mac)

**Solution:** Make the script executable
```bash
chmod +x run_bookkeeper.sh
```

---

## Alternative Launch Methods

### Method 1: Direct Python

```bash
# Activate virtual environment
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Run directly
python src/agentic_bookkeeper/main.py
```

### Method 2: Console Script

```bash
# After installation, use the console script
agentic_bookkeeper
```

### Method 3: CLI Mode

For command-line operations without GUI:

```bash
# Process documents
python cli.py process /path/to/document.pdf

# Generate reports
python cli.py report --type income --start-date 2025-01-01 --end-date 2025-12-31
```

---

## Launcher Script Features

### Color-Coded Output (Linux/Mac)

- 🔵 **Blue:** Information messages
- 🟢 **Green:** Success messages
- 🟡 **Yellow:** Warnings
- 🔴 **Red:** Errors

### Startup Information

The launcher displays:
- Application mode (GUI)
- Python version being used
- Working directory
- Configuration status

### Error Handling

The launcher will:
- Exit gracefully if prerequisites are missing
- Display helpful error messages
- Provide guidance on how to fix issues

---

## Advanced Usage

### Running from Different Directory

The launchers automatically change to the correct directory, so you can run them from anywhere:

```bash
# Linux/Mac
/path/to/agentic_bookkeeper/run_bookkeeper.sh

# Windows
C:\path\to\agentic_bookkeeper\run_bookkeeper.bat
```

### Creating Desktop Shortcuts

**Windows:**
1. Right-click `run_bookkeeper.bat`
2. Select "Create shortcut"
3. Drag shortcut to Desktop
4. (Optional) Right-click shortcut → Properties → Change Icon

**Linux:**
1. Create `.desktop` file:
   ```bash
   nano ~/.local/share/applications/agentic-bookkeeper.desktop
   ```

2. Add content:
   ```ini
   [Desktop Entry]
   Version=1.0
   Type=Application
   Name=Agentic Bookkeeper
   Comment=Intelligent bookkeeping automation
   Exec=/path/to/agentic_bookkeeper/run_bookkeeper.sh
   Icon=/path/to/icon.png
   Terminal=false
   Categories=Office;Finance;
   ```

**Mac:**
1. Create Automator Application
2. Add "Run Shell Script" action
3. Set script: `/path/to/run_bookkeeper.sh`
4. Save as Application

---

## Support

For more information:

- **User Guide:** [docs/user/USER_GUIDE.md](docs/user/USER_GUIDE.md)
- **Installation Help:** [docs/user/ENV_SETUP_GUIDE.md](docs/user/ENV_SETUP_GUIDE.md)
- **Troubleshooting:** [docs/user/USER_GUIDE.md#troubleshooting](docs/user/USER_GUIDE.md#troubleshooting)
- **GitHub Issues:** [https://github.com/StephenBogner/agentic_bookkeeper/issues](https://github.com/StephenBogner/agentic_bookkeeper/issues)

---

**Quick Tip:** Bookmark this file for easy reference!
