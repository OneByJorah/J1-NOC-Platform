<# 
.SYNOPSIS
    Build J1 NOC Windows Agent executable using PyInstaller

.DESCRIPTION
    This script creates a standalone Windows executable (.exe) from the Python agent.
    Run this on a Windows machine with Python 3.10+ installed.

.PREREQUISITES
    - Python 3.10+
    - pip install -r requirements.txt
    - Run as Administrator (recommended for pywin32)

.USAGE
    .\build.ps1
    .\build.ps1 -Clean
#>

param(
    [switch]$Clean
)

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$AgentDir = "$ScriptDir"
$DistDir = "$AgentDir\dist"
$BuildDir = "$AgentDir\build"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  J1 NOC Windows Agent Build Script" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Check Python
$pythonVersion = python --version 2>&1
if (-not $pythonVersion) {
    Write-Error "Python not found in PATH. Please install Python 3.10+"
    exit 1
}
Write-Host "Using: $pythonVersion" -ForegroundColor Green

# Install dependencies
Write-Host "Installing dependencies..." -ForegroundColor Yellow
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to install dependencies"
    exit 1
}

# Clean previous builds
if ($Clean -or (Test-Path $DistDir) -or (Test-Path $BuildDir)) {
    Write-Host "Cleaning previous builds..." -ForegroundColor Yellow
    if (Test-Path $DistDir) { Remove-Item -Recurse -Force $DistDir }
    if (Test-Path $BuildDir) { Remove-Item -Recurse -Force $BuildDir }
    if (Test-Path "$AgentDir\j1noc-agent.spec") {
        # Spec file is kept
    }
}

# Build with PyInstaller
Write-Host "Building executable..." -ForegroundColor Yellow
python -m PyInstaller --clean j1noc-agent.spec
if ($LASTEXITCODE -ne 0) {
    Write-Error "PyInstaller build failed"
    exit 1
}

# Verify output
$ExePath = "$DistDir\j1noc-agent.exe"
if (Test-Path $ExePath) {
    $size = (Get-Item $ExePath).Length / 1MB
    Write-Host ""
    Write-Host "==========================================" -ForegroundColor Green
    Write-Host "  BUILD SUCCESSFUL!" -ForegroundColor Green
    Write-Host "==========================================" -ForegroundColor Green
    Write-Host "Output: $ExePath" -ForegroundColor Green
    Write-Host "Size:   {0:N1} MB" -f $size -ForegroundColor Green
    Write-Host ""
    Write-Host "Deployment:" -ForegroundColor Cyan
    Write-Host "  1. Copy j1noc-agent.exe to target Windows machine" -ForegroundColor Cyan
    Write-Host "  2. Create config.json in %APPDATA%\j1noc\" -ForegroundColor Cyan
    Write-Host "  3. Set NOC_URL and AGENT_TOKEN environment variables" -ForegroundColor Cyan
    Write-Host "  4. Run: j1noc-agent.exe" -ForegroundColor Cyan
    Write-Host "  5. Or install as service: .\install-service.ps1" -ForegroundColor Cyan
} else {
    Write-Error "Executable not found at expected path: $ExePath"
    exit 1
}