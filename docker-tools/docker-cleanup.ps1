# ================================
# Safe Docker Desktop Cleanup Tool
# ================================

Write-Host "Docker Cleanup Utility (Safe Mode)" -ForegroundColor Cyan
Write-Host "This will remove Docker data from C: drive step-by-step." -ForegroundColor Yellow
Write-Host ""

# Step 1: Confirm start
$confirmStart = Read-Host "Do you want to proceed? (yes/no)"
if ($confirmStart -ne "yes") {
    Write-Host "Aborted." -ForegroundColor Red
    exit
}

# Step 2: Stop Docker Desktop
Write-Host "`n[Step 1] Stopping Docker Desktop..." -ForegroundColor Cyan
Stop-Process -Name "Docker Desktop" -Force -ErrorAction SilentlyContinue
wsl --shutdown
Write-Host "Docker & WSL stopped."

# Step 3: Show WSL distros
Write-Host "`n[Step 2] Current WSL distros:" -ForegroundColor Cyan
wsl -l -v

$confirmWSL = Read-Host "Do you want to remove Docker WSL distros? (yes/no)"
if ($confirmWSL -eq "yes") {
    Write-Host "Removing docker-desktop..."
    wsl --unregister docker-desktop 2>$null

    Write-Host "Removing docker-desktop-data..."
    wsl --unregister docker-desktop-data 2>$null

    Write-Host "WSL distros removed."
} else {
    Write-Host "Skipping WSL removal."
}

# Step 4: Remove Docker folders from C:
$paths = @(
    "$env:LOCALAPPDATA\Docker",
    "$env:LOCALAPPDATA\Docker Desktop",
    "$env:APPDATA\Docker",
    "C:\ProgramData\Docker"
)

Write-Host "`n[Step 3] Docker directories found:" -ForegroundColor Cyan

foreach ($path in $paths) {
    if (Test-Path $path) {
        Write-Host "Found: $path" -ForegroundColor Yellow
        $confirmDelete = Read-Host "Delete this folder? (yes/no)"
        if ($confirmDelete -eq "yes") {
            Remove-Item -Recurse -Force $path
            Write-Host "Deleted: $path" -ForegroundColor Green
        } else {
            Write-Host "Skipped: $path"
        }
    }
}

# Step 5: Optional uninstall reminder
Write-Host "`n[Step 4] Optional: Uninstall Docker Desktop from Apps & Features." -ForegroundColor Cyan
$confirmFinal = Read-Host "Open uninstall settings now? (yes/no)"

if ($confirmFinal -eq "yes") {
    Start-Process "ms-settings:appsfeatures"
}

Write-Host "`nCleanup completed." -ForegroundColor Green
Write-Host "You can now reinstall Docker and set a new drive (e.g., H:\DockerData)." -ForegroundColor Cyan