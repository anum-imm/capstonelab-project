# Run from project root. Requires Docker Desktop.
# Set OPENAI_API_KEY in your environment before running (do not commit keys).
# Usage: powershell -ExecutionPolicy Bypass -File scripts\generate_docker_build_log.ps1

$ErrorActionPreference = "Continue"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root
$log = Join-Path $root "docker_build.log"

function Write-LogSection {
    param([string]$Title)
    "`n=== $Title === $(Get-Date -Format o) ===`n" | Add-Content -Path $log -Encoding utf8
}

Remove-Item $log -ErrorAction SilentlyContinue
"docker_build.log — capstonelab Docker lab`nGenerated: $(Get-Date -Format o)" | Out-File -FilePath $log -Encoding utf8

Write-LogSection "docker compose build"
docker compose build 2>&1 | Add-Content -Path $log -Encoding utf8

Write-LogSection "docker compose up -d"
docker compose up -d 2>&1 | Add-Content -Path $log -Encoding utf8

Write-LogSection "docker ps"
docker ps 2>&1 | Add-Content -Path $log -Encoding utf8

Write-Host "Done. See $log"
