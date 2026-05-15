# Automated test runner script for Product Catalog API (PowerShell)
# Usage: .\scripts\run_tests.ps1 [options]

param(
    [switch]$Help,
    [switch]$Verbose,
    [switch]$Quiet,
    [switch]$StopOnFail,
    [string]$Markers,
    [string]$Keyword,
    [int]$Parallel,
    [switch]$NoCov,
    [switch]$Html,
    [switch]$Xml,
    [switch]$Unit,
    [switch]$Integration,
    [switch]$Smoke,
    [switch]$Slow,
    [switch]$Watch
)

# Colors for output
function Write-ColorOutput($ForegroundColor) {
    $fc = $host.UI.RawUI.ForegroundColor
    $host.UI.RawUI.ForegroundColor = $ForegroundColor
    if ($args) {
        Write-Output $args
    }
    $host.UI.RawUI.ForegroundColor = $fc
}

# Print usage
function Show-Usage {
    Write-Host ""
    Write-Host "Usage: .\scripts\run_tests.ps1 [options]"
    Write-Host ""
    Write-Host "Options:"
    Write-Host "  -Help               Show this help message"
    Write-Host "  -Verbose            Verbose output"
    Write-Host "  -Quiet              Minimal output"
    Write-Host "  -StopOnFail         Stop on first failure"
    Write-Host "  -Markers <markers>  Run tests with specific markers (e.g., 'unit', 'integration')"
    Write-Host "  -Keyword <keyword>  Run tests matching keyword expression"
    Write-Host "  -Parallel <n>       Run tests in parallel with N workers"
    Write-Host "  -NoCov              Skip coverage report"
    Write-Host "  -Html               Generate HTML coverage report"
    Write-Host "  -Xml                Generate XML coverage report"
    Write-Host "  -Unit               Run only unit tests"
    Write-Host "  -Integration        Run only integration tests"
    Write-Host "  -Smoke              Run only smoke tests"
    Write-Host "  -Slow               Include slow tests"
    Write-Host "  -Watch              Watch mode - rerun on file changes"
    Write-Host ""
    exit 0
}

if ($Help) {
    Show-Usage
}

# Print header
Write-ColorOutput Cyan "========================================"
Write-ColorOutput Cyan "  Product Catalog API - Test Runner"
Write-ColorOutput Cyan "========================================"
Write-Host ""

# Check if pytest is installed
try {
    $null = Get-Command pytest -ErrorAction Stop
} catch {
    Write-ColorOutput Red "Error: pytest is not installed"
    Write-Host "Install with: pip install pytest pytest-cov"
    exit 1
}

# Build pytest command
$PytestCmd = "pytest tests/"

# Add verbosity
if ($Verbose) {
    $PytestCmd += " -v"
} elseif ($Quiet) {
    $PytestCmd += " -q"
}

# Add stop on fail
if ($StopOnFail) {
    $PytestCmd += " -x"
}

# Handle marker shortcuts
if ($Unit) {
    $Markers = "unit"
}
if ($Integration) {
    $Markers = "integration"
}
if ($Smoke) {
    $Markers = "smoke"
}
if ($Slow) {
    $Markers = "slow"
}

# Add markers
if ($Markers) {
    $PytestCmd += " -m $Markers"
    Write-ColorOutput Yellow "Running tests with markers: $Markers"
}

# Add keyword
if ($Keyword) {
    $PytestCmd += " -k $Keyword"
    Write-ColorOutput Yellow "Running tests matching: $Keyword"
}

# Add parallel execution
if ($Parallel -gt 0) {
    try {
        $null = Get-Command pytest-xdist -ErrorAction Stop
    } catch {
        Write-ColorOutput Yellow "Warning: pytest-xdist not installed. Installing..."
        pip install pytest-xdist
    }
    $PytestCmd += " -n $Parallel"
    Write-ColorOutput Yellow "Running tests in parallel with $Parallel workers"
}

# Add coverage
$ReportType = "term"
if ($Html) {
    $ReportType = "html"
}
if ($Xml) {
    $ReportType = "xml"
}

if (-not $NoCov) {
    $PytestCmd += " --cov=src --cov-report=$ReportType"
    if ($ReportType -eq "html") {
        $PytestCmd += " --cov-report=html"
        Write-ColorOutput Yellow "Coverage report will be generated in htmlcov/"
    } elseif ($ReportType -eq "xml") {
        $PytestCmd += " --cov-report=xml"
        Write-ColorOutput Yellow "Coverage report will be generated as coverage.xml"
    }
}

Write-Host ""

# Watch mode
if ($Watch) {
    try {
        $null = Get-Command pytest-watch -ErrorAction Stop
    } catch {
        Write-ColorOutput Yellow "Installing pytest-watch..."
        pip install pytest-watch
    }
    Write-ColorOutput Green "Starting watch mode..."
    Invoke-Expression "ptw -- $PytestCmd"
    exit 0
}

# Run tests
Write-ColorOutput Green "Running tests..."
Write-ColorOutput Cyan "Command: $PytestCmd"
Write-Host ""

$exitCode = 0
try {
    Invoke-Expression $PytestCmd
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-ColorOutput Green "========================================"
        Write-ColorOutput Green "  All tests passed! ✓"
        Write-ColorOutput Green "========================================"
    } else {
        $exitCode = 1
    }
} catch {
    $exitCode = 1
}

if ($exitCode -ne 0) {
    Write-Host ""
    Write-ColorOutput Red "========================================"
    Write-ColorOutput Red "  Tests failed! ✗"
    Write-ColorOutput Red "========================================"
}

exit $exitCode

# Made with Bob
