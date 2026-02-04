# Building AI-Lab Manager as Executable

This guide shows you how to convert the Python script into a fully self-contained Windows executable (.exe) that includes all dependencies.

## Quick Start (Easiest Method)

### Step 1: Build the Executable
```bash
scripts\build_exe.bat
```

This will:
- Auto-detect if you're using a virtual environment
- Install PyInstaller if needed
- Ensure all dependencies are installed
- Create a **fully self-contained** executable with embedded:
  - Python runtime
  - tkinter GUI framework
  - ttkbootstrap themes
  - psutil library
  - All Python dependencies
- Output to `dist\AILab_Manager.exe`

### Step 2: Create Desktop Shortcut (Optional)
```powershell
powershell -ExecutionPolicy Bypass -File scripts\create_shortcut.ps1
```

That's it! You now have a standalone executable that works on **any Windows machine without Python installed**.

---

## Virtual Environment Builds (Recommended)

For the cleanest build with isolated dependencies:

### 1. Setup Virtual Environment
```bash
scripts\setup_venv.bat
```

### 2. Build from Virtual Environment
```bash
scripts\build_exe.bat
```

When prompted, choose **Yes** to use the virtual environment.

**Benefits**:
- ✅ No interference from global Python packages
- ✅ Reproducible builds
- ✅ Clean dependency isolation
- ✅ Same self-contained exe output

---

## What Gets Built?

### Executable Details
- **Name**: `AILab_Manager.exe`
- **Type**: Single-file, fully self-contained Windows executable
- **Size**: ~25-30 MB (includes everything needed)
- **Location**: `dist\AILab_Manager.exe`
- **Requirements on target machine**: **NONE** - no Python needed!

### Dependencies INCLUDED in Executable
✅ Python 3.10+ runtime  
✅ tkinter GUI framework  
✅ ttkbootstrap (modern themes)  
✅ psutil (process management)  
✅ All required Python libraries  

### What's NOT Included (Installed at Runtime)
❌ ComfyUI itself (installed when you click Install ComfyUI)  
❌ AI Toolkit itself (installed when you click Install AI Toolkit)  
❌ Git, Node.js (checked at runtime, prompts if missing)  
❌ Your saved configurations (reads ailab_config.json from exe directory)  

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

## Troubleshooting

### "PyInstaller is not recognized"
**Solution**: Install PyInstaller first
```bash
pip install pyinstaller
```

### "Python is not recognized"
**Solution**: Install Python 3.10+ and add it to PATH

### Build fails with module errors
**Solution**: Install required dependencies
```bash
pip install -r requirements.txt
```

Or use virtual environment (see [VENV_SETUP.md](VENV_SETUP.md))

### Executable won't start
**Possible causes:**
1. Antivirus blocking (add exception for PyInstaller and the exe)
2. Missing Visual C++ Runtime (install from Microsoft)
3. Corrupted build (delete `build` and `dist` folders, rebuild)
4. Hidden imports missing (already configured in spec file)

### Build is too large
The spec file already excludes unnecessary packages like matplotlib, numpy, pandas, etc.

**If you need to reduce size further**:
- Remove ttkbootstrap themes (use plain tkinter)
- Disable UPX compression in spec file: `upx=False`

### Shortcut creation fails
**Solution**: Run PowerShell script as administrator
```powershell
powershell -ExecutionPolicy Bypass -File scripts\create_shortcut.ps1
```

---

## Advanced Configuration

### Custom Icon
To add a custom icon to your executable:

1. Get an `.ico` file (Windows icon format)
2. Update `AILab_Manager.spec`:
   ```python
   icon='path/to/myicon.ico',
   ```
3. Rebuild:
   ```bash
   pyinstaller AILab_Manager.spec
   ```

### Console Window (for debugging)
To show a console window (useful for debugging):

In `AILab_Manager.spec`, change:
```python
console=True,  # Changed from False
```

### Exclude More Packages
Edit the `excludes` list in `AILab_Manager.spec`:
```python
excludes=[
    'matplotlib',
    'numpy',
    'pandas',
    'scipy',
    'IPython',
    'jupyter',
    # Add more here
],
```

---

## Technical Details

### PyInstaller Spec File
The `AILab_Manager.spec` file controls the build process:

- **hiddenimports**: Ensures ttkbootstrap and dependencies are included
- **excludes**: Removes unnecessary packages (matplotlib, numpy, etc.)
- **upx=True**: Compresses the executable
- **console=False**: No console window (GUI only)
- **onefile**: Single executable (all-in-one)

### Why Self-Contained?
The spec file explicitly includes all imports:
```python
hiddenimports=[
    'ttkbootstrap',
    'ttkbootstrap.scrolled',
    'psutil',
    'tkinter',
    'tkinter.ttk',
    'tkinter.scrolledtext',
],
```

This ensures the executable works **without any Python installation** on target machines.

---

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
