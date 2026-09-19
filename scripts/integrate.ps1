# ============================================================
# TerraFlux Master Integration Script
# ============================================================
# Run this from PowerShell in d:\fintech
# This script merges all component branches and prepares
# the integration/terraflux branch for full system assembly.
# ============================================================

$ErrorActionPreference = "Stop"

Write-Host "============================================" -ForegroundColor Cyan
Write-Host " TerraFlux Integration - Phase 1: Merge" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan

# Verify we're on integration/terraflux
$branch = git branch --show-current
if ($branch -ne "integration/terraflux") {
    Write-Host "ERROR: Not on integration/terraflux. Current branch: $branch" -ForegroundColor Red
    Write-Host "Run: git checkout integration/terraflux" -ForegroundColor Yellow
    exit 1
}

Write-Host "`n[1/6] Verifying backup/frontend-v1 exists remotely..." -ForegroundColor Yellow
$backup = git branch -a | Select-String "backup/frontend-v1"
if ($backup) {
    Write-Host "  OK: backup/frontend-v1 found remotely" -ForegroundColor Green
} else {
    Write-Host "  WARNING: backup/frontend-v1 not found remotely" -ForegroundColor Red
}

Write-Host "`n[2/6] Merging backend/ramraj..." -ForegroundColor Yellow
git merge backend/ramraj --no-edit
if ($LASTEXITCODE -ne 0) {
    Write-Host "  MERGE CONFLICT: Resolve conflicts then re-run" -ForegroundColor Red
    exit 1
}
Write-Host "  OK: backend merged" -ForegroundColor Green

Write-Host "`n[3/6] Merging infra/akshaya..." -ForegroundColor Yellow
git merge infra/akshaya --no-edit
if ($LASTEXITCODE -ne 0) {
    Write-Host "  MERGE CONFLICT: Resolve conflicts then re-run" -ForegroundColor Red
    exit 1
}
Write-Host "  OK: infra merged" -ForegroundColor Green

Write-Host "`n[4/6] Merging ai/sanju..." -ForegroundColor Yellow
git merge ai/sanju --no-edit
if ($LASTEXITCODE -ne 0) {
    Write-Host "  MERGE CONFLICT: Resolve conflicts then re-run" -ForegroundColor Red
    exit 1
}
Write-Host "  OK: AI merged" -ForegroundColor Green

Write-Host "`n[5/6] Replacing frontend with D:\frontend source..." -ForegroundColor Yellow
# Remove old frontend content (keep directory)
if (Test-Path "frontend\*") {
    Remove-Item -Recurse -Force frontend\*
}
# Copy new frontend source (exclude .git, node_modules, .next)
robocopy D:\frontend frontend /E /XD .git node_modules .next /NFL /NDL /NJH /NJS /NC /NS
Write-Host "  OK: New frontend copied" -ForegroundColor Green

Write-Host "`n[6/6] Installing frontend dependencies..." -ForegroundColor Yellow
Push-Location frontend
npm install
Pop-Location
Write-Host "  OK: Dependencies installed" -ForegroundColor Green

Write-Host "`n============================================" -ForegroundColor Cyan
Write-Host " Phase 1 Complete!" -ForegroundColor Cyan  
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Start a new Antigravity agent session" -ForegroundColor White
Write-Host "  2. The agent will continue integration from here" -ForegroundColor White
Write-Host ""

# Show status
git log --oneline -10
git status --short

