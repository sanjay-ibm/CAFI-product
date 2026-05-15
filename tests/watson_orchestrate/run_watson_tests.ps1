# Watson Orchestrate Test Runner Script (Windows PowerShell)
# 
# Usage:
#   .\run_watson_tests.ps1 -All
#   .\run_watson_tests.ps1 -Baseline
#   .\run_watson_tests.ps1 -Drift
#   .\run_watson_tests.ps1 -Quick

param(
    [Parameter(ParameterSetName='All')]
    [switch]$All,
    
    [Parameter(ParameterSetName='Baseline')]
    [switch]$Baseline,
    
    [Parameter(ParameterSetName='Drift')]
    [switch]$Drift,
    
    [Parameter(ParameterSetName='Performance')]
    [switch]$Performance,
    
    [Parameter(ParameterSetName='Category')]
    [ValidateSet('product_specific', 'general_ibm', 'multi_turn', 'product_comparison', 'troubleshooting')]
    [string]$Category,
    
    [Parameter(ParameterSetName='Quick')]
    [switch]$Quick,
    
    [Parameter(ParameterSetName='Check')]
    [switch]$Check,
    
    [switch]$VerboseOutput,
    [switch]$Html,
    [switch]$Coverage,
    [switch]$Parallel,
    [int]$Workers = 4,
    [switch]$Summary
)

# Script directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

# Load environment variables from .env if exists
$EnvFile = Join-Path $ScriptDir ".env"
if (Test-Path $EnvFile) {
    Write-Host "Loading environment from .env" -ForegroundColor Blue
    Get-Content $EnvFile | ForEach-Object {
        if ($_ -match '^([^#][^=]+)=(.*)$') {
            $name = $matches[1].Trim()
            $value = $matches[2].Trim()
            [Environment]::SetEnvironmentVariable($name, $value, "Process")
        }
    }
}

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "Error: Python is not installed or not in PATH" -ForegroundColor Red
    exit 1
}

# Check if pytest is installed
try {
    python -c "import pytest" 2>&1 | Out-Null
} catch {
    Write-Host "Warning: pytest is not installed" -ForegroundColor Yellow
    Write-Host "Installing pytest..." -ForegroundColor Blue
    pip install pytest pytest-html pytest-xdist requests
}

# Build arguments for Python script
$args = @()

if ($All) { $args += "--all" }
if ($Baseline) { $args += "--baseline" }
if ($Drift) { $args += "--drift" }
if ($Performance) { $args += "--performance" }
if ($Category) { $args += "--category", $Category }
if ($Quick) { $args += "--quick" }
if ($Check) { $args += "--check" }
if ($VerboseOutput) { $args += "--verbose" }
if ($Html) { $args += "--html" }
if ($Coverage) { $args += "--coverage" }
if ($Parallel) { $args += "--parallel", "--workers", $Workers }
if ($Summary) { $args += "--summary" }

# Run the Python test runner
Write-Host "Starting Watson Orchestrate Tests" -ForegroundColor Green
Write-Host "Command: python run_watson_tests.py $($args -join ' ')" -ForegroundColor Cyan

$exitCode = 0
try {
    python run_watson_tests.py @args
    $exitCode = $LASTEXITCODE
} catch {
    Write-Host "Error running tests: $_" -ForegroundColor Red
    $exitCode = 1
}

if ($exitCode -eq 0) {
    Write-Host "`n✅ Tests completed successfully" -ForegroundColor Green
} else {
    Write-Host "`n❌ Tests failed with exit code $exitCode" -ForegroundColor Red
}

exit $exitCode

# Made with Bob
