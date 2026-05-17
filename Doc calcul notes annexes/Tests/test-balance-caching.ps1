# Script PowerShell pour tester la mise en cache des balances
# Test rapide de la fonctionnalité de cache

Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "TEST DE MISE EN CACHE DES BALANCES" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host ""

# Vérifier que Python est installé
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python détecté: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Python n'est pas installé ou n'est pas dans le PATH" -ForegroundColor Red
    exit 1
}

# Vérifier que le fichier de test existe
$testFile = "test_balance_caching.py"
if (-not (Test-Path $testFile)) {
    Write-Host "✗ Fichier de test introuvable: $testFile" -ForegroundColor Red
    exit 1
}

Write-Host "✓ Fichier de test trouvé: $testFile" -ForegroundColor Green
Write-Host ""

# Exécuter les tests
Write-Host "Exécution des tests..." -ForegroundColor Yellow
Write-Host ""

python $testFile

$exitCode = $LASTEXITCODE

Write-Host ""
Write-Host "=" * 80 -ForegroundColor Cyan

if ($exitCode -eq 0) {
    Write-Host "✓ TOUS LES TESTS ONT RÉUSSI" -ForegroundColor Green
} else {
    Write-Host "✗ CERTAINS TESTS ONT ÉCHOUÉ" -ForegroundColor Red
}

Write-Host "=" * 80 -ForegroundColor Cyan

exit $exitCode
