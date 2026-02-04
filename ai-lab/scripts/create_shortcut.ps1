param(
    [string]$ExePath = "$PSScriptRoot\..\dist\AILab_Manager.exe"
)

# Get the Desktop path
$DesktopPath = [Environment]::GetFolderPath("Desktop")
$ShortcutPath = "$DesktopPath\AI-Lab Manager.lnk"

# Resolve the absolute path
$ExePath = Resolve-Path $ExePath -ErrorAction SilentlyContinue

if (-not $ExePath -or -not (Test-Path $ExePath)) {
    Write-Host "Error: Executable not found at $ExePath" -ForegroundColor Red
    Write-Host "Please build the executable first using scripts\build_exe.bat" -ForegroundColor Yellow
    pause
    exit 1
}

# Create the shortcut
$WScriptShell = New-Object -ComObject WScript.Shell
$Shortcut = $WScriptShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = $ExePath
$Shortcut.WorkingDirectory = Split-Path $ExePath
$Shortcut.Description = "AI-Lab Manager - Unified ComfyUI and AI Toolkit Manager"
$Shortcut.Save()

Write-Host "Success! Desktop shortcut created:" -ForegroundColor Green
Write-Host "  $ShortcutPath" -ForegroundColor Cyan
Write-Host ""
pause
