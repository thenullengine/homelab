"""
AI Lab Manager - Unified GUI
Combines ComfyUI Manager and AI Toolkit Manager in a single tabbed interface
"""

import sys

# Check Python version before any other imports
if sys.version_info < (3, 10):
    print("=" * 60)
    print("ERROR: Python 3.10 or higher is required!")
    print(f"Current version: Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    print("=" * 60)
    print("\nPlease upgrade Python to version 3.10 or higher.")
    print("Download from: https://www.python.org/downloads/")
    input("\nPress Enter to exit...")
    sys.exit(1)

import tkinter as tk
from tkinter import filedialog, messagebox
try:
    import ttkbootstrap as ttk
    from ttkbootstrap.scrolled import ScrolledText
    THEME_AVAILABLE = True
except ImportError:
    from tkinter import ttk, scrolledtext
    ScrolledText = scrolledtext.ScrolledText
    THEME_AVAILABLE = False
import json
import os
import sys
import subprocess
import threading
from pathlib import Path


class AILabManager:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Lab Manager")
        self.root.geometry("950x750")
        
        # Config file path - load config first
        self.config_file = Path(__file__).parent / "ailab_config.json"
        self.load_config()
        
        # Apply modern theme if available
        if THEME_AVAILABLE:
            self.style = ttk.Style()
            theme = self.config.get('theme', 'darkly')
            self.style.theme_use(theme)
        
        # Initialize StringVars for settings
        self.init_settings_vars()
        
        # Track installation/operation status
        self.comfyui_installing = False
        self.comfyui_starting = False
        self.aitoolkit_installing = False
        self.aitoolkit_starting = False
        self.onetrainer_installing = False
        self.onetrainer_starting = False
        
        # Track log monitoring
        self.comfyui_monitoring = False
        self.aitoolkit_monitoring = False
        self.onetrainer_monitoring = False
        
        # Track running processes
        self.comfyui_process = None
        self.aitoolkit_process = None
        self.onetrainer_process = None
        
        # Create UI
        self.create_widgets()
    
    def init_settings_vars(self):
        """Initialize all settings variables"""
        # ComfyUI settings
        self.comfyui_install_parent_var = tk.StringVar(value=self.config["comfyui"]["install_parent_dir"])
        self.comfyui_user_dir_var = tk.StringVar(value=self.config["comfyui"]["user_directory"])
        self.comfyui_output_dir_var = tk.StringVar(value=self.config["comfyui"]["output_directory"])
        self.comfyui_input_dir_var = tk.StringVar(value=self.config["comfyui"]["input_directory"])
        self.comfyui_extra_model_paths_var = tk.StringVar(value=self.config["comfyui"]["extra_model_paths"])
        self.comfyui_quick_install_var = tk.BooleanVar(value=self.config["comfyui"]["quick_install"])
        self.comfyui_vram_mode_var = tk.StringVar(value=self.config["comfyui"]["vram_mode"])
        
        # AI Toolkit settings
        self.aitoolkit_install_parent_var = tk.StringVar(value=self.config["aitoolkit"]["install_parent_dir"])
        
        # OneTrainer settings
        self.onetrainer_install_parent_var = tk.StringVar(value=self.config["onetrainer"]["install_parent_dir"])
        
        # Theme settings
        self.theme_var = tk.StringVar(value=self.config.get("theme", "darkly"))

    def load_config(self):
        """Load configuration from JSON file"""
        default_config = {
            "theme": "darkly",
            "comfyui": {
                "install_parent_dir": str(Path(__file__).parent),
                "user_directory": "D:\\_AI\\user",
                "output_directory": "D:\\_AI\\output",
                "input_directory": "D:\\_AI\\input",
                "extra_model_paths": str(Path(__file__).parent / "extra_model_paths_personal.yaml"),
                "quick_install": False,
                "vram_mode": "--normalvram"
            },
            "aitoolkit": {
                "install_parent_dir": str(Path(__file__).parent)
            },
            "onetrainer": {
                "install_parent_dir": str(Path(__file__).parent)
            }
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    self.config = json.load(f)
                # Merge with defaults for any missing keys
                for section, values in default_config.items():
                    if section not in self.config:
                        self.config[section] = values
                    elif isinstance(values, dict):
                        # Only iterate if values is a dict (not for 'theme' which is a string)
                        for key, value in values.items():
                            if key not in self.config[section]:
                                self.config[section][key] = value
            except Exception as e:
                messagebox.showerror("Config Error", f"Error loading config: {e}\nUsing defaults.")
                self.config = default_config
        else:
            self.config = default_config
            self.save_config()
    
    def save_config(self):
        """Save configuration to JSON file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, separators=(',', ': '), indent=4, fp=f)
        except Exception as e:
            messagebox.showerror("Config Error", f"Error saving config: {e}")
    
    def create_widgets(self):
        """Create all GUI widgets"""
        # Create menu bar
        self.create_menu_bar()
        
        # Main container with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1) # Ensure notebook row expands
        
        # Top bar for title and theme selector
        top_bar = ttk.Frame(main_frame)
        top_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        top_bar.columnconfigure(0, weight=1)
        
        # Title
        title_label = ttk.Label(top_bar, text="AI Lab Manager", font=('Arial', 18, 'bold'))
        title_label.grid(row=0, column=0, sticky=tk.W)
        
        # Theme Selector
        if THEME_AVAILABLE:
            theme_frame = ttk.Frame(top_bar)
            theme_frame.grid(row=0, column=1, sticky=tk.E)
            
            ttk.Label(theme_frame, text="Theme:").pack(side=tk.LEFT, padx=(0, 5))
            
            themes = self.style.theme_names()
            theme_combo = ttk.Combobox(theme_frame, textvariable=self.theme_var, values=themes, width=15, state="readonly")
            theme_combo.pack(side=tk.LEFT)
            theme_combo.bind("<<ComboboxSelected>>", self.on_theme_select)
        
        # Create notebook (tabbed interface)
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create tabs
        self.comfyui_tab = ttk.Frame(self.notebook, padding="10")
        self.aitoolkit_tab = ttk.Frame(self.notebook, padding="10")
        self.onetrainer_tab = ttk.Frame(self.notebook, padding="10")
        
        self.notebook.add(self.comfyui_tab, text="ComfyUI")
        self.notebook.add(self.aitoolkit_tab, text="AI Toolkit")
        self.notebook.add(self.onetrainer_tab, text="OneTrainer")
        
        # Configure tab weights
        self.comfyui_tab.columnconfigure(0, weight=1)
        self.comfyui_tab.rowconfigure(1, weight=1)
        self.aitoolkit_tab.columnconfigure(0, weight=1)
        self.aitoolkit_tab.rowconfigure(1, weight=1)
        self.onetrainer_tab.columnconfigure(0, weight=1)
        self.onetrainer_tab.rowconfigure(1, weight=1)
        
        # Build ComfyUI tab
        self.create_comfyui_tab()
        
        # Build AI Toolkit tab
        self.create_aitoolkit_tab()
        
        # Build OneTrainer tab
        self.create_onetrainer_tab()
    
    def create_menu_bar(self):
        """Create the menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Settings menu
        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Settings", menu=settings_menu)
        settings_menu.add_command(label="ComfyUI Settings", command=self.show_comfyui_settings)
        settings_menu.add_command(label="AI Toolkit Settings", command=self.show_aitoolkit_settings)
        settings_menu.add_command(label="OneTrainer Settings", command=self.show_onetrainer_settings)
        settings_menu.add_separator()
        settings_menu.add_command(label="Exit", command=self.root.quit)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        if not THEME_AVAILABLE:
            help_menu.add_separator()
            help_menu.add_command(label="Install ttkbootstrap for modern themes", command=self.show_theme_install_help)
    
    def create_comfyui_tab(self):
        """Create ComfyUI tab content"""
        # Action Buttons (grid layout for square appearance)
        button_frame = ttk.Frame(self.comfyui_tab)
        button_frame.grid(row=0, column=0, pady=20)
        
        # Row 1
        if THEME_AVAILABLE:
            self.comfyui_install_btn = ttk.Button(button_frame, text="Install\nComfyUI", 
                                                  command=self.install_comfyui, bootstyle="success", width=12, padding=10)
        else:
            self.comfyui_install_btn = ttk.Button(button_frame, text="Install\nComfyUI", 
                                                  command=self.install_comfyui, width=12)
        self.comfyui_install_btn.grid(row=0, column=0, padx=10, pady=10)
        
        if THEME_AVAILABLE:
            self.comfyui_start_btn = ttk.Button(button_frame, text="Start\nComfyUI", 
                                                command=self.start_comfyui, bootstyle="primary", width=12, padding=10)
        else:
            self.comfyui_start_btn = ttk.Button(button_frame, text="Start\nComfyUI", 
                                                command=self.start_comfyui, width=12)
        self.comfyui_start_btn.grid(row=0, column=1, padx=10, pady=10)
        
        if THEME_AVAILABLE:
            self.comfyui_browser_btn = ttk.Button(button_frame, text="Open\nBrowser", 
                                                  command=self.open_comfyui_browser, bootstyle="info", width=12, padding=10)
        else:
            self.comfyui_browser_btn = ttk.Button(button_frame, text="Open\nBrowser", 
                                                  command=self.open_comfyui_browser, width=12)
        self.comfyui_browser_btn.grid(row=0, column=2, padx=10, pady=10)
        
        if THEME_AVAILABLE:
            self.comfyui_stop_btn = ttk.Button(button_frame, text="Stop\nComfyUI", 
                                               command=self.stop_comfyui, bootstyle="danger", width=12, padding=10)
        else:
            self.comfyui_stop_btn = ttk.Button(button_frame, text="Stop\nComfyUI", 
                                               command=self.stop_comfyui, width=12)
        self.comfyui_stop_btn.grid(row=0, column=3, padx=10, pady=10)
        
        if THEME_AVAILABLE:
            self.comfyui_restart_btn = ttk.Button(button_frame, text="Restart\nComfyUI", 
                                                  command=self.restart_comfyui, bootstyle="warning", width=12, padding=10)
        else:
            self.comfyui_restart_btn = ttk.Button(button_frame, text="Restart\nComfyUI", 
                                                  command=self.restart_comfyui, width=12)
        self.comfyui_restart_btn.grid(row=0, column=4, padx=10, pady=10)
        
        # Output Log
        log_frame = ttk.LabelFrame(self.comfyui_tab, text="ComfyUI Output Log", padding="10")
        log_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        if THEME_AVAILABLE:
            self.comfyui_log_text = ScrolledText(log_frame, wrap=tk.WORD, height=20, autohide=True)
        else:
            self.comfyui_log_text = ScrolledText(log_frame, wrap=tk.WORD, height=20)
        self.comfyui_log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Clear log button
        ttk.Button(log_frame, text="Clear Log", command=lambda: self.comfyui_log_text.delete(1.0, tk.END)).grid(row=1, column=0, pady=(5, 0))
    
    def create_aitoolkit_tab(self):
        """Create AI Toolkit tab content"""
        # Action Buttons (all on one line)
        button_frame = ttk.Frame(self.aitoolkit_tab)
        button_frame.grid(row=0, column=0, pady=20)
        
        # All buttons in row 0
        if THEME_AVAILABLE:
            self.aitoolkit_install_btn = ttk.Button(button_frame, text="Install\nAI Toolkit", 
                                                    command=self.install_aitoolkit, bootstyle="success", width=12, padding=10)
        else:
            self.aitoolkit_install_btn = ttk.Button(button_frame, text="Install\nAI Toolkit", 
                                                    command=self.install_aitoolkit, width=12)
        self.aitoolkit_install_btn.grid(row=0, column=0, padx=10, pady=10)
        
        if THEME_AVAILABLE:
            self.aitoolkit_start_btn = ttk.Button(button_frame, text="Start\nAI Toolkit", 
                                                  command=self.start_aitoolkit, bootstyle="primary", width=12, padding=10)
        else:
            self.aitoolkit_start_btn = ttk.Button(button_frame, text="Start\nAI Toolkit", 
                                                  command=self.start_aitoolkit, width=12)
        self.aitoolkit_start_btn.grid(row=0, column=1, padx=10, pady=10)
        
        if THEME_AVAILABLE:
            self.aitoolkit_update_btn = ttk.Button(button_frame, text="Update\nAI Toolkit", 
                                                   command=self.update_aitoolkit, bootstyle="warning", width=12, padding=10)
        else:
            self.aitoolkit_update_btn = ttk.Button(button_frame, text="Update\nAI Toolkit", 
                                                   command=self.update_aitoolkit, width=12)
        self.aitoolkit_update_btn.grid(row=0, column=2, padx=10, pady=10)
        
        if THEME_AVAILABLE:
            self.aitoolkit_browser_btn = ttk.Button(button_frame, text="Open\nBrowser", 
                                                    command=self.open_aitoolkit_browser, bootstyle="info", width=12, padding=10)
        else:
            self.aitoolkit_browser_btn = ttk.Button(button_frame, text="Open\nBrowser", 
                                                    command=self.open_aitoolkit_browser, width=12)
        self.aitoolkit_browser_btn.grid(row=0, column=3, padx=10, pady=10)
        
        if THEME_AVAILABLE:
            self.aitoolkit_stop_btn = ttk.Button(button_frame, text="Stop\nAI Toolkit", 
                                                 command=self.stop_aitoolkit, bootstyle="danger", width=12, padding=10)
        else:
            self.aitoolkit_stop_btn = ttk.Button(button_frame, text="Stop\nAI Toolkit", 
                                                 command=self.stop_aitoolkit, width=12)
        self.aitoolkit_stop_btn.grid(row=0, column=4, padx=10, pady=10)
        
        if THEME_AVAILABLE:
            self.aitoolkit_restart_btn = ttk.Button(button_frame, text="Restart\nAI Toolkit", 
                                                    command=self.restart_aitoolkit, bootstyle="warning", width=12, padding=10)
        else:
            self.aitoolkit_restart_btn = ttk.Button(button_frame, text="Restart\nAI Toolkit", 
                                                    command=self.restart_aitoolkit, width=12)
        self.aitoolkit_restart_btn.grid(row=0, column=5, padx=10, pady=10)
        
        # Output Log
        log_frame = ttk.LabelFrame(self.aitoolkit_tab, text="AI Toolkit Output Log", padding="10")
        log_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        if THEME_AVAILABLE:
            self.aitoolkit_log_text = ScrolledText(log_frame, wrap=tk.WORD, height=20, autohide=True)
        else:
            self.aitoolkit_log_text = ScrolledText(log_frame, wrap=tk.WORD, height=20)
        self.aitoolkit_log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Clear log button
        ttk.Button(log_frame, text="Clear Log", command=lambda: self.aitoolkit_log_text.delete(1.0, tk.END)).grid(row=1, column=0, pady=(5, 0))
    
    def create_onetrainer_tab(self):
        """Create OneTrainer tab content"""
        # Action Buttons (all on one line)
        button_frame = ttk.Frame(self.onetrainer_tab)
        button_frame.grid(row=0, column=0, pady=20)
        
        # All buttons in row 0
        if THEME_AVAILABLE:
            self.onetrainer_install_btn = ttk.Button(button_frame, text="Install\nOneTrainer", 
                                                     command=self.install_onetrainer, bootstyle="success", width=12, padding=10)
        else:
            self.onetrainer_install_btn = ttk.Button(button_frame, text="Install\nOneTrainer", 
                                                     command=self.install_onetrainer, width=12)
        self.onetrainer_install_btn.grid(row=0, column=0, padx=10, pady=10)
        
        if THEME_AVAILABLE:
            self.onetrainer_start_btn = ttk.Button(button_frame, text="Start\nOneTrainer", 
                                                   command=self.start_onetrainer, bootstyle="primary", width=12, padding=10)
        else:
            self.onetrainer_start_btn = ttk.Button(button_frame, text="Start\nOneTrainer", 
                                                   command=self.start_onetrainer, width=12)
        self.onetrainer_start_btn.grid(row=0, column=1, padx=10, pady=10)
        
        if THEME_AVAILABLE:
            self.onetrainer_update_btn = ttk.Button(button_frame, text="Update\nOneTrainer", 
                                                    command=self.update_onetrainer, bootstyle="warning", width=12, padding=10)
        else:
            self.onetrainer_update_btn = ttk.Button(button_frame, text="Update\nOneTrainer", 
                                                    command=self.update_onetrainer, width=12)
        self.onetrainer_update_btn.grid(row=0, column=2, padx=10, pady=10)
        
        if THEME_AVAILABLE:
            self.onetrainer_browser_btn = ttk.Button(button_frame, text="Open\nBrowser", 
                                                     command=self.open_onetrainer_browser, bootstyle="info", width=12, padding=10)
        else:
            self.onetrainer_browser_btn = ttk.Button(button_frame, text="Open\nBrowser", 
                                                     command=self.open_onetrainer_browser, width=12)
        self.onetrainer_browser_btn.grid(row=0, column=3, padx=10, pady=10)
        
        if THEME_AVAILABLE:
            self.onetrainer_stop_btn = ttk.Button(button_frame, text="Stop\nOneTrainer", 
                                                  command=self.stop_onetrainer, bootstyle="danger", width=12, padding=10)
        else:
            self.onetrainer_stop_btn = ttk.Button(button_frame, text="Stop\nOneTrainer", 
                                                  command=self.stop_onetrainer, width=12)
        self.onetrainer_stop_btn.grid(row=0, column=4, padx=10, pady=10)
        
        if THEME_AVAILABLE:
            self.onetrainer_restart_btn = ttk.Button(button_frame, text="Restart\nOneTrainer", 
                                                     command=self.restart_onetrainer, bootstyle="warning", width=12, padding=10)
        else:
            self.onetrainer_restart_btn = ttk.Button(button_frame, text="Restart\nOneTrainer", 
                                                     command=self.restart_onetrainer, width=12)
        self.onetrainer_restart_btn.grid(row=0, column=5, padx=10, pady=10)
        
        # Output Log
        log_frame = ttk.LabelFrame(self.onetrainer_tab, text="OneTrainer Output Log", padding="10")
        log_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        if THEME_AVAILABLE:
            self.onetrainer_log_text = ScrolledText(log_frame, wrap=tk.WORD, height=20, autohide=True)
        else:
            self.onetrainer_log_text = ScrolledText(log_frame, wrap=tk.WORD, height=20)
        self.onetrainer_log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Clear log button
        ttk.Button(log_frame, text="Clear Log", command=lambda: self.onetrainer_log_text.delete(1.0, tk.END)).grid(row=1, column=0, pady=(5, 0))
    
    # Utility Methods
    def browse_directory(self, var):
        """Browse for a directory"""
        directory = filedialog.askdirectory(initialdir=var.get())
        if directory:
            var.set(directory)
    
    def browse_file(self, var, file_desc, pattern):
        """Browse for a file"""
        filename = filedialog.askopenfilename(
            initialdir=os.path.dirname(var.get()),
            title=f"Select {file_desc}",
            filetypes=[(file_desc, pattern), ("All files", "*.*")]
        )
        if filename:
            var.set(filename)
    
    def show_comfyui_settings(self):
        """Show ComfyUI settings dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title("ComfyUI Settings")
        dialog.geometry("700x500")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Main frame
        main_frame = ttk.Frame(dialog, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        dialog.columnconfigure(0, weight=1)
        dialog.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Parent Directory
        ttk.Label(main_frame, text="Parent Directory:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.comfyui_install_parent_var).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5)
        ttk.Button(main_frame, text="Browse", command=lambda: self.browse_directory(self.comfyui_install_parent_var)).grid(row=0, column=2)
        
        # User Directory
        ttk.Label(main_frame, text="User Directory:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.comfyui_user_dir_var).grid(row=1, column=1, sticky=(tk.W, tk.E), padx=5)
        ttk.Button(main_frame, text="Browse", command=lambda: self.browse_directory(self.comfyui_user_dir_var)).grid(row=1, column=2)
        
        # Output Directory
        ttk.Label(main_frame, text="Output Directory:").grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.comfyui_output_dir_var).grid(row=2, column=1, sticky=(tk.W, tk.E), padx=5)
        ttk.Button(main_frame, text="Browse", command=lambda: self.browse_directory(self.comfyui_output_dir_var)).grid(row=2, column=2)
        
        # Input Directory
        ttk.Label(main_frame, text="Input Directory:").grid(row=3, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.comfyui_input_dir_var).grid(row=3, column=1, sticky=(tk.W, tk.E), padx=5)
        ttk.Button(main_frame, text="Browse", command=lambda: self.browse_directory(self.comfyui_input_dir_var)).grid(row=3, column=2)
        
        # Extra Model Paths
        ttk.Label(main_frame, text="Extra Model Paths:").grid(row=4, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.comfyui_extra_model_paths_var).grid(row=4, column=1, sticky=(tk.W, tk.E), padx=5)
        ttk.Button(main_frame, text="Browse", command=lambda: self.browse_file(self.comfyui_extra_model_paths_var, "YAML files", "*.yaml")).grid(row=4, column=2)
        
        # Options
        ttk.Separator(main_frame, orient='horizontal').grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=15)
        
        ttk.Checkbutton(main_frame, text="Quick Install (skip optional nodes)", 
                       variable=self.comfyui_quick_install_var).grid(row=6, column=0, columnspan=3, sticky=tk.W, pady=5)
        
        # VRAM Mode
        vram_frame = ttk.Frame(main_frame)
        vram_frame.grid(row=7, column=0, columnspan=3, sticky=tk.W, pady=5)
        ttk.Label(vram_frame, text="VRAM Mode:").pack(side=tk.LEFT, padx=(0, 5))
        vram_combo = ttk.Combobox(vram_frame, textvariable=self.comfyui_vram_mode_var, width=15, state="readonly")
        vram_combo['values'] = ('--normalvram', '--highvram', '--lowvram', '--novram')
        vram_combo.pack(side=tk.LEFT)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=8, column=0, columnspan=3, pady=20)
        
        ttk.Button(button_frame, text="Save", command=lambda: [self.save_comfyui_config(), dialog.destroy()]).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def show_aitoolkit_settings(self):
        """Show AI Toolkit settings dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title("AI Toolkit Settings")
        dialog.geometry("600x200")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Main frame
        main_frame = ttk.Frame(dialog, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        dialog.columnconfigure(0, weight=1)
        dialog.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Installation Directory
        ttk.Label(main_frame, text="Installation Directory:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.aitoolkit_install_parent_var).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5)
        ttk.Button(main_frame, text="Browse", command=lambda: self.browse_directory(self.aitoolkit_install_parent_var)).grid(row=0, column=2)
        
        # Info
        ttk.Label(main_frame, text="AI Toolkit will be installed to: [selected_dir]/ai-toolkit", 
                 foreground="gray", font=('Arial', 8)).grid(row=1, column=0, columnspan=3, sticky=tk.W, pady=(0, 15))
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=3, pady=10)
        
        ttk.Button(button_frame, text="Save", command=lambda: [self.save_aitoolkit_config(), dialog.destroy()]).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def show_about(self):
        """Show about dialog"""
        theme_status = "with ttkbootstrap themes" if THEME_AVAILABLE else "(install ttkbootstrap for modern themes)"
        messagebox.showinfo("About AI Lab Manager", 
                           f"AI Lab Manager v1.0\n\n" +
                           f"A unified manager for:\n" +
                           f"  • ComfyUI\n" +
                           f"  • AI Toolkit\n" +
                           f"  • OneTrainer\n\n" +
                           f"{theme_status}\n\n" +
                           "Created by thenullengine\n" +
                           "GitHub: thenullengine/homelab")
    
    def on_theme_select(self, event=None):
        """Handle theme selection change."""
        selected_theme = self.theme_var.get()
        self.config["theme"] = selected_theme
        self.save_config()
        
        # Apply theme immediately without restart
        if THEME_AVAILABLE:
            self.style.theme_use(selected_theme)
            # Force update of all widgets
            self.root.update_idletasks()
        
        # messagebox.showinfo("Theme Changed", 
        #     f"Theme changed to '{selected_theme}' successfully!")

    def show_theme_install_help(self):
        """Show help for installing ttkbootstrap"""
        messagebox.showinfo("Install Modern Themes",
                           "To enable modern themes, install ttkbootstrap:\n\n" +
                           "pip install ttkbootstrap\n\n" +
                           "Then restart the application.")
    
    def log_to_tab(self, tab, message):
        """Add message to appropriate log"""
        if tab == "comfyui":
            log_widget = self.comfyui_log_text
        elif tab == "aitoolkit":
            log_widget = self.aitoolkit_log_text
        elif tab == "onetrainer":
            log_widget = self.onetrainer_log_text
        else:
            return
        log_widget.insert(tk.END, message + "\n")
        log_widget.see(tk.END)
        self.root.update_idletasks()
    
    def _run_command(self, cmd, cwd, tab):
        """Run a command and log output"""
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(cwd))
        if result.stdout:
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    self.log_to_tab(tab, f"  {line}")
        if result.returncode != 0 and result.stderr:
            self.log_to_tab(tab, f"ERROR: {result.stderr}")
    
    # ComfyUI Methods
    def save_comfyui_config(self):
        """Save ComfyUI configuration"""
        self.config["comfyui"]["install_parent_dir"] = self.comfyui_install_parent_var.get()
        self.config["comfyui"]["user_directory"] = self.comfyui_user_dir_var.get()
        self.config["comfyui"]["output_directory"] = self.comfyui_output_dir_var.get()
        self.config["comfyui"]["input_directory"] = self.comfyui_input_dir_var.get()
        self.config["comfyui"]["extra_model_paths"] = self.comfyui_extra_model_paths_var.get()
        self.config["comfyui"]["quick_install"] = self.comfyui_quick_install_var.get()
        self.config["comfyui"]["vram_mode"] = self.comfyui_vram_mode_var.get()
        
        self.save_config()
        messagebox.showinfo("Success", "ComfyUI configuration saved successfully!")
    
    def install_comfyui(self):
        """Install ComfyUI in a separate thread"""
        if self.comfyui_installing:
            messagebox.showwarning("Installation", "ComfyUI installation already in progress!")
            return
        
        self.save_comfyui_config()
        
        parent_dir = Path(self.comfyui_install_parent_var.get())
        install_path = parent_dir / "ComfyUI"
        
        if install_path.exists() and (install_path / "venv").exists() and (install_path / "main.py").exists():
            if not messagebox.askyesno("ComfyUI Already Installed", 
                f"ComfyUI appears to be already installed at:\n{install_path}\n\nDo you want to delete it and reinstall?"):
                return
            try:
                import shutil
                shutil.rmtree(install_path)
                self.log_to_tab("comfyui", f"Removed existing ComfyUI installation: {install_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to remove directory: {e}")
                return
        
        self.comfyui_install_btn.state(['disabled'])
        self.comfyui_installing = True
        
        thread = threading.Thread(target=self._run_comfyui_installation, daemon=True)
        thread.start()
    
    def _run_comfyui_installation(self):
        """Run the ComfyUI installation process"""
        try:
            self.log_to_tab("comfyui", "=" * 60)
            self.log_to_tab("comfyui", "Starting ComfyUI Installation")
            self.log_to_tab("comfyui", "=" * 60)
            
            parent_dir = Path(self.comfyui_install_parent_var.get())
            install_path = parent_dir / "ComfyUI"
            
            self.log_to_tab("comfyui", f"Parent directory: {parent_dir}")
            self.log_to_tab("comfyui", f"ComfyUI will be installed to: {install_path}")
            
            if not parent_dir.exists():
                self.log_to_tab("comfyui", f"Creating directory: {parent_dir}")
                parent_dir.mkdir(parents=True, exist_ok=True)
            
            # Clone ComfyUI
            self.log_to_tab("comfyui", "\nCloning ComfyUI repository...")
            result = subprocess.run(
                ["git", "clone", "--depth", "1", "https://github.com/Comfy-Org/ComfyUI.git"],
                capture_output=True, text=True, cwd=str(parent_dir)
            )
            if result.returncode != 0:
                self.log_to_tab("comfyui", f"ERROR: {result.stderr}")
                messagebox.showerror("Installation Error", f"Failed to clone ComfyUI:\n{result.stderr}")
                return
            self.log_to_tab("comfyui", "ComfyUI cloned successfully!")
            
            # Create venv
            self.log_to_tab("comfyui", "\nCreating Python virtual environment...")
            result = subprocess.run(
                ["py", "-3.12", "-m", "venv", "venv"],
                capture_output=True, text=True, cwd=str(install_path)
            )
            if result.returncode != 0:
                self.log_to_tab("comfyui", f"ERROR: {result.stderr}")
                messagebox.showerror("Installation Error", f"Failed to create venv:\n{result.stderr}")
                return
            self.log_to_tab("comfyui", "Virtual environment created!")
            
            venv_python = str(install_path / "venv" / "Scripts" / "python.exe")
            venv_pip = str(install_path / "venv" / "Scripts" / "pip.exe")
            
            # Upgrade pip
            self.log_to_tab("comfyui", "\nUpgrading pip...")
            self._run_command([venv_python, "-m", "pip", "install", "--upgrade", "pip"], install_path, "comfyui")
            
            # Install PyTorch
            self.log_to_tab("comfyui", "\nInstalling PyTorch for CUDA 12.4...")
            self._run_command([
                venv_pip, "install", "torch", "torchvision", "torchaudio",
                "--index-url", "https://download.pytorch.org/whl/cu124"
            ], install_path, "comfyui")
            
            # Verify PyTorch
            self.log_to_tab("comfyui", "\nVerifying PyTorch installation...")
            result = subprocess.run(
                [venv_python, "-c", "import torch; print(f'PyTorch {torch.__version__} installed')"],
                capture_output=True, text=True, cwd=str(install_path)
            )
            self.log_to_tab("comfyui", result.stdout.strip() if result.stdout else "PyTorch verified")
            
            # Install SageAttention
            self.log_to_tab("comfyui", "\nInstalling SageAttention...")
            self._run_command([venv_pip, "install", "ninja", "packaging", "wheel"], install_path, "comfyui")
            self._run_command([venv_pip, "install", "--no-build-isolation", "sageattention"], install_path, "comfyui")
            
            # Install ComfyUI requirements
            self.log_to_tab("comfyui", "\nInstalling ComfyUI requirements...")
            self._run_command([venv_pip, "install", "-r", "requirements.txt"], install_path, "comfyui")
            
            # Install common dependencies
            self.log_to_tab("comfyui", "\nInstalling common dependencies...")
            self._run_command([venv_pip, "install", "soundfile"], install_path, "comfyui")
            
            # Clone custom nodes
            self._clone_custom_nodes(install_path)
            
            # Install custom node dependencies
            self._install_custom_node_dependencies(install_path, venv_python, venv_pip)
            
            self.log_to_tab("comfyui", "\n" + "=" * 60)
            self.log_to_tab("comfyui", "Installation Complete!")
            self.log_to_tab("comfyui", "=" * 60)
            messagebox.showinfo("Success", "ComfyUI installed successfully!")
            
        except Exception as e:
            self.log_to_tab("comfyui", f"\nERROR: {str(e)}")
            messagebox.showerror("Installation Error", f"Installation failed:\n{str(e)}")
        finally:
            self.comfyui_installing = False
            self.comfyui_install_btn.state(['!disabled'])
    
    def _clone_custom_nodes(self, install_path):
        """Clone custom nodes for ComfyUI"""
        node_dir = install_path / "custom_nodes"
        
        self.log_to_tab("comfyui", "\nCloning custom nodes...")
        
        must_have_nodes = [
            "https://github.com/ltdrdata/ComfyUI-Manager.git",
            "https://github.com/rgthree/rgthree-comfy.git",
            "https://github.com/ltdrdata/ComfyUI-Impact-Pack.git",
            "https://github.com/kijai/ComfyUI-KJNodes.git",
            "https://github.com/PozzettiAndrea/ComfyUI-SAM3.git",
            "https://github.com/lquesada/ComfyUI-Inpaint-CropAndStitch.git",
            "https://github.com/cubiq/ComfyUI_essentials.git",
            "https://github.com/Fannovel16/comfyui_controlnet_aux.git",
            "https://github.com/pythongosssss/ComfyUI-Custom-Scripts.git",
            "https://github.com/ssitu/ComfyUI_UltimateSDUpscale.git",
            "https://github.com/chflame163/ComfyUI_LayerStyle.git",
            "https://github.com/Acly/comfyui-inpaint-nodes.git",
            "https://github.com/Acly/comfyui-tooling-nodes.git",
        ]
        
        for repo in must_have_nodes:
            node_name = repo.split("/")[-1].replace(".git", "")
            self.log_to_tab("comfyui", f"  Cloning {node_name}...")
            result = subprocess.run(
                ["git", "clone", "--depth", "1", repo],
                capture_output=True, text=True, cwd=str(node_dir)
            )
            if result.returncode != 0:
                self.log_to_tab("comfyui", f"    WARNING: Failed to clone {node_name}")
        
        if not self.comfyui_quick_install_var.get():
            self.log_to_tab("comfyui", "\nCloning additional nodes...")
            additional_nodes = [
                "https://github.com/city96/ComfyUI-GGUF.git",
                "https://github.com/yolain/ComfyUI-Easy-Use.git",
                "https://github.com/crystian/ComfyUI-Crystools.git",
                "https://github.com/1038lab/ComfyUI-RMBG.git",
                "https://github.com/ltdrdata/ComfyUI-Impact-Subpack.git",
                "https://github.com/ty0x2333/ComfyUI-Dev-Utils.git",
                "https://github.com/ltdrdata/ComfyUI-Inspire-Pack.git",
                "https://github.com/gseth/ControlAltAI-Nodes.git",
                "https://github.com/jamesWalker55/comfyui-various.git",
                "https://github.com/pollockjj/ComfyUI-MultiGPU.git",
                "https://github.com/ltdrdata/was-node-suite-comfyui.git",
                "https://github.com/kijai/ComfyUI-segment-anything-2.git",
                "https://github.com/PozzettiAndrea/ComfyUI-SAM3DBody.git",
                "https://github.com/chrisgoringe/cg-image-filter.git",
                "https://github.com/Jonseed/ComfyUI-Detail-Daemon.git",
                "https://github.com/tritant/ComfyUI_CreaPrompt.git",
                "https://github.com/mr-pepe69/ComfyUI-SelectStringFromListWithIndex.git",
                "https://github.com/un-seen/comfyui-tensorops.git",
                "https://github.com/giriss/comfy-image-saver.git",
                "https://github.com/cubiq/ComfyUI_InstantID.git",
                "https://github.com/cubiq/ComfyUI_IPAdapter_plus.git",
                "https://github.com/PowerHouseMan/ComfyUI-AdvancedLivePortrait.git",
                "https://github.com/kijai/ComfyUI-LivePortraitKJ.git",
                "https://github.com/Gourieff/ComfyUI-ReActor.git",
                "https://github.com/pythongosssss/ComfyUI-WD14-Tagger.git",
                "https://github.com/stavsap/comfyui-ollama.git",
                "https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite.git",
                "https://github.com/Lightricks/ComfyUI-LTXVideo.git",
                "https://github.com/kijai/ComfyUI-HunyuanVideoWrapper.git",
                "https://github.com/kijai/ComfyUI-CogVideoXWrapper.git",
                "https://github.com/Fannovel16/ComfyUI-Frame-Interpolation.git",
                "https://github.com/kijai/ComfyUI-WanVideoWrapper.git",
            ]
            
            for repo in additional_nodes:
                node_name = repo.split("/")[-1].replace(".git", "")
                self.log_to_tab("comfyui", f"  Cloning {node_name}...")
                result = subprocess.run(
                    ["git", "clone", "--depth", "1", repo],
                    capture_output=True, text=True, cwd=str(node_dir)
                )
                if result.returncode != 0:
                    self.log_to_tab("comfyui", f"    WARNING: Failed to clone {node_name}")
    
    def _install_custom_node_dependencies(self, install_path, venv_python, venv_pip):
        """Install dependencies for custom nodes"""
        node_dir = install_path / "custom_nodes"
        
        self.log_to_tab("comfyui", "\nInstalling custom node dependencies...")
        
        for node_folder in node_dir.iterdir():
            if not node_folder.is_dir() or node_folder.name.startswith('.'):
                continue
            
            self.log_to_tab("comfyui", f"\nChecking {node_folder.name}...")
            
            install_bat = node_folder / "install.bat"
            install_py = node_folder / "install.py"
            requirements_txt = node_folder / "requirements.txt"
            
            try:
                if install_bat.exists():
                    self.log_to_tab("comfyui", f"  Running install.bat for {node_folder.name}...")
                    result = subprocess.run(
                        ["cmd", "/c", str(install_bat)],
                        cwd=str(node_folder), 
                        capture_output=True,
                        stdin=subprocess.DEVNULL,
                        timeout=300,
                        text=True
                    )
                    if result.returncode != 0 and result.stderr:
                        self.log_to_tab("comfyui", f"    WARNING: {result.stderr[:200]}")
                    else:
                        self.log_to_tab("comfyui", f"    Completed successfully")
                        
                elif install_py.exists():
                    self.log_to_tab("comfyui", f"  Running install.py for {node_folder.name}...")
                    result = subprocess.run(
                        [venv_python, str(install_py)],
                        cwd=str(node_folder), 
                        capture_output=True,
                        timeout=300,
                        text=True
                    )
                    if result.returncode != 0 and result.stderr:
                        self.log_to_tab("comfyui", f"    WARNING: {result.stderr[:200]}")
                    else:
                        self.log_to_tab("comfyui", f"    Completed successfully")
                        
                elif requirements_txt.exists():
                    self.log_to_tab("comfyui", f"  Installing requirements for {node_folder.name}...")
                    result = subprocess.run(
                        [venv_pip, "install", "-r", str(requirements_txt)],
                        cwd=str(node_folder), 
                        capture_output=True,
                        timeout=300,
                        text=True
                    )
                    if result.returncode != 0 and result.stderr:
                        self.log_to_tab("comfyui", f"    WARNING: {result.stderr[:200]}")
                    else:
                        self.log_to_tab("comfyui", f"    Completed successfully")
                else:
                    self.log_to_tab("comfyui", f"  No install script found for {node_folder.name}, skipping.")
                    
            except subprocess.TimeoutExpired:
                self.log_to_tab("comfyui", f"    WARNING: Installation timed out after 5 minutes")
            except Exception as e:
                self.log_to_tab("comfyui", f"    WARNING: Installation failed - {str(e)[:100]}")
    
    def start_comfyui(self):
        """Start ComfyUI"""
        if self.comfyui_starting:
            messagebox.showwarning("Starting", "ComfyUI is already starting!")
            return
        
        # self.save_comfyui_config()
        
        parent_dir = Path(self.comfyui_install_parent_var.get())
        install_path = parent_dir / "ComfyUI"
        if not install_path.exists():
            messagebox.showerror("Error", f"ComfyUI not found at {install_path}\nPlease install first.")
            return
        
        self.comfyui_start_btn.state(['disabled'])
        self.comfyui_starting = True
        
        thread = threading.Thread(target=self._run_comfyui, daemon=True)
        thread.start()
    
    def _run_comfyui(self):
        """Run ComfyUI process"""
        try:
            self.log_to_tab("comfyui", "=" * 60)
            self.log_to_tab("comfyui", "Starting ComfyUI")
            self.log_to_tab("comfyui", "=" * 60)
            
            parent_dir = Path(self.comfyui_install_parent_var.get())
            install_path = parent_dir / "ComfyUI"
            venv_python = install_path / "venv" / "Scripts" / "python.exe"
            
            # Copy extra_model_paths.yaml if it exists
            extra_paths = Path(self.comfyui_extra_model_paths_var.get())
            if extra_paths.exists():
                import shutil
                dest = install_path / "extra_model_paths.yaml"
                shutil.copy(extra_paths, dest)
                self.log_to_tab("comfyui", f"Copied {extra_paths.name} to ComfyUI directory")
            
            # Build command
            cmd = [
                str(venv_python),
                "main.py",
                "--user-directory", self.comfyui_user_dir_var.get(),
                "--output-directory", self.comfyui_output_dir_var.get(),
                "--input-directory", self.comfyui_input_dir_var.get(),
                self.comfyui_vram_mode_var.get()
            ]
            
            self.log_to_tab("comfyui", f"\nRunning: {' '.join(cmd)}")
            self.log_to_tab("comfyui", "The UI will be available at: http://127.0.0.1:8188\n")
            
            # Start process with output capture
            self.comfyui_process = subprocess.Popen(
                cmd,
                cwd=str(install_path),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Stream output to log
            import time
            time.sleep(2)
            self.root.after(100, lambda: self.open_comfyui_browser())
            
            for line in iter(self.comfyui_process.stdout.readline, ''):
                if self.comfyui_process.poll() is not None:
                    break
                self.log_to_tab("comfyui", line.rstrip())
            
            self.comfyui_process.stdout.close()
            return_code = self.comfyui_process.wait()
            
            if return_code != 0:
                self.log_to_tab("comfyui", f"\n[ComfyUI exited with code {return_code}]")
            else:
                self.log_to_tab("comfyui", "\n[ComfyUI stopped]")
            
        except Exception as e:
            self.log_to_tab("comfyui", f"\nERROR: {str(e)}")
            messagebox.showerror("Start Error", f"Failed to start ComfyUI:\n{str(e)}")
        finally:
            self.comfyui_process = None
            self.comfyui_starting = False
            self.comfyui_start_btn.state(['!disabled'])
    
    def open_comfyui_browser(self):
        """Open ComfyUI in browser"""
        import webbrowser
        webbrowser.open("http://127.0.0.1:8188")
        self.log_to_tab("comfyui", "Opened browser to http://127.0.0.1:8188")
    
    def stop_comfyui(self):
        """Stop ComfyUI process"""
        if self.comfyui_process is None or self.comfyui_process.poll() is not None:
            messagebox.showinfo("Stop", "ComfyUI is not currently running.")
            return
        
        if messagebox.askyesno("Stop ComfyUI", "Are you sure you want to stop ComfyUI?"):
            self.log_to_tab("comfyui", "\n[Stopping ComfyUI...]")
            try:
                import psutil
                import time
                
                # Get parent process and all children
                try:
                    parent = psutil.Process(self.comfyui_process.pid)
                    children = parent.children(recursive=True)
                    
                    # Terminate all children first
                    for child in children:
                        try:
                            self.log_to_tab("comfyui", f"[Stopping child process: {child.pid}]")
                            child.terminate()
                        except psutil.NoSuchProcess:
                            pass
                    
                    # Terminate parent
                    parent.terminate()
                    
                    # Wait for processes to terminate
                    gone, alive = psutil.wait_procs(children + [parent], timeout=3)
                    
                    # Force kill any remaining processes
                    for p in alive:
                        try:
                            self.log_to_tab("comfyui", f"[Force killing process: {p.pid}]")
                            p.kill()
                        except psutil.NoSuchProcess:
                            pass
                    
                except psutil.NoSuchProcess:
                    # Process already died
                    pass
                
                self.log_to_tab("comfyui", "[ComfyUI stopped successfully]")
            except ImportError:
                # Fallback if psutil not available
                self.comfyui_process.terminate()
                time.sleep(2)
                if self.comfyui_process.poll() is None:
                    self.comfyui_process.kill()
                self.log_to_tab("comfyui", "[ComfyUI stopped]")
            except Exception as e:
                self.log_to_tab("comfyui", f"[Error stopping ComfyUI: {str(e)}]")
                messagebox.showerror("Stop Error", f"Failed to stop ComfyUI:\n{str(e)}")
    
    def restart_comfyui(self):
        """Restart ComfyUI process"""
        self.log_to_tab("comfyui", "\n[Restarting ComfyUI...]")
        
        # Stop if running
        if self.comfyui_process and self.comfyui_process.poll() is None:
            try:
                import psutil
                import time
                
                parent = psutil.Process(self.comfyui_process.pid)
                children = parent.children(recursive=True)
                
                for child in children:
                    try:
                        child.terminate()
                    except psutil.NoSuchProcess:
                        pass
                
                parent.terminate()
                gone, alive = psutil.wait_procs(children + [parent], timeout=3)
                
                for p in alive:
                    try:
                        p.kill()
                    except psutil.NoSuchProcess:
                        pass
                
                time.sleep(1)
            except Exception as e:
                self.log_to_tab("comfyui", f"[Error during stop: {str(e)}]")
        
        # Start again
        self.start_comfyui()
    
    # AI Toolkit Methods
    def save_aitoolkit_config(self):
        """Save AI Toolkit configuration"""
        self.config["aitoolkit"]["install_parent_dir"] = self.aitoolkit_install_parent_var.get()
        
        self.save_config()
        messagebox.showinfo("Success", "AI Toolkit configuration saved successfully!")
    
    def install_aitoolkit(self):
        """Install AI Toolkit in a separate thread"""
        if self.aitoolkit_installing:
            messagebox.showwarning("Installation", "AI Toolkit installation already in progress!")
            return
        
        self.save_aitoolkit_config()
        
        parent_dir = Path(self.aitoolkit_install_parent_var.get())
        ai_toolkit_dir = parent_dir / "ai-toolkit"
        
        if ai_toolkit_dir.exists():
            messagebox.showwarning("Already Exists", 
                f"AI-Toolkit folder already exists at:\n{ai_toolkit_dir}\n\n" +
                "Please choose a different location or remove the existing folder.")
            return
        
        self.aitoolkit_install_btn.state(['disabled'])
        self.aitoolkit_installing = True
        
        thread = threading.Thread(target=self._run_aitoolkit_installation, daemon=True)
        thread.start()
    
    def _run_aitoolkit_installation(self):
        """Run the AI Toolkit installation process"""
        try:
            self.log_to_tab("aitoolkit", "=" * 60)
            self.log_to_tab("aitoolkit", "Starting AI Toolkit Installation")
            self.log_to_tab("aitoolkit", "=" * 60)
            
            parent_dir = Path(self.aitoolkit_install_parent_var.get())
            self.log_to_tab("aitoolkit", f"Installation directory: {parent_dir}")
            
            if not parent_dir.exists():
                self.log_to_tab("aitoolkit", f"Creating directory: {parent_dir}")
                parent_dir.mkdir(parents=True, exist_ok=True)
            
            # Check for git
            self.log_to_tab("aitoolkit", "\nChecking for git...")
            result = subprocess.run(["git", "--version"], capture_output=True, text=True)
            if result.returncode != 0:
                self.log_to_tab("aitoolkit", "ERROR: Git is not installed!")
                messagebox.showerror("Error", "Git is not installed.\nPlease install git from https://git-scm.com/")
                return
            self.log_to_tab("aitoolkit", f"Git found: {result.stdout.strip()}")
            
            # Check for Node.js
            self.log_to_tab("aitoolkit", "\nChecking for Node.js...")
            result = subprocess.run(["node", "--version"], capture_output=True, text=True)
            if result.returncode != 0:
                self.log_to_tab("aitoolkit", "WARNING: Node.js not found. Installing/updating Node.js...")
                self._run_command(["winget", "install", "--id=OpenJS.NodeJS", "-e"], parent_dir, "aitoolkit")
            else:
                self.log_to_tab("aitoolkit", f"Node.js found: {result.stdout.strip()}")
            
            # Install Python embedded
            self.log_to_tab("aitoolkit", "\n" + "=" * 60)
            self.log_to_tab("aitoolkit", "Installing Python Embedded")
            self.log_to_tab("aitoolkit", "=" * 60)
            self._install_python_embedded(parent_dir)
            
            # Clone AI-Toolkit
            self.log_to_tab("aitoolkit", "\n" + "=" * 60)
            self.log_to_tab("aitoolkit", "Cloning AI-Toolkit Repository")
            self.log_to_tab("aitoolkit", "=" * 60)
            self._run_command(["git", "clone", "https://github.com/ostris/ai-toolkit.git"], parent_dir, "aitoolkit")
            
            ai_toolkit_dir = parent_dir / "ai-toolkit"
            python_dir = parent_dir / "python_embeded"
            python_exe = python_dir / "python.exe"
            
            # Install AI Toolkit dependencies
            self.log_to_tab("aitoolkit", "\n" + "=" * 60)
            self.log_to_tab("aitoolkit", "Installing AI Toolkit Dependencies")
            self.log_to_tab("aitoolkit", "=" * 60)
            
            # Check if uv is available
            uv_exe = python_dir / "Scripts" / "uv.exe"
            if uv_exe.exists():
                self.log_to_tab("aitoolkit", "Using UV for faster package installation...")
                
                # Install PyTorch
                self.log_to_tab("aitoolkit", "\nInstalling PyTorch 2.8.0 with CUDA 12.8...")
                self._run_command([
                    str(python_exe), "-I", "-m", "uv", "pip", "install",
                    "torch==2.8.0", "torchvision==0.23.0", "torchaudio==2.8.0",
                    "--index-url", "https://download.pytorch.org/whl/cu128",
                    "--no-cache", "--link-mode=copy"
                ], ai_toolkit_dir, "aitoolkit")
                
                # Install requirements
                self.log_to_tab("aitoolkit", "\nInstalling requirements...")
                self._run_command([
                    str(python_exe), "-I", "-m", "uv", "pip", "install",
                    "-r", "requirements.txt",
                    "--no-cache", "--link-mode=copy"
                ], ai_toolkit_dir, "aitoolkit")
                
                # Install additional packages
                self.log_to_tab("aitoolkit", "\nInstalling additional packages...")
                for pkg in ["poetry-core", "wheel", "triton-windows==3.4.0.post20", "hf_xet"]:
                    self._run_command([
                        str(python_exe), "-I", "-m", "uv", "pip", "install",
                        pkg, "--no-cache", "--link-mode=copy"
                    ], ai_toolkit_dir, "aitoolkit")
            else:
                self.log_to_tab("aitoolkit", "Using pip for package installation...")
                
                # Install PyTorch
                self.log_to_tab("aitoolkit", "\nInstalling PyTorch 2.8.0 with CUDA 12.8...")
                self._run_command([
                    str(python_exe), "-I", "-m", "pip", "install",
                    "torch==2.8.0", "torchvision==0.23.0", "torchaudio==2.8.0",
                    "--index-url", "https://download.pytorch.org/whl/cu128",
                    "--no-cache-dir", "--no-warn-script-location"
                ], ai_toolkit_dir, "aitoolkit")
                
                # Install requirements
                self.log_to_tab("aitoolkit", "\nInstalling requirements...")
                self._run_command([
                    str(python_exe), "-I", "-m", "pip", "install",
                    "-r", "requirements.txt",
                    "--no-cache-dir", "--no-warn-script-location"
                ], ai_toolkit_dir, "aitoolkit")
                
                # Install additional packages
                self.log_to_tab("aitoolkit", "\nInstalling additional packages...")
                for pkg in ["poetry-core", "wheel", "triton-windows==3.4.0.post20", "hf_xet"]:
                    self._run_command([
                        str(python_exe), "-I", "-m", "pip", "install",
                        pkg, "--no-cache-dir", "--no-warn-script-location"
                    ], ai_toolkit_dir, "aitoolkit")
            
            # Create startup batch files
            self.log_to_tab("aitoolkit", "\n" + "=" * 60)
            self.log_to_tab("aitoolkit", "Creating Startup Scripts")
            self.log_to_tab("aitoolkit", "=" * 60)
            self._create_startup_scripts(parent_dir)
            
            self.log_to_tab("aitoolkit", "\n" + "=" * 60)
            self.log_to_tab("aitoolkit", "Installation Complete!")
            self.log_to_tab("aitoolkit", "=" * 60)
            self.log_to_tab("aitoolkit", "\nYou can now start AI Toolkit using the 'Start AI Toolkit' button")
            self.log_to_tab("aitoolkit", "or by running Start-AI-Toolkit.bat in the installation directory.")
            
            messagebox.showinfo("Success", "AI Toolkit installed successfully!")
            
        except Exception as e:
            self.log_to_tab("aitoolkit", f"\nERROR: {str(e)}")
            import traceback
            self.log_to_tab("aitoolkit", traceback.format_exc())
            messagebox.showerror("Installation Error", f"Installation failed:\n{str(e)}")
        finally:
            self.aitoolkit_installing = False
            self.aitoolkit_install_btn.state(['!disabled'])
    
    def _install_python_embedded(self, parent_dir):
        """Install Python embedded for AI Toolkit"""
        self.log_to_tab("aitoolkit", "\nDownloading Python 3.12.10 embedded...")
        
        python_zip = "python-3.12.10-embed-amd64.zip"
        python_url = f"https://www.python.org/ftp/python/3.12.10/{python_zip}"
        
        # Download Python
        result = subprocess.run(
            ["powershell", "-Command",
             f"try {{ Invoke-WebRequest -Uri '{python_url}' -OutFile '{python_zip}' -UseBasicParsing }} catch {{ exit 1 }}"],
            cwd=str(parent_dir),
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            self.log_to_tab("aitoolkit", "PowerShell download failed, trying curl...")
            subprocess.run(
                ["curl", "-L", "-o", python_zip, python_url, "--ssl-no-revoke"],
                cwd=str(parent_dir),
                check=True
            )
        
        self.log_to_tab("aitoolkit", "Extracting Python...")
        python_dir = parent_dir / "python_embeded"
        python_dir.mkdir(exist_ok=True)
        
        subprocess.run(
            ["tar", "-xf", str(parent_dir / python_zip), "-C", str(python_dir)],
            cwd=str(parent_dir),
            check=True
        )
        
        (parent_dir / python_zip).unlink()
        
        # Download and install pip
        self.log_to_tab("aitoolkit", "\nInstalling pip...")
        get_pip_url = "https://bootstrap.pypa.io/get-pip.py"
        
        result = subprocess.run(
            ["powershell", "-Command",
             f"try {{ Invoke-WebRequest -Uri '{get_pip_url}' -OutFile 'get-pip.py' -UseBasicParsing }} catch {{ exit 1 }}"],
            cwd=str(python_dir),
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            self.log_to_tab("aitoolkit", "PowerShell download failed, trying curl...")
            subprocess.run(
                ["curl", "-L", "-o", "get-pip.py", get_pip_url, "--ssl-no-revoke"],
                cwd=str(python_dir),
                check=True
            )
        
        # Configure Python path
        self.log_to_tab("aitoolkit", "Configuring Python paths...")
        pth_file = python_dir / "python312._pth"
        with open(pth_file, 'w') as f:
            f.write("../ai-toolkit\n")
            f.write("Lib/site-packages\n")
            f.write("Lib\n")
            f.write("Scripts\n")
            f.write("python312.zip\n")
            f.write(".\n")
            f.write("# import site\n")
        
        python_exe = python_dir / "python.exe"
        
        # Install pip
        self.log_to_tab("aitoolkit", "Running pip installer...")
        subprocess.run(
            [str(python_exe), "-I", "get-pip.py", "--no-cache-dir", "--no-warn-script-location"],
            cwd=str(python_dir),
            check=True
        )
        
        # Install uv and upgrade pip
        self.log_to_tab("aitoolkit", "Installing uv and upgrading pip...")
        subprocess.run(
            [str(python_exe), "-I", "-m", "pip", "install", "uv==0.9.7", "--no-cache-dir", "--no-warn-script-location"],
            cwd=str(python_dir),
            check=True
        )
        
        subprocess.run(
            [str(python_exe), "-I", "-m", "pip", "install", "--upgrade", "pip", "--no-cache-dir", "--no-warn-script-location"],
            cwd=str(python_dir),
            check=True
        )
        
        # Download and extract Python libs for Triton
        self.log_to_tab("aitoolkit", "\nDownloading Python libs for Triton support...")
        libs_zip = "python_3.12.7_include_libs.zip"
        libs_url = f"https://github.com/woct0rdho/triton-windows/releases/download/v3.0.0-windows.post1/{libs_zip}"
        
        result = subprocess.run(
            ["powershell", "-Command",
             f"try {{ Invoke-WebRequest -Uri '{libs_url}' -OutFile '{libs_zip}' -UseBasicParsing }} catch {{ exit 1 }}"],
            cwd=str(python_dir),
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            self.log_to_tab("aitoolkit", "PowerShell download failed, trying curl...")
            subprocess.run(
                ["curl", "-L", "-o", libs_zip, libs_url, "--ssl-no-revoke"],
                cwd=str(python_dir),
                check=True
            )
        
        subprocess.run(
            ["tar", "-xf", libs_zip],
            cwd=str(python_dir),
            check=True
        )
        
        (python_dir / libs_zip).unlink()
        
        self.log_to_tab("aitoolkit", "Python embedded installation complete!")
    
    def _create_startup_scripts(self, parent_dir):
        """Create startup batch files for AI Toolkit"""
        # Create Start-AI-Toolkit.bat
        start_bat = parent_dir / "Start-AI-Toolkit.bat"
        self.log_to_tab("aitoolkit", f"Creating {start_bat.name}...")
        
        with open(start_bat, 'w') as f:
            f.write('@echo off&&cd /d %~dp0\n')
            f.write('Title AI-Toolkit\n')
            f.write('setlocal enabledelayedexpansion\n\n')
            
            # Clear Python environment variables
            f.write('set PYTHONPATH=\n')
            f.write('set PYTHONHOME=\n')
            f.write('set PYTHON=\n')
            f.write('set PYTHONSTARTUP=\n')
            f.write('set PYTHONUSERBASE=\n')
            f.write('set PIP_CONFIG_FILE=\n')
            f.write('set PIP_REQUIRE_VIRTUALENV=\n')
            f.write('set VIRTUAL_ENV=\n')
            f.write('set CONDA_PREFIX=\n')
            f.write('set CONDA_DEFAULT_ENV=\n')
            f.write('set PYENV_ROOT=\n')
            f.write('set PYENV_VERSION=\n\n')
            
            # Set colors
            f.write('set warning=[33m\n')
            f.write('set     red=[91m\n')
            f.write('set   green=[92m\n')
            f.write('set  yellow=[93m\n')
            f.write('set    bold=[97m\n')
            f.write('set   reset=[0m\n\n')
            
            # Set path
            f.write('set "path=%~dp0\\python_embeded;%~dp0\\python_embeded\\Scripts;%path%"\n')
            
            # Check folders exist
            f.write('if not exist .\\ai-toolkit\\ (\n')
            f.write('    echo %warning%WARNING:%reset% \'%bold%ai-toolkit%reset%\' folder NOT exists!\n')
            f.write('    echo %green%Please reinstall AI-Toolkit.%reset%\n')
            f.write('    echo Press any key to Exit...&Pause>nul\n')
            f.write('    goto :eof\n')
            f.write(')\n')
            f.write('if not exist .\\python_embeded\\ (\n')
            f.write('    echo %warning%WARNING:%reset% \'%bold%python_embeded%reset%\' folder NOT exists!\n')
            f.write('    echo %green%Please reinstall AI-Toolkit.%reset%\n')
            f.write('    echo Press any key to Exit...&Pause>nul\n')
            f.write('    goto :eof\n')
            f.write(')\n\n')
            
            f.write('set GIT_LFS_SKIP_SMUDGE=1\n')
            f.write('set "local_serv=http://localhost:8675"\n')
            f.write('echo.\n')
            f.write('cd ./ai-toolkit\n')
            f.write('echo %green%:::::::::::::  Starting AI-Toolkit ...  ::::::::::::::::%reset%\n')
            f.write('echo.\n')
            
            # Check for updates
            f.write('git.exe fetch\n')
            f.write('git.exe status -uno | findstr /C:"Your branch is behind" >nul\n')
            f.write('if !errorlevel!==0 (\n')
            f.write('    echo  - %red%New updates%reset% are available.%green% Run Update-AI-Toolkit.bat%reset%\n')
            f.write('    echo.\n')
            f.write(')\n\n')
            
            # Check for HF token
            f.write('if exist ".\\aitk_db.db" (\n')
            f.write('    type ".\\aitk_db.db" 2>nul | findstr /i /c:"HF_TOKEN" >nul 2>&1\n')
            f.write('    if errorlevel 1 (echo  - %green%Hugging Face Token%reset% not found. Set it in Settings.)\n')
            f.write(')\n')
            f.write('echo  - Stop the server with %green%Ctrl+C twice%reset%, not %red%X%reset%\n')
            f.write('echo.\n')
            f.write('echo %yellow%::::::::: Waiting for the server to start... ::::::::::%reset%\n\n')
            
            # Start the UI
            f.write('cd ./ui\n')
            f.write('start cmd.exe /k npm run build_and_start\n')
            
            # Wait for server and open browser
            f.write(':loop\n')
            f.write('if exist "%windir%\\System32\\WindowsPowerShell\\v1.0" set "path=%path%;%windir%\\System32\\WindowsPowerShell\\v1.0"\n')
            f.write('powershell -Command "try { $response = Invoke-WebRequest -Uri \'!local_serv!\' -TimeoutSec 2 -UseBasicParsing; exit 0 } catch { exit 1 }" >nul 2>&1\n')
            f.write('if !errorlevel! neq 0 (timeout /t 2 /nobreak >nul&&goto :loop)\n')
            f.write('start !local_serv!\n')
        
        self.log_to_tab("aitoolkit", f"Created {start_bat.name}")
        
        # Create Update-AI-Toolkit.bat
        update_bat = parent_dir / "Update-AI-Toolkit.bat"
        self.log_to_tab("aitoolkit", f"Creating {update_bat.name}...")
        
        with open(update_bat, 'w') as f:
            f.write('@echo off&&cd /d %~dp0\n')
            f.write('Title AI-Toolkit Update\n\n')
            
            # Clear Python environment variables
            f.write('set PYTHONPATH=\n')
            f.write('set PYTHONHOME=\n')
            f.write('set PYTHON=\n')
            f.write('set PYTHONSTARTUP=\n')
            f.write('set PYTHONUSERBASE=\n')
            f.write('set PIP_CONFIG_FILE=\n')
            f.write('set PIP_REQUIRE_VIRTUALENV=\n')
            f.write('set VIRTUAL_ENV=\n')
            f.write('set CONDA_PREFIX=\n')
            f.write('set CONDA_DEFAULT_ENV=\n')
            f.write('set PYENV_ROOT=\n')
            f.write('set PYENV_VERSION=\n\n')
            
            # Set colors
            f.write('set warning=[33m\n')
            f.write('set     red=[91m\n')
            f.write('set   green=[92m\n')
            f.write('set  yellow=[93m\n')
            f.write('set    bold=[97m\n')
            f.write('set   reset=[0m\n\n')
            
            # Set path
            f.write('set "path=%~dp0\\python_embeded;%~dp0\\python_embeded\\Scripts;%path%"\n')
            
            # Check folders exist
            f.write('if not exist .\\ai-toolkit\\ (\n')
            f.write('    echo %warning%WARNING:%reset% \'%bold%ai-toolkit%reset%\' folder NOT exists!\n')
            f.write('    echo %green%Please reinstall AI-Toolkit.%reset%\n')
            f.write('    echo Press any key to Exit...&Pause>nul\n')
            f.write('    goto :eof\n')
            f.write(')\n')
            f.write('if not exist .\\python_embeded\\ (\n')
            f.write('    echo %warning%WARNING:%reset% \'%bold%python_embeded%reset%\' folder NOT exists!\n')
            f.write('    echo %green%Please reinstall AI-Toolkit.%reset%\n')
            f.write('    echo Press any key to Exit...&Pause>nul\n')
            f.write('    goto :eof\n')
            f.write(')\n\n')
            
            f.write('set GIT_LFS_SKIP_SMUDGE=1\n')
            f.write('cd ./ai-toolkit\n\n')
            
            f.write('echo.\n')
            f.write('echo %green%::::::::::::::: Installing %yellow%AI-Toolkit%green% updates... :::::::::::::::%reset%\n')
            f.write('echo.\n')
            f.write('git.exe reset --hard\n')
            f.write('git.exe clean -fd\n')
            f.write('git.exe pull\n')
            f.write('echo.\n')
            f.write('echo %green%::::::: Installing %yellow%requirements %green%and updating %yellow%diffusers%green% :::::::::%reset%\n')
            f.write('echo.\n')
            f.write('..\\python_embeded\\python.exe -I -m pip uninstall diffusers -y\n')
            f.write('..\\python_embeded\\python.exe -I -m pip install -r requirements.txt --no-cache --no-warn-script-location\n\n')
            
            f.write('echo.\n')
            f.write('echo %green%:::::::::::::::   Update completed    :::::::::::::::%reset%\n')
            f.write('if "%~1"=="" (\n')
            f.write('    echo %yellow%::::::::::::::: Press any key to exit :::::::::::::::%reset%&Pause>nul\n')
            f.write('    exit\n')
            f.write(')\n\n')
            f.write('exit\n')
        
        self.log_to_tab("aitoolkit", f"Created {update_bat.name}")
    
    def start_aitoolkit(self):
        """Start AI Toolkit"""
        if self.aitoolkit_starting:
            messagebox.showwarning("Starting", "AI Toolkit is already starting!")
            return
        
        parent_dir = Path(self.aitoolkit_install_parent_var.get())
        start_bat = parent_dir / "Start-AI-Toolkit.bat"
        
        if not start_bat.exists():
            messagebox.showerror("Error", f"Start script not found at {start_bat}\nPlease install first.")
            return
        
        self.aitoolkit_start_btn.state(['disabled'])
        self.aitoolkit_starting = True
        
        thread = threading.Thread(target=self._run_aitoolkit_start, daemon=True)
        thread.start()
    
    def _run_aitoolkit_start(self):
        """Run the AI Toolkit start process"""
        try:
            self.log_to_tab("aitoolkit", "=" * 60)
            self.log_to_tab("aitoolkit", "Starting AI Toolkit")
            self.log_to_tab("aitoolkit", "=" * 60)
            
            parent_dir = Path(self.aitoolkit_install_parent_var.get())
            start_bat = parent_dir / "Start-AI-Toolkit.bat"
            
            self.log_to_tab("aitoolkit", f"\nLaunching: {start_bat}")
            self.log_to_tab("aitoolkit", "The UI will be available at: http://localhost:8675\n")
            
            # Start process with output capture
            self.aitoolkit_process = subprocess.Popen(
                [str(start_bat)],
                cwd=str(parent_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Stream output to log
            import time
            time.sleep(3)
            
            for line in iter(self.aitoolkit_process.stdout.readline, ''):
                if self.aitoolkit_process.poll() is not None:
                    break
                self.log_to_tab("aitoolkit", line.rstrip())
            
            self.aitoolkit_process.stdout.close()
            return_code = self.aitoolkit_process.wait()
            
            if return_code != 0:
                self.log_to_tab("aitoolkit", f"\n[AI Toolkit exited with code {return_code}]")
            else:
                self.log_to_tab("aitoolkit", "\n[AI Toolkit stopped]")
            
        except Exception as e:
            self.log_to_tab("aitoolkit", f"\nERROR: {str(e)}")
            messagebox.showerror("Start Error", f"Failed to start AI Toolkit:\n{str(e)}")
        finally:
            self.aitoolkit_process = None
            import time
            time.sleep(2)
            self.aitoolkit_starting = False
            self.aitoolkit_start_btn.state(['!disabled'])
    
    def update_aitoolkit(self):
        """Update AI Toolkit"""
        parent_dir = Path(self.aitoolkit_install_parent_var.get())
        update_bat = parent_dir / "Update-AI-Toolkit.bat"
        
        if not update_bat.exists():
            messagebox.showerror("Error", f"Update script not found at {update_bat}\nPlease install first.")
            return
        
        if not messagebox.askyesno("Update", "This will update AI Toolkit to the latest version.\nContinue?"):
            return
        
        self.aitoolkit_update_btn.state(['disabled'])
        thread = threading.Thread(target=self._run_aitoolkit_update, daemon=True)
        thread.start()
    
    def _run_aitoolkit_update(self):
        """Run the AI Toolkit update process"""
        try:
            self.log_to_tab("aitoolkit", "=" * 60)
            self.log_to_tab("aitoolkit", "Updating AI Toolkit")
            self.log_to_tab("aitoolkit", "=" * 60)
            
            parent_dir = Path(self.aitoolkit_install_parent_var.get())
            update_bat = parent_dir / "Update-AI-Toolkit.bat"
            
            self.log_to_tab("aitoolkit", f"\nRunning: {update_bat}")
            
            result = subprocess.run(
                [str(update_bat), "silent"],
                capture_output=True,
                text=True,
                cwd=str(parent_dir)
            )
            
            if result.stdout:
                self.log_to_tab("aitoolkit", result.stdout)
            if result.stderr:
                self.log_to_tab("aitoolkit", f"STDERR: {result.stderr}")
            
            if result.returncode == 0:
                self.log_to_tab("aitoolkit", "\nUpdate completed successfully!")
                messagebox.showinfo("Success", "AI Toolkit updated successfully!")
            else:
                self.log_to_tab("aitoolkit", "\nUpdate completed with warnings.")
                messagebox.showwarning("Warning", "Update completed but there may have been issues.\nCheck the log for details.")
            
        except Exception as e:
            self.log_to_tab("aitoolkit", f"\nERROR: {str(e)}")
            messagebox.showerror("Update Error", f"Failed to update AI Toolkit:\n{str(e)}")
        finally:
            self.aitoolkit_update_btn.state(['!disabled'])
    
    def open_aitoolkit_browser(self):
        """Open AI Toolkit in browser"""
        import webbrowser
        webbrowser.open("http://localhost:8675")
        self.log_to_tab("aitoolkit", "Opened browser to http://localhost:8675")
    
    def stop_aitoolkit(self):
        """Stop AI Toolkit process"""
        if messagebox.askyesno("Stop AI Toolkit", "Are you sure you want to stop AI Toolkit?"):
            self.log_to_tab("aitoolkit", "\n[Stopping AI Toolkit...]")
            try:
                import psutil
                import time
                
                processes_killed = []
                
                # Kill the tracked process and its children if it exists
                if self.aitoolkit_process and self.aitoolkit_process.poll() is None:
                    try:
                        parent = psutil.Process(self.aitoolkit_process.pid)
                        children = parent.children(recursive=True)
                        
                        for child in children:
                            try:
                                self.log_to_tab("aitoolkit", f"[Stopping child process: {child.pid} ({child.name()})]")
                                child.terminate()
                                processes_killed.append(child)
                            except psutil.NoSuchProcess:
                                pass
                        
                        parent.terminate()
                        processes_killed.append(parent)
                    except psutil.NoSuchProcess:
                        pass
                
                # Also look for any Node.js processes on port 8675 that might still be running
                for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'connections']):
                    try:
                        # Check if it's a node process related to AI Toolkit
                        if 'node' in proc.info['name'].lower():
                            cmdline = proc.info.get('cmdline', [])
                            if cmdline:
                                cmdline_str = ' '.join(cmdline)
                                if 'ai-toolkit' in cmdline_str.lower() or '8675' in cmdline_str:
                                    self.log_to_tab("aitoolkit", f"[Found AI Toolkit Node process: {proc.pid}]")
                                    proc.terminate()
                                    processes_killed.append(proc)
                                    continue
                            
                            # Check if it's listening on port 8675
                            connections = proc.info.get('connections', [])
                            if connections:
                                for conn in connections:
                                    if hasattr(conn, 'laddr') and conn.laddr.port == 8675:
                                        self.log_to_tab("aitoolkit", f"[Found process on port 8675: {proc.pid}]")
                                        proc.terminate()
                                        processes_killed.append(proc)
                                        break
                    except (psutil.NoSuchProcess, psutil.AccessDenied, AttributeError):
                        continue
                
                # Wait for processes to die
                if processes_killed:
                    gone, alive = psutil.wait_procs(processes_killed, timeout=3)
                    
                    # Force kill any remaining
                    for p in alive:
                        try:
                            self.log_to_tab("aitoolkit", f"[Force killing process: {p.pid}]")
                            p.kill()
                        except psutil.NoSuchProcess:
                            pass
                
                self.log_to_tab("aitoolkit", "[AI Toolkit stopped successfully]")
                
            except ImportError:
                self.log_to_tab("aitoolkit", "[ERROR: psutil not installed. Cannot properly stop AI Toolkit.]")
                self.log_to_tab("aitoolkit", "[Run: pip install psutil]")
                if self.aitoolkit_process:
                    self.aitoolkit_process.terminate()
            except Exception as e:
                self.log_to_tab("aitoolkit", f"[Error stopping AI Toolkit: {str(e)}]")
                messagebox.showerror("Stop Error", f"Failed to stop AI Toolkit:\n{str(e)}")
    
    def restart_aitoolkit(self):
        """Restart AI Toolkit process"""
        self.log_to_tab("aitoolkit", "\n[Restarting AI Toolkit...]")
        
        # Use the stop function logic without the confirmation dialog
        try:
            import psutil
            import time
            
            processes_killed = []
            
            if self.aitoolkit_process and self.aitoolkit_process.poll() is None:
                try:
                    parent = psutil.Process(self.aitoolkit_process.pid)
                    children = parent.children(recursive=True)
                    
                    for child in children:
                        try:
                            child.terminate()
                            processes_killed.append(child)
                        except psutil.NoSuchProcess:
                            pass
                    
                    parent.terminate()
                    processes_killed.append(parent)
                except psutil.NoSuchProcess:
                    pass
            
            # Kill any Node.js processes on port 8675
            for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'connections']):
                try:
                    if 'node' in proc.info['name'].lower():
                        cmdline = proc.info.get('cmdline', [])
                        if cmdline and ('ai-toolkit' in ' '.join(cmdline).lower() or '8675' in ' '.join(cmdline)):
                            proc.terminate()
                            processes_killed.append(proc)
                            continue
                        
                        connections = proc.info.get('connections', [])
                        if connections:
                            for conn in connections:
                                if hasattr(conn, 'laddr') and conn.laddr.port == 8675:
                                    proc.terminate()
                                    processes_killed.append(proc)
                                    break
                except (psutil.NoSuchProcess, psutil.AccessDenied, AttributeError):
                    continue
            
            if processes_killed:
                gone, alive = psutil.wait_procs(processes_killed, timeout=3)
                for p in alive:
                    try:
                        p.kill()
                    except psutil.NoSuchProcess:
                        pass
            
            time.sleep(1)
        except Exception as e:
            self.log_to_tab("aitoolkit", f"[Error during stop: {str(e)}]")
        
        # Start again
        self.start_aitoolkit()
    
    # OneTrainer Methods
    def show_onetrainer_settings(self):
        """Show OneTrainer settings dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title("OneTrainer Settings")
        dialog.geometry("600x200")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Main frame
        main_frame = ttk.Frame(dialog, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        dialog.columnconfigure(0, weight=1)
        dialog.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Installation Directory
        ttk.Label(main_frame, text="Installation Directory:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.onetrainer_install_parent_var).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5)
        ttk.Button(main_frame, text="Browse", command=lambda: self.browse_directory(self.onetrainer_install_parent_var)).grid(row=0, column=2)
        
        # Info
        ttk.Label(main_frame, text="OneTrainer will be installed to: [selected_dir]/OneTrainer", 
                 foreground="gray", font=('Arial', 8)).grid(row=1, column=0, columnspan=3, sticky=tk.W, pady=(0, 15))
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=3, pady=10)
        
        ttk.Button(button_frame, text="Save", command=lambda: [self.save_onetrainer_config(), dialog.destroy()]).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def save_onetrainer_config(self):
        """Save OneTrainer configuration"""
        self.config["onetrainer"]["install_parent_dir"] = self.onetrainer_install_parent_var.get()
        self.save_config()
        # messagebox.showinfo("Success", "OneTrainer configuration saved successfully!")
    
    def install_onetrainer(self):
        """Install OneTrainer in a separate thread"""
        if self.onetrainer_installing:
            messagebox.showwarning("Installation", "OneTrainer installation already in progress!")
            return
        
        self.save_onetrainer_config()
        
        parent_dir = Path(self.onetrainer_install_parent_var.get())
        install_path = parent_dir / "OneTrainer"
        
        if install_path.exists():
            response = messagebox.askyesno("Existing Installation", 
                                          f"OneTrainer already exists at {install_path}.\\n\\nRemove and reinstall?")
            if not response:
                return
        
        self.onetrainer_install_btn.state(['disabled'])
        self.onetrainer_installing = True
        
        thread = threading.Thread(target=self._run_onetrainer_install, daemon=True)
        thread.start()
    
    def _run_onetrainer_install(self):
        """Run OneTrainer installation process"""
        try:
            parent_dir = Path(self.onetrainer_install_parent_var.get())
            install_path = parent_dir / "OneTrainer"
            
            # Remove existing installation
            if install_path.exists():
                import shutil
                self.log_to_tab("onetrainer", f"Removing existing installation: {install_path}")
                shutil.rmtree(install_path)
                self.log_to_tab("onetrainer", "Removed successfully!")
            
            # Create parent directory
            if not parent_dir.exists():
                parent_dir.mkdir(parents=True, exist_ok=True)
                self.log_to_tab("onetrainer", f"Created directory: {parent_dir}")
            
            self.log_to_tab("onetrainer", "=" * 60)
            self.log_to_tab("onetrainer", "Starting OneTrainer Installation")
            self.log_to_tab("onetrainer", "=" * 60)
            self.log_to_tab("onetrainer", f"Parent directory: {parent_dir}")
            self.log_to_tab("onetrainer", f"OneTrainer will be installed to: {install_path}")
            
            # Clone OneTrainer repository
            self.log_to_tab("onetrainer", "\\nCloning OneTrainer repository...")
            result = subprocess.run(
                ["git", "clone", "https://github.com/Nerogar/OneTrainer.git", str(install_path)],
                capture_output=True, text=True
            )
            if result.returncode != 0:
                self.log_to_tab("onetrainer", f"ERROR: {result.stderr}")
                raise Exception("Failed to clone OneTrainer repository")
            self.log_to_tab("onetrainer", "OneTrainer cloned successfully!")
            
            # Create virtual environment
            self.log_to_tab("onetrainer", "\\nCreating Python virtual environment...")
            venv_path = install_path / "venv"
            result = subprocess.run(
                ["python", "-m", "venv", str(venv_path)],
                capture_output=True, text=True
            )
            if result.returncode != 0:
                self.log_to_tab("onetrainer", f"ERROR: {result.stderr}")
                raise Exception("Failed to create virtual environment")
            self.log_to_tab("onetrainer", "Virtual environment created!")
            
            # Get venv python and pip paths
            venv_python = venv_path / "Scripts" / "python.exe"
            venv_pip = venv_path / "Scripts" / "pip.exe"
            
            # Upgrade pip
            self.log_to_tab("onetrainer", "\\nUpgrading pip...")
            result = subprocess.run(
                [str(venv_python), "-m", "pip", "install", "--upgrade", "pip"],
                capture_output=True, text=True
            )
            
            # Install OneTrainer requirements
            # requirements-cuda.txt contains --extra-index-url for PyTorch cu128
            self.log_to_tab("onetrainer", "\\nInstalling OneTrainer requirements...")
            self.log_to_tab("onetrainer", "This includes PyTorch 2.8.0 with CUDA 12.8 from PyTorch's repository")
            self.log_to_tab("onetrainer", "This may take several minutes...")
            requirements_file = install_path / "requirements.txt"
            self._run_command([
                str(venv_pip), "install", "-r", str(requirements_file)
            ], install_path, "onetrainer")
            
            self.log_to_tab("onetrainer", "\\n" + "=" * 60)
            self.log_to_tab("onetrainer", "Installation Complete!")
            self.log_to_tab("onetrainer", "=" * 60)
            messagebox.showinfo("Success", "OneTrainer installed successfully!")
            
        except Exception as e:
            self.log_to_tab("onetrainer", f"\\nERROR: {str(e)}")
            messagebox.showerror("Installation Error", f"Failed to install OneTrainer:\\n{str(e)}")
        finally:
            self.onetrainer_installing = False
            self.onetrainer_install_btn.state(['!disabled'])
    
    def start_onetrainer(self):
        """Start OneTrainer"""
        if self.onetrainer_starting:
            messagebox.showwarning("Starting", "OneTrainer is already starting!")
            return
        
        parent_dir = Path(self.onetrainer_install_parent_var.get())
        install_path = parent_dir / "OneTrainer"
        if not install_path.exists():
            messagebox.showerror("Error", f"OneTrainer not found at {install_path}\\nPlease install first.")
            return
        
        self.onetrainer_start_btn.state(['disabled'])
        self.onetrainer_starting = True
        
        thread = threading.Thread(target=self._run_onetrainer, daemon=True)
        thread.start()
    
    def _run_onetrainer(self):
        """Run OneTrainer process"""
        try:
            self.log_to_tab("onetrainer", "=" * 60)
            self.log_to_tab("onetrainer", "Starting OneTrainer")
            self.log_to_tab("onetrainer", "=" * 60)
            
            parent_dir = Path(self.onetrainer_install_parent_var.get())
            install_path = parent_dir / "OneTrainer"
            venv_python = install_path / "venv" / "Scripts" / "python.exe"
            
            # Build command
            cmd = [str(venv_python), "scripts/train.py", "--ui-server"]
            
            self.log_to_tab("onetrainer", f"\\nRunning: {' '.join(cmd)}")
            self.log_to_tab("onetrainer", "The UI will be available at: http://127.0.0.1:8502\\n")
            
            # Start process with output capture
            self.onetrainer_process = subprocess.Popen(
                cmd,
                cwd=str(install_path),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Stream output to log
            import time
            time.sleep(2)
            self.root.after(100, lambda: self.open_onetrainer_browser())
            
            for line in iter(self.onetrainer_process.stdout.readline, ''):
                if self.onetrainer_process.poll() is not None:
                    break
                self.log_to_tab("onetrainer", line.rstrip())
            
            self.onetrainer_process.stdout.close()
            return_code = self.onetrainer_process.wait()
            
            if return_code != 0:
                self.log_to_tab("onetrainer", f"\\n[OneTrainer exited with code {return_code}]")
            else:
                self.log_to_tab("onetrainer", "\\n[OneTrainer stopped]")
            
        except Exception as e:
            self.log_to_tab("onetrainer", f"\\nERROR: {str(e)}")
            messagebox.showerror("Start Error", f"Failed to start OneTrainer:\\n{str(e)}")
        finally:
            self.onetrainer_process = None
            self.onetrainer_starting = False
            self.onetrainer_start_btn.state(['!disabled'])
    
    def open_onetrainer_browser(self):
        """Open OneTrainer in browser"""
        import webbrowser
        webbrowser.open("http://127.0.0.1:8502")
        self.log_to_tab("onetrainer", "Opened browser to http://127.0.0.1:8502")
    
    def stop_onetrainer(self):
        """Stop OneTrainer process"""
        if self.onetrainer_process is None or self.onetrainer_process.poll() is not None:
            messagebox.showinfo("Stop", "OneTrainer is not currently running.")
            return
        
        if messagebox.askyesno("Stop OneTrainer", "Are you sure you want to stop OneTrainer?"):
            self.log_to_tab("onetrainer", "\\n[Stopping OneTrainer...]")
            try:
                import psutil
                import time
                
                # Get parent process and all children
                try:
                    parent = psutil.Process(self.onetrainer_process.pid)
                    children = parent.children(recursive=True)
                    
                    # Terminate all children first
                    for child in children:
                        try:
                            self.log_to_tab("onetrainer", f"[Stopping child process: {child.pid}]")
                            child.terminate()
                        except psutil.NoSuchProcess:
                            pass
                    
                    # Terminate parent
                    parent.terminate()
                    
                    # Wait for processes to terminate
                    gone, alive = psutil.wait_procs(children + [parent], timeout=3)
                    
                    # Force kill any remaining processes
                    for p in alive:
                        try:
                            self.log_to_tab("onetrainer", f"[Force killing process: {p.pid}]")
                            p.kill()
                        except psutil.NoSuchProcess:
                            pass
                    
                except psutil.NoSuchProcess:
                    pass
                
                self.log_to_tab("onetrainer", "[OneTrainer stopped successfully]")
            except ImportError:
                # Fallback if psutil not available
                self.onetrainer_process.terminate()
                time.sleep(2)
                if self.onetrainer_process.poll() is None:
                    self.onetrainer_process.kill()
                self.log_to_tab("onetrainer", "[OneTrainer stopped]")
            except Exception as e:
                self.log_to_tab("onetrainer", f"[Error stopping OneTrainer: {str(e)}]")
                messagebox.showerror("Stop Error", f"Failed to stop OneTrainer:\\n{str(e)}")
    
    def restart_onetrainer(self):
        """Restart OneTrainer process"""
        self.log_to_tab("onetrainer", "\\n[Restarting OneTrainer...]")
        
        # Stop if running
        if self.onetrainer_process and self.onetrainer_process.poll() is None:
            try:
                import psutil
                import time
                
                parent = psutil.Process(self.onetrainer_process.pid)
                children = parent.children(recursive=True)
                
                for child in children:
                    try:
                        child.terminate()
                    except psutil.NoSuchProcess:
                        pass
                
                parent.terminate()
                gone, alive = psutil.wait_procs(children + [parent], timeout=3)
                
                for p in alive:
                    try:
                        p.kill()
                    except psutil.NoSuchProcess:
                        pass
                
                time.sleep(1)
            except Exception as e:
                self.log_to_tab("onetrainer", f"[Error during stop: {str(e)}]")
        
        # Start again
        self.start_onetrainer()
    
    def update_onetrainer(self):
        """Update OneTrainer"""
        parent_dir = Path(self.onetrainer_install_parent_var.get())
        install_path = parent_dir / "OneTrainer"
        
        if not install_path.exists():
            messagebox.showerror("Error", f"OneTrainer not found at {install_path}\\nPlease install first.")
            return
        
        if not messagebox.askyesno("Update", "This will update OneTrainer to the latest version.\\nContinue?"):
            return
        
        self.onetrainer_update_btn.state(['disabled'])
        thread = threading.Thread(target=self._run_onetrainer_update, daemon=True)
        thread.start()
    
    def _run_onetrainer_update(self):
        """Run OneTrainer update process"""
        try:
            self.log_to_tab("onetrainer", "=" * 60)
            self.log_to_tab("onetrainer", "Updating OneTrainer")
            self.log_to_tab("onetrainer", "=" * 60)
            
            parent_dir = Path(self.onetrainer_install_parent_var.get())
            install_path = parent_dir / "OneTrainer"
            
            # Update git repository
            self.log_to_tab("onetrainer", "\\nUpdating repository...")
            result = subprocess.run(
                ["git", "pull"],
                cwd=str(install_path),
                capture_output=True,
                text=True
            )
            
            if result.stdout:
                self.log_to_tab("onetrainer", result.stdout.strip())
            if result.stderr:
                self.log_to_tab("onetrainer", f"STDERR: {result.stderr}")
            
            # Update requirements
            venv_pip = install_path / "venv" / "Scripts" / "pip.exe"
            requirements_file = install_path / "requirements.txt"
            
            self.log_to_tab("onetrainer", "\\nUpdating requirements...")
            result = subprocess.run(
                [str(venv_pip), "install", "-r", str(requirements_file), "--upgrade"],
                cwd=str(install_path),
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                self.log_to_tab("onetrainer", "\\nUpdate completed successfully!")
                messagebox.showinfo("Success", "OneTrainer updated successfully!")
            else:
                self.log_to_tab("onetrainer", "\\nUpdate completed with warnings.")
                if result.stderr:
                    self.log_to_tab("onetrainer", f"STDERR: {result.stderr}")
                messagebox.showwarning("Warning", "Update completed but there may have been issues.\\nCheck the log for details.")
            
        except Exception as e:
            self.log_to_tab("onetrainer", f"\\nERROR: {str(e)}")
            messagebox.showerror("Update Error", f"Failed to update OneTrainer:\\n{str(e)}")
        finally:
            self.onetrainer_update_btn.state(['!disabled'])


def main():
    if THEME_AVAILABLE:
        # Load config to get theme
        config_file = Path(__file__).parent / "ailab_config.json"
        theme = "darkly"
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    config = json.load(f)
                    theme = config.get('theme', 'darkly')
            except:
                pass
        root = ttk.Window(themename=theme)
    else:
        root = tk.Tk()
    app = AILabManager(root)
    root.mainloop()


if __name__ == "__main__":
    main()
