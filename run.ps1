<#
.SYNOPSIS
    Starts the inference server + capture client, or runs training.
.PARAMETER Mode
    "inference" (default) starts the server and capture client together.
    "train" runs the PPO training loop in the foreground.
.PARAMETER Control
    (inference) Enable virtual controller input.
.PARAMETER CaptureFrames
    (inference) Save captured frames to disk instead of streaming.
.PARAMETER Port
    (inference) WebSocket port (default: 8765).
.PARAMETER Model
    Path to a PPO model checkpoint. Defaults to MODEL_PATH from .env.
.PARAMETER Timesteps
    (train) Total environment timesteps (default: 1000000).
.EXAMPLE
    .\run.ps1
    .\run.ps1 -Control
    .\run.ps1 -Mode train
    .\run.ps1 -Mode train -Timesteps 2000000 -Model models/my_model.zip
#>
param(
    [ValidateSet("inference", "train")]
    [string]$Mode = "inference",
    [switch]$Control,
    [switch]$CaptureFrames,
    [int]$Port = 8765,
    [string]$Model = "",
    [int]$Timesteps = 1000000
)

Set-StrictMode -Version Latest
$root = $PSScriptRoot
Set-Location $root

if (-not (Get-Command conda -ErrorAction SilentlyContinue)) {
    Write-Error "conda not found in PATH. Open an Anaconda Prompt or add conda to your PATH."
    exit 1
}

# --- Training mode: run in foreground, no server window or client needed ---
if ($Mode -eq "train") {
    Write-Host "[run] Starting training..." -ForegroundColor Cyan
    $trainArgs = [System.Collections.Generic.List[string]]::new()
    $trainArgs.AddRange([string[]]@("--mode", "train", "--timesteps", "$Timesteps"))
    if ($Model) { $trainArgs.Add("--model"); $trainArgs.Add($Model) }
    conda run --no-capture-output -n br2-ai python -m training.main @trainArgs
    exit
}

# --- Inference mode: server in new window, client in foreground ---
$serverCmd = "conda run --no-capture-output -n br2-ai python -m training.main --mode inference --host 0.0.0.0 --port $Port"
if ($Model) {
    $serverCmd += " --model `"$Model`""
}

$psArgs = @("-NoExit", "-Command", $serverCmd)

Write-Host "[run] Starting inference server..." -ForegroundColor Cyan
$serverProc = Start-Process -PassThru -FilePath powershell -ArgumentList $psArgs -WorkingDirectory $root

Write-Host "[run] Server PID $($serverProc.Id) - waiting for /health (up to 60s)..." -ForegroundColor Cyan

try {
    $ready = $false
    for ($i = 0; $i -lt 60; $i++) {
        try {
            $null = Invoke-WebRequest "http://127.0.0.1:$Port/health" -UseBasicParsing -TimeoutSec 2 -ErrorAction Stop
            $ready = $true
            break
        } catch {
            Start-Sleep 1
        }
    }

    if (-not $ready) {
        throw "[run] Server did not become ready within 60 seconds. Check the server window for errors."
    }

    Write-Host "[run] Server ready. Starting capture client..." -ForegroundColor Green

    # Only pass boolean flags when explicitly set to avoid argparse bool() quirk
    $clientArgs = [System.Collections.Generic.List[string]]::new()
    $clientArgs.AddRange([string[]]@("--host", "127.0.0.1", "--port", "$Port"))
    if ($Control)       { $clientArgs.Add("--control");       $clientArgs.Add("True") }
    if ($CaptureFrames) { $clientArgs.Add("--capture_frames"); $clientArgs.Add("True") }

    conda run --no-capture-output -n br2-ai python -m capture.ws_client @clientArgs

} finally {
    Write-Host ""
    Write-Host "[run] Shutting down server (PID $($serverProc.Id))..." -ForegroundColor Yellow
    $null = & taskkill /F /T /PID $serverProc.Id 2>&1
    Write-Host "[run] Done." -ForegroundColor Yellow
}
