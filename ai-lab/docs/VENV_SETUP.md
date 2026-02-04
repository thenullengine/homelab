# Virtual Environment Setup Guide

This guide explains how to use Python virtual environments with AI Lab Manager.

## Why Use a Virtual Environment?

✅ **Isolated Dependencies** - Keep project dependencies separate from system Python  
✅ **No Conflicts** - Avoid version conflicts with other Python projects  
✅ **Clean Development** - Easy to recreate or remove without affecting system  
✅ **Best Practice** - Standard approach for Python development

## Quick Start

### 1. Create and Setup Virtual Environment

```bat
scripts\setup_venv.bat
```

This will:
- Create a `venv` folder with isolated Python environment
- Upgrade pip to latest version
- Install all required dependencies from `requirements.txt`

### 2. Run AI Lab Manager

```bat
scripts\start_manager_venv.bat
```

This automatically:
- Activates the virtual environment
- Launches the AI Lab Manager
- Deactivates on exit

## Manual Virtual Environment Usage

### Activate Virtual Environment

```bat
venv\Scripts\activate
```

Your prompt will change to show `(venv)` prefix.

### Deactivate Virtual Environment

```bat
deactivate
```

### Install New Packages

While activated:
```bat
pip install package-name
```

### Update Requirements

After installing new packages:
```bat
pip freeze > requirements.txt
```

## Building Executable with Virtual Environment

The build script automatically detects and offers to use your virtual environment:

```bat
scripts\build_exe.bat
```

You'll be prompted:
- **Yes** - Build using venv (recommended if you've customized dependencies)
- **No** - Build using global Python installation

The resulting `.exe` is **always self-contained** regardless of which option you choose.

## Troubleshooting

### Virtual Environment Won't Create

**Error**: `No module named venv`

**Solution (Windows)**:
```bat
python -m pip install --upgrade pip
```

Python on Windows usually includes venv by default. If not, reinstall Python and ensure "pip" and "tcl/tk" are selected.

### Dependencies Won't Install

**Check Internet Connection**: pip needs to download packages

**Update pip first**:
```bat
venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Wrong Python Version in venv

Delete the venv folder and recreate:
```bat
rmdir /s venv
scripts\setup_venv.bat
```

## File Structure

```
ai-lab/
├── venv/                      # Virtual environment (gitignored)
│   ├── Scripts/              # Executables and activation scripts
│   ├── Lib/                  # Installed packages
│   └── pyvenv.cfg           # Configuration
├── requirements.txt          # Package dependencies
├── ailab_manager.py         # Main application
└── scripts/
    ├── setup_venv.bat       # Create and setup venv
    ├── start_manager_venv.bat  # Run with venv
    └── build_exe.bat        # Build (can use venv)
```

## Best Practices

1. **Always use venv for development** - Keeps your system Python clean
2. **Update requirements.txt** - When you add new dependencies
3. **Recreate venv if corrupted** - Just delete the folder and run setup again
4. **Don't commit venv folder** - It's already in .gitignore
5. **Use venv for building exe** - Ensures consistent builds

## Global Python vs Virtual Environment

| Aspect | Global Python | Virtual Environment |
|--------|--------------|---------------------|
| Setup | None needed | One-time setup |
| Dependencies | Shared across all projects | Isolated per project |
| Conflicts | Possible | None |
| Development | Quick start | Best practice |
| Building | Works | Recommended |
| Distribution | Same exe output | Same exe output |

## Scripts Summary

| Script | Purpose | Uses venv? |
|--------|---------|-----------|
| `setup_venv.bat` | Create virtual environment | Creates it |
| `start_manager_venv.bat` | Run with venv | Yes |
| `start_manager.bat` | Run with global Python | No |
| `build_exe.bat` | Build executable | Optional (asks) |

---

**Recommendation**: Use virtual environments for development, but either method works fine. The built executable is always fully self-contained regardless of how you build it.
