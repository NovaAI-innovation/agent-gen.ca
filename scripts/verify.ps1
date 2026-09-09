/**
 * verify.ps1 — local quality gate for agent-gen.ca
 *
 * Runs the same checks that CI enforces. Exit code 0 = all green.
 *
 * Usage:
 *   pwsh scripts/verify.ps1           # full run
 *   pwsh scripts/verify.ps1 -SkipE2E  # skip Playwright E2E tests
 */

param(
    [switch]$SkipE2E
)

$ErrorActionPreference = 'Stop'
$PSNativeCommandUseErrorActionPreference = $true

$root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)

function Invoke-Step {
    param([string]$Name, [scriptblock]$Action)
    Write-Host "`n━━━ $Name ━━━" -ForegroundColor Cyan
    & $Action
    if ($LASTEXITCODE -ne 0) {
        Write-Host "FAILED: $Name" -ForegroundColor Red
        exit $LASTEXITCODE
    }
    Write-Host "✓ $Name" -ForegroundColor Green
}

# ── Frontend ──────────────────────────────────────────────────────────────

Invoke-Step "Frontend: install" {
    Push-Location "$root\frontend"
    npm ci
    Pop-Location
}

Invoke-Step "Frontend: lint" {
    Push-Location "$root\frontend"
    npm run lint
    Pop-Location
}

Invoke-Step "Frontend: unit tests" {
    Push-Location "$root\frontend"
    npm test -- --run
    Pop-Location
}

Invoke-Step "Frontend: build" {
    Push-Location "$root\frontend"
    npm run build
    Pop-Location
}

# ── Backend ───────────────────────────────────────────────────────────────

Invoke-Step "Backend: install" {
    Push-Location "$root\backend"
    pip install -e .[dev] -q
    Pop-Location
}

Invoke-Step "Backend: pytest" {
    Push-Location "$root\backend"
    pytest -q
    Pop-Location
}

Invoke-Step "Backend: black (check)" {
    Push-Location "$root\backend"
    black --check .
    Pop-Location
}

Invoke-Step "Backend: isort (check)" {
    Push-Location "$root\backend"
    isort --check-only .
    Pop-Location
}

# ── E2E ───────────────────────────────────────────────────────────────────

if (-not $SkipE2E) {
    Invoke-Step "E2E: Playwright smoke" {
        Push-Location "$root\frontend"
        npx playwright test --project=chromium
        Pop-Location
    }
} else {
    Write-Host "`n⚠ E2E tests skipped (-SkipE2E)" -ForegroundColor Yellow
}

Write-Host "`n✅ All checks passed." -ForegroundColor Green
