# PowerShell script to run Note 3A integration test
# This script runs the integration test for Note 3A calculation

Write-Host "================================" -ForegroundColor Cyan
Write-Host "Note 3A Integration Test Runner" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Check if pytest is installed
Write-Host "Checking dependencies..." -ForegroundColor Yellow
$pytestCheck = python -m pytest --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ pytest not found. Installing..." -ForegroundColor Red
    pip install pytest
}

# Check if beautifulsoup4 is installed
$bs4Check = python -c "import bs4" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ beautifulsoup4 not found. Installing..." -ForegroundColor Red
    pip install beautifulsoup4
}

Write-Host "✓ Dependencies OK" -ForegroundColor Green
Write-Host ""

# Run the test
Write-Host "Running integration test..." -ForegroundColor Yellow
Write-Host ""

python -m pytest test_note_3a_integration.py -v --tb=short

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "================================" -ForegroundColor Green
    Write-Host "✓ ALL TESTS PASSED" -ForegroundColor Green
    Write-Host "================================" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "================================" -ForegroundColor Red
    Write-Host "✗ SOME TESTS FAILED" -ForegroundColor Red
    Write-Host "================================" -ForegroundColor Red
}
