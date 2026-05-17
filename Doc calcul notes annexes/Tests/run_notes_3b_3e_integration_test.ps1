#!/usr/bin/env pwsh
# -*- coding: utf-8 -*-

<#
.SYNOPSIS
    Run integration tests for Notes 3B-3E

.DESCRIPTION
    This script executes the integration test suite for Notes 3B (Immobilisations Corporelles),
    3C (Immobilisations Financières), 3D (Charges Immobilisées), and 3E (Écarts de Conversion Actif).
    
    The tests validate:
    - Individual note calculation workflows
    - Inter-note coherence (total immobilizations, dotations)
    - Temporal continuity across fiscal years
    - Comprehensive integration of all notes

.PARAMETER TestName
    Optional: Specific test to run. If not provided, runs all tests.
    Examples:
    - "test_note_3b_complete_workflow"
    - "test_inter_note_total_immobilizations"
    - "test_all_notes_3b_3e_comprehensive"

.PARAMETER Verbose
    Show detailed test output

.PARAMETER Coverage
    Generate code coverage report

.EXAMPLE
    .\run_notes_3b_3e_integration_test.ps1
    Run all integration tests

.EXAMPLE
    .\run_notes_3b_3e_integration_test.ps1 -TestName "test_note_3b_complete_workflow"
    Run specific test

.EXAMPLE
    .\run_notes_3b_3e_integration_test.ps1 -Verbose
    Run all tests with detailed output

.EXAMPLE
    .\run_notes_3b_3e_integration_test.ps1 -Coverage
    Run all tests with coverage report

.NOTES
    Author: Système de calcul automatique des notes annexes SYSCOHADA
    Date: 25 Avril 2026
#>

param(
    [Parameter(Mandatory=$false)]
    [string]$TestName,
    
    [Parameter(Mandatory=$false)]
    [switch]$Verbose,
    
    [Parameter(Mandatory=$false)]
    [switch]$Coverage
)

# Set error action preference
$ErrorActionPreference = "Stop"

# Get script directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$TestFile = Join-Path $ScriptDir "test_notes_3b_3e_integration.py"

# Display header
Write-Host ""
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "  Integration Tests for Notes 3B-3E" -ForegroundColor Cyan
Write-Host "  SYSCOHADA Annexes Calculation System" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

# Check if test file exists
if (-not (Test-Path $TestFile)) {
    Write-Host "ERROR: Test file not found: $TestFile" -ForegroundColor Red
    exit 1
}

# Check if pytest is installed
try {
    $pytestVersion = python -m pytest --version 2>&1
    Write-Host "Using: $pytestVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: pytest is not installed" -ForegroundColor Red
    Write-Host "Install with: pip install pytest" -ForegroundColor Yellow
    exit 1
}

# Build pytest command
$pytestArgs = @($TestFile)

# Add specific test if provided
if ($TestName) {
    $pytestArgs += "::TestNotes3B3EIntegration::$TestName"
    Write-Host "Running specific test: $TestName" -ForegroundColor Yellow
    Write-Host ""
}

# Add verbose flag
if ($Verbose) {
    $pytestArgs += "-v"
    $pytestArgs += "-s"
} else {
    $pytestArgs += "-v"
}

# Add coverage if requested
if ($Coverage) {
    $ScriptsDir = Join-Path (Split-Path -Parent $ScriptDir) "Scripts"
    $pytestArgs += "--cov=$ScriptsDir"
    $pytestArgs += "--cov-report=html"
    $pytestArgs += "--cov-report=term"
    Write-Host "Coverage report will be generated" -ForegroundColor Yellow
    Write-Host ""
}

# Display command
Write-Host "Executing: python -m pytest $($pytestArgs -join ' ')" -ForegroundColor Cyan
Write-Host ""

# Run tests
try {
    python -m pytest @pytestArgs
    $exitCode = $LASTEXITCODE
    
    Write-Host ""
    if ($exitCode -eq 0) {
        Write-Host "======================================================================" -ForegroundColor Green
        Write-Host "  ALL TESTS PASSED ✓" -ForegroundColor Green
        Write-Host "======================================================================" -ForegroundColor Green
        
        if ($Coverage) {
            $CoverageDir = Join-Path $ScriptDir "htmlcov"
            if (Test-Path $CoverageDir) {
                Write-Host ""
                Write-Host "Coverage report generated: $CoverageDir\index.html" -ForegroundColor Cyan
            }
        }
    } else {
        Write-Host "======================================================================" -ForegroundColor Red
        Write-Host "  TESTS FAILED ✗" -ForegroundColor Red
        Write-Host "======================================================================" -ForegroundColor Red
    }
    Write-Host ""
    
    exit $exitCode
    
} catch {
    Write-Host ""
    Write-Host "ERROR: Failed to run tests" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    exit 1
}
