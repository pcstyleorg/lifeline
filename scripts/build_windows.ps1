Param(
    [string]$PythonBin = "python"
)

$ErrorActionPreference = "Stop"

# Thin wrapper for Windows build.
# Delegates all logic to the unified Python orchestrator:
#   python -m scripts.build --target windows --component all

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Resolve-Path (Join-Path $ScriptDir "..")

Write-Host "[build-windows] Using Python: $PythonBin"
Write-Host "[build-windows] Invoking orchestrator for Windows (all components)"

Push-Location $RepoRoot
try {
    & $PythonBin -m scripts.build --target windows --component all
}
finally {
    Pop-Location
}

Write-Host "[build-windows] Completed. Artifacts are under .\build"