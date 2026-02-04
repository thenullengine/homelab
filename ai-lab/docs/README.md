# AI-Lab Manager

A unified Python GUI application for easy installation and management of both ComfyUI and AI Toolkit.

## Features

- **Unified Interface**: Manage both ComfyUI and AI Toolkit from a single application
- **Tabbed Design**: Separate tabs for each tool with dedicated controls
- **One-Click Installation**: Automated installation of both tools with all dependencies
- **GPU Support**: Installs PyTorch with CUDA support for both tools
- **Easy Management**: Start, update, and manage both tools from a simple GUI
- **Progress Logging**: Real-time installation and operation logs per tool
- **Persistent Configuration**: Save and load settings for both tools

## Requirements

Before running the AI-Lab Manager, ensure you have:

- **Windows 10/11**
- **Git** (required for cloning repositories)
- **Node.js** (required for AI Toolkit, will be installed if missing)
- **Python 3.8+** (with tkinter)
- **NVIDIA GPU** with CUDA support (recommended)

## Quick Start

### Option 1: Using the GUI (Recommended)

1. Run the GUI manager:
   ```bash
   python ailab_manager.py
   ```
   Or use the launcher:
   ```bash
   scripts\start_manager.bat
   ```

2. Choose the tool you want to install (ComfyUI or AI Toolkit tab)

3. Configure installation directories and settings

4. Click "Install" button for the desired tool

5. Once installed, click "Start" to launch the tool

### Option 2: Building as Executable

1. Build the executable:
   ```bash
   scripts\build_exe.bat
   ```

2. Create desktop shortcut:
   ```bash
   powershell -ExecutionPolicy Bypass -File scripts\create_shortcut.ps1
   ```

3. Run `dist\AILab_Manager.exe`

## ComfyUI Features

### Configuration Options
- **Parent Directory**: Where ComfyUI will be installed
- **User Directory**: Custom workflows location
- **Output Directory**: Generated images location
- **Input Directory**: Input images location
- **Extra Model Paths**: YAML file for additional model locations
- **Quick Install**: Skip optional custom nodes for faster installation
- **VRAM Mode**: Choose between normal, high, low, or no VRAM modes

### Buttons
- **Install ComfyUI**: Run complete installation with custom nodes
- **Start ComfyUI**: Launch ComfyUI server and open browser
- **Open Browser**: Open ComfyUI interface at http://127.0.0.1:8188

### Custom Nodes

Must-have nodes (always installed):
- ComfyUI-Manager
- rgthree-comfy
- ComfyUI-Impact-Pack
- ComfyUI-KJNodes
- ComfyUI-SAM3
- ComfyUI-Inpaint-CropAndStitch
- ComfyUI_essentials
- comfyui_controlnet_aux
- ComfyUI-Custom-Scripts
- ComfyUI_UltimateSDUpscale
- ComfyUI_LayerStyle
- comfyui-inpaint-nodes
- comfyui-tooling-nodes

Additional nodes (installed if "Quick Install" is unchecked):
- Over 30+ additional nodes for video, face swap, GGUF models, and more

## AI Toolkit Features

### Configuration Options
- **Installation Directory**: Where AI Toolkit will be installed
- AI Toolkit uses embedded Python 3.12.10 for isolated environment

### Buttons
- **Install AI Toolkit**: Run complete installation with embedded Python
- **Start AI Toolkit**: Launch AI Toolkit UI
- **Update AI Toolkit**: Update to latest version from GitHub
- **Open Browser**: Open AI Toolkit interface at http://localhost:8675

### What Gets Installed
- Embedded Python 3.12.10
- PyTorch 2.8.0 with CUDA 12.8
- AI Toolkit from GitHub
- All required dependencies via pip/uv
- Startup and update batch scripts

## Configuration File

The manager uses `ailab_config.json` to store settings:

```json
{
    "comfyui": {
        "install_parent_dir": "",
        "user_directory": "D:\\_AI\\user",
        "output_directory": "D:\\_AI\\output",
        "input_directory": "D:\\_AI\\input",
        "extra_model_paths": "",
        "quick_install": false,
        "vram_mode": "--normalvram"
    },
    "aitoolkit": {
        "install_parent_dir": ""
    }
}
```

## Installation Locations

### ComfyUI
- Installed to: `[parent_dir]/ComfyUI/`
- Contains: venv, main.py, custom_nodes/

### AI Toolkit  
- Installed to: `[parent_dir]/AI-Toolkit/`
- Contains: ai-toolkit/, python_embeded/, startup scripts

## Logs

Each tab has its own log output showing:
- Installation progress
- Package installations
- Error messages
- Status updates

Use the "Clear Log" button to clean up the log view.

## Troubleshooting

### "Git is not installed"
Install Git from https://git-scm.com/

### "Python is not recognized"
Install Python 3.8+ and ensure "Add to PATH" is checked during installation.

### ComfyUI won't start
- Verify installation completed successfully
- Check that venv exists in ComfyUI folder
- Review log for error messages

### AI Toolkit won't start
- Verify python_embeded folder exists
- Check that ai-toolkit folder exists
- Review log for error messages

### Antivirus blocking executable
Add exception for AILab_Manager.exe in your antivirus software.

## Development

### Running from Source
```bash
python ailab_manager.py
```

### Building Executable
```bash
scripts\build_exe.bat
```

### Requirements
- Python 3.8+
- tkinter (usually included with Python)

## License

This manager is a convenience tool for installing:
- ComfyUI: https://github.com/comfyanonymous/ComfyUI
- AI Toolkit: https://github.com/ostris/ai-toolkit

Please refer to each project's license for usage terms.

## Credits

- ComfyUI by comfyanonymous
- AI Toolkit by Ostris
- Manager GUI by thenullengine
