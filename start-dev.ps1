param(
    [int]$BackendPort = 8000,
    [int]$FrontendPort = 5174,
    [string]$MysqlServiceName = "MySQL80"
)

$ErrorActionPreference = "Stop"

function Write-Step {
    param([string]$Message)
    Write-Host "[AI Mall] $Message" -ForegroundColor Cyan
}

function Test-PortListening {
    param([int]$Port)
    $connections = netstat -ano | Select-String -Pattern ":$Port\s+.*LISTENING"
    return [bool]$connections
}

function Wait-HttpOk {
    param(
        [string]$Url,
        [int]$TimeoutSeconds = 45
    )

    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    while ((Get-Date) -lt $deadline) {
        try {
            $response = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 3
            if ($response.StatusCode -ge 200 -and $response.StatusCode -lt 500) {
                return $true
            }
        }
        catch {
            Start-Sleep -Seconds 1
        }
    }
    return $false
}

$RootDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$BackendDir = Join-Path $RootDir "backend"
$FrontendDir = Join-Path $RootDir "frontend"
$PythonExe = Join-Path $BackendDir ".venv\Scripts\python.exe"
$FrontendUrl = "http://127.0.0.1:$FrontendPort/"
$BackendHealthUrl = "http://127.0.0.1:$BackendPort/api/health"

Write-Step "Project root: $RootDir"

if (-not (Test-Path $PythonExe)) {
    Write-Host "Backend virtual environment not found: $PythonExe" -ForegroundColor Red
    Write-Host "Please run:"
    Write-Host "  cd backend"
    Write-Host "  python -m venv .venv"
    Write-Host "  .\.venv\Scripts\python.exe -m pip install -r requirements.txt"
    Read-Host "Press Enter to exit"
    exit 1
}

if (-not (Test-Path (Join-Path $FrontendDir "node_modules"))) {
    Write-Host "Frontend dependencies not found: frontend\node_modules" -ForegroundColor Red
    Write-Host "Please run:"
    Write-Host "  cd frontend"
    Write-Host "  npm install"
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Step "Checking MySQL service: $MysqlServiceName"
try {
    $mysql = Get-Service -Name $MysqlServiceName -ErrorAction Stop
    if ($mysql.Status -ne "Running") {
        Write-Step "Starting MySQL service..."
        Start-Service -Name $MysqlServiceName
        Start-Sleep -Seconds 2
    }
    else {
        Write-Step "MySQL is already running."
    }
}
catch {
    Write-Host "Could not start or check MySQL service '$MysqlServiceName'." -ForegroundColor Yellow
    Write-Host "If the backend cannot connect to MySQL, open PowerShell as Administrator and run:"
    Write-Host "  net start $MysqlServiceName"
}

if (Test-PortListening -Port $BackendPort) {
    Write-Step "Backend port $BackendPort is already in use. Reusing existing backend."
}
else {
    Write-Step "Starting backend on http://127.0.0.1:$BackendPort"
    $backendCommand = "cd `"$BackendDir`"; & `"$PythonExe`" -m uvicorn app.main:app --reload --host 127.0.0.1 --port $BackendPort"
    Start-Process powershell.exe -ArgumentList @("-NoExit", "-ExecutionPolicy", "Bypass", "-Command", $backendCommand)
}

if (-not (Wait-HttpOk -Url $BackendHealthUrl -TimeoutSeconds 45)) {
    Write-Host "Backend did not become ready in time: $BackendHealthUrl" -ForegroundColor Yellow
    Write-Host "Please check the backend PowerShell window for errors."
}
else {
    Write-Step "Backend is ready."
}

if (Test-PortListening -Port $FrontendPort) {
    Write-Step "Frontend port $FrontendPort is already in use. Reusing existing frontend."
}
else {
    Write-Step "Starting frontend on $FrontendUrl"
    $frontendCommand = "cd `"$FrontendDir`"; npm.cmd run dev -- --host 127.0.0.1 --port $FrontendPort --strictPort"
    Start-Process powershell.exe -ArgumentList @("-NoExit", "-ExecutionPolicy", "Bypass", "-Command", $frontendCommand)
}

if (-not (Wait-HttpOk -Url $FrontendUrl -TimeoutSeconds 45)) {
    Write-Host "Frontend did not become ready in time: $FrontendUrl" -ForegroundColor Yellow
    Write-Host "Please check the frontend PowerShell window for errors."
}
else {
    Write-Step "Opening browser: $FrontendUrl"
    Start-Process $FrontendUrl
}

Write-Step "Done. Keep the backend and frontend PowerShell windows open while developing."
