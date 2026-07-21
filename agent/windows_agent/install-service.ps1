<# 
.SYNOPSIS
    Install J1 NOC Windows Agent as a Windows Service

.DESCRIPTION
    Installs the agent as a Windows Service using NSSM (Non-Sucking Service Manager)
    or Windows built-in sc.exe. Requires Administrator privileges.

.PREREQUISITES
    - j1noc-agent.exe built and available
    - Run as Administrator

.USAGE
    .\install-service.ps1
    .\install-service.ps1 -NocUrl "http://your-noc:8000" -Token "your-token"
#>

param(
    [string]$NocUrl = "http://127.0.0.1:8000",
    [string]$Token = "change-me",
    [string]$AgentPath = "",
    [string]$ServiceName = "J1NOC-Agent",
    [string]$DisplayName = "J1 NOC Windows Agent",
    [string]$Description = "Collects Windows services, events, and logs for J1 NOC Platform"
)

$ErrorActionPreference = "Stop"

# Check admin
$currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
if (-not $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Error "This script must be run as Administrator"
    exit 1
}

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
if (-not $AgentPath) {
    $AgentPath = "$ScriptDir\dist\j1noc-agent.exe"
}

if (-not (Test-Path $AgentPath)) {
    Write-Error "Agent executable not found at: $AgentPath"
    Write-Host "Run .\build.ps1 first, or specify -AgentPath"
    exit 1
}

# Resolve full path
$AgentPath = Resolve-Path $AgentPath

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  Installing J1 NOC Agent as Service" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Executable: $AgentPath"
Write-Host "Service:    $ServiceName"
Write-Host "NOC URL:    $NocUrl"
Write-Host ""

# Check if service exists
$existing = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
if ($existing) {
    Write-Host "Service exists, stopping and removing..." -ForegroundColor Yellow
    Stop-Service -Name $ServiceName -Force -ErrorAction SilentlyContinue
    sc.exe delete $ServiceName | Out-Null
    Start-Sleep -Seconds 2
}

# Create service using sc.exe (built-in)
$cmd = "`"$AgentPath`""
$envArgs = "NOC_URL=$NocUrl AGENT_TOKEN=$Token"

# Using NSSM if available, otherwise sc.exe
$nssmPath = Get-Command nssm -ErrorAction SilentlyContinue
if ($nssmPath) {
    Write-Host "Using NSSM for service installation..." -ForegroundColor Green
    & $nssmPath install $ServiceName $AgentPath
    & $nssmPath set $ServiceName AppEnvironmentExtra "NOC_URL=$NocUrl" "AGENT_TOKEN=$Token"
    & $nssmPath set $ServiceName DisplayName $DisplayName
    & $nssmPath set $ServiceName Description $Description
    & $nssmPath set $ServiceName Start SERVICE_AUTO_START
    & $nssmPath set $ServiceName AppStdout "$env:ProgramData\J1NOC\agent.log"
    & $nssmPath set $ServiceName AppStderr "$env:ProgramData\J1NOC\agent-error.log"
    & $nssmPath set $ServiceName AppRotateFiles 1
    & $nssmPath set $ServiceName AppRotateOnline 1
} else {
    Write-Host "NSSM not found, using sc.exe (basic)..." -ForegroundColor Yellow
    Write-Host "Note: Environment variables must be set system-wide or use NSSM" -ForegroundColor Yellow
    
    # Set env vars system-wide (requires reboot to take effect for services)
    [Environment]::SetEnvironmentVariable("NOC_URL", $NocUrl, "Machine")
    [Environment]::SetEnvironmentVariable("AGENT_TOKEN", $Token, "Machine")
    
    sc.exe create $ServiceName binPath= "$AgentPath" DisplayName= "$DisplayName" start= auto
    sc.exe description $ServiceName $Description
}

# Configure recovery (restart on failure)
sc.exe failure $ServiceName reset= 86400 actions= restart/5000/restart/10000/restart/60000

# Start service
Write-Host "Starting service..." -ForegroundColor Green
Start-Service -Name $ServiceName

Start-Sleep -Seconds 3

$svc = Get-Service -Name $ServiceName
if ($svc.Status -eq 'Running') {
    Write-Host ""
    Write-Host "==========================================" -ForegroundColor Green
    Write-Host "  SERVICE INSTALLED AND RUNNING!" -ForegroundColor Green
    Write-Host "==========================================" -ForegroundColor Green
    Write-Host "Service Name: $ServiceName" -ForegroundColor Green
    Write-Host "Status:       $($svc.Status)" -ForegroundColor Green
    Write-Host ""
    Write-Host "Logs (NSSM):  C:\ProgramData\J1NOC\agent.log" -ForegroundColor Cyan
    Write-Host "Logs (sc):    Event Viewer -> Windows Logs -> Application" -ForegroundColor Cyan
} else {
    Write-Error "Service failed to start. Status: $($svc.Status)"
    Write-Host "Check logs: Get-EventLog -LogName Application -Source $ServiceName" -ForegroundColor Red
    exit 1
}