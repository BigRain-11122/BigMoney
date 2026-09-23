# Install Tailscale on Windows (Master laptop or Worker PC).
# Run in PowerShell as Administrator.

Write-Host "=== Tailscale setup (Windows) ===" -ForegroundColor Cyan

# 1. Check if Tailscale is already installed
$ts = Get-Command tailscale -ErrorAction SilentlyContinue
if (-not $ts) {
    Write-Host "[1/4] Downloading Tailscale installer..."
    $installer = "$env:TEMP\tailscale-setup.exe"
    Invoke-WebRequest -Uri "https://pkgs.tailscale.com/stable/tailscale-setup-latest-amd64.msi" `
        -OutFile $installer
    Write-Host "[2/4] Installing (will pop UAC)..."
    Start-Process msiexec.exe -ArgumentList "/i", "`"$installer`"", "/quiet", "ADDLOCAL=Tailscale" -Wait
} else {
    Write-Host "[1/4] Tailscale already installed."
}

# 2. Bring up
Write-Host "[3/4] Running tailscale up (browser will open for login)..."
tailscale up

# 3. Show our IP
Write-Host "[4/4] Tailscale status:" -ForegroundColor Green
tailscale ip -4
tailscale status
