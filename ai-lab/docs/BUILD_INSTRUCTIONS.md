# Building AI-Lab Manager as Executable

This guide shows you how to convert the Python script into a standalone Windows executable (.exe) and create shortcuts.

## Quick Start (Easiest Method)

### Step 1: Build the Executable
```bash
scripts\build_exe.bat
```

This will:
- Install PyInstaller if needed
- Create a standalone executable
- Output to `dist\AILab_Manager.exe`

### Step 2: Create Desktop Shortcut
```powershell
powershell -ExecutionPolicy Bypass -File scripts\create_shortcut.ps1
```

That's it! You'll now have a desktop shortcut to launch AI-Lab Manager.

---

## Manual Methods

### Method 1: Using PyInstaller (Recommended)

1. **Install PyInstaller**
   ```bash
   pip install pyinstaller
   ```

2. **Build the executable**
   ```bash
   pyinstaller --onefile --windowed --name="AILab_Manager" ailab_manager.py
   ```

3. **Find your executable**
   - Location: `dist\AILab_Manager.exe`
   - This is a standalone file - you can move it anywhere!

4. **Create a shortcut**
   - Right-click on `AILab_Manager.exe`
   - Select "Create shortcut"
   - Move shortcut to Desktop or Start Menu

### Method 2: Using the Spec File

For advanced customization:
```bash
pyinstaller AILab_Manager.spec
```

---

## What Gets Built?

### Executable Details
- **Name**: `AILab_Manager.exe`
- **Type**: Standalone Windows executable
- **Size**: ~15-20 MB (includes Python runtime)
- **Location**: `dist\AILab_Manager.exe`

### Dependencies Included
The executable bundles:
- Python runtime
- tkinter GUI framework
- All required Python packages
- Configuration file template

### What's NOT Included
- ComfyUI itself (installed when you click Install ComfyUI)
- AI Toolkit itself (installed when you click Install AI Toolkit)
- Git, Node.js (checked at runtime)
- Your saved configurations (reads ailab_config.json from exe directory)

---

## Distribution

### Single File Distribution
After building, you can distribute just the `.exe` file:

1. Copy `dist\AILab_Manager.exe` to any location
2. Run it directly - no Python installation needed
3. First-time users will see the installation wizard for each tool

### With Pre-configured Settings
To distribute with default settings:

1. Run the manager once and configure both tools
2. Copy both:
   - `dist\AILab_Manager.exe`
   - `ailab_config.json`
3. Place them in the same folder
4. The exe will read the config automatically

---

## Troubleshooting

### "PyInstaller is not recognized"
**Solution**: Install PyInstaller first
```bash
pip install pyinstaller
```

### "Python is not recognized"
**Solution**: Install Python 3.x and add it to PATH

### Build fails with module errors
**Solution**: Install required dependencies
```bash
pip install -r requirements.txt
```

### Executable won't start
**Possible causes:**
1. Antivirus blocking (add exception)
2. Missing Visual C++ Runtime (install from Microsoft)
3. Corrupted build (delete `build` and `dist` folders, rebuild)

### Shortcut creation fails
**Solution**: Run PowerShell script as administrator
```powershell
powershell -ExecutionPolicy Bypass -File scripts\create_shortcut.ps1
```

---

## Advanced Options

### Custom Icon
To add a custom icon to your executable:

1. Get an `.ico` file (Windows icon format)
2. Modify the build command:
   ```bash
   pyinstaller --onefile --windowed --icon=myicon.ico --name="AILab_Manager" ailab_manager.py
   ```

### Console Window (for debugging)
To show a console window (useful for debugging):
```bash
pyinstaller --onefile --icon=NONE --name="AILab_Manager" ailab_manager.py
```
(Remove `--windowed` flag)

### Smaller Executable
To reduce executable size:
```bash
pyinstaller --onefile --windowed --exclude-module matplotlib --exclude-module numpy --name="AILab_Manager" ailab_manager.py
```

### Using the .spec File
For advanced customization, edit `AILab_Manager.spec` and build with:
```bash
pyinstaller AILab_Manager.spec
```

---

## File Structure After Build

```
ai-lab/
├── dist/
│   └── AILab_Manager.exe        ← Your standalone executable
├── build/                        ← Temporary build files (can delete)
├── scripts/
│   ├── build_exe.bat            ← Build script
│   ├── create_shortcut.ps1      ← Shortcut creator
│   └── start_manager.bat        ← Python script launcher
├── docs/
│   ├── BUILD_INSTRUCTIONS.md    ← This file
│   └── README.md                ← User guide
├── ailab_manager.py             ← Source Python script
├── ailab_config.json            ← Configuration file
├── AILab_Manager.spec           ← PyInstaller spec file
└── requirements.txt             ← Python dependencies
```

---

## Notes

- **First build takes longer**: PyInstaller analyzes all dependencies
- **Subsequent builds are faster**: Cached data speeds up the process
- **Safe to delete**: `build/` folder (regenerated on each build)
- **Keep for distribution**: `dist/AILab_Manager.exe` only
- **Config persistence**: The exe reads/writes `ailab_config.json` in its directory

---

## Questions?

- **Can I move the exe?** Yes, anywhere! It's completely standalone.
- **Will it update itself?** No, rebuild after updating the Python script.
- **Can others use it?** Yes, they don't need Python installed.
- **Does it work on other Windows versions?** Yes, Windows 7 and later.
- **Can I install both tools at once?** Yes, use separate tabs for each tool.
