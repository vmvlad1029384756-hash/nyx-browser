$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$archive = Get-ChildItem -LiteralPath $repoRoot -Filter "NYX_Browser_*_ThemeWidgets.zip" -File |
    Select-Object -First 1
if (-not $archive) { throw "Could not find the NYX desktop source archive in $repoRoot" }

$buildRoot = Join-Path $repoRoot "build\windows"
$sourceRoot = Join-Path $buildRoot "source"
$venvRoot = Join-Path $buildRoot ".venv"
$outputRoot = Join-Path $repoRoot "dist"
if (Test-Path $buildRoot) { Remove-Item -LiteralPath $buildRoot -Recurse -Force }
if (Test-Path $outputRoot) { Remove-Item -LiteralPath $outputRoot -Recurse -Force }
New-Item -ItemType Directory -Force -Path $sourceRoot, $outputRoot | Out-Null

Write-Host "[NYX] Extracting desktop source archive..."
Expand-Archive -LiteralPath $archive.FullName -DestinationPath $sourceRoot -Force

$versionFile = Join-Path $sourceRoot "VERSION.txt"
$issTarget = Join-Path $sourceRoot "setup\NYX_Browser.iss"
$issTemplate = Join-Path $repoRoot "windows-build\NYX_Browser.iss"
if (-not (Test-Path $versionFile)) { throw "VERSION.txt is missing from source archive." }
if (-not (Test-Path $issTemplate)) { throw "Installer script is missing: $issTemplate" }

$sourceVersion = (Get-Content -LiteralPath $versionFile -Raw).Trim()
$installerText = Get-Content -LiteralPath $issTemplate -Raw
if ($installerText -notmatch '#define AppVersion "([^"]+)"') {
    throw "Could not read AppVersion from the Inno Setup script."
}
$installerVersion = $Matches[1]
if ($sourceVersion -ne $installerVersion) {
    throw "Version mismatch: source archive is $sourceVersion but installer script is $installerVersion."
}
Copy-Item -LiteralPath $issTemplate -Destination $issTarget -Force

$basePython = $null
$pyLauncher = Get-Command py -ErrorAction SilentlyContinue
if ($pyLauncher) {
    $basePython = (& py -3.13 -c "import sys; print(sys.executable)" 2>$null | Select-Object -First 1)
    if ($LASTEXITCODE -ne 0) { $basePython = $null }
}
if (-not $basePython) {
    $pythonCommand = Get-Command python -ErrorAction SilentlyContinue
    if ($pythonCommand) { $basePython = $pythonCommand.Source }
}
if (-not $basePython -or -not (Test-Path $basePython)) {
    throw "Python 3.13 x64 is required to build NYX. End users do not need Python."
}
$basePython = $basePython.Trim()
& $basePython -c "import sys, struct; assert sys.version_info[:2] == (3,13), sys.version; assert struct.calcsize('P') == 8"
if ($LASTEXITCODE -ne 0) { throw "The selected Python must be version 3.13 x64." }

Write-Host "[NYX] Creating an isolated build environment..."
& $basePython -m venv $venvRoot
if ($LASTEXITCODE -ne 0) { throw "Could not create the build virtual environment." }
$python = Join-Path $venvRoot "Scripts\python.exe"

Push-Location $sourceRoot
try {
    Write-Host "[NYX] Installing build dependencies..."
    & $python -m pip install --upgrade pip
    if ($LASTEXITCODE -ne 0) { throw "pip upgrade failed." }
    & $python -m pip install --no-cache-dir -r requirements-build.txt
    if ($LASTEXITCODE -ne 0) { throw "Dependency installation failed." }

    Write-Host "[NYX] Running regression tests..."
    & $python -m unittest discover -s tests -v
    if ($LASTEXITCODE -ne 0) { throw "Regression tests failed." }

    Write-Host "[NYX] Packaging NYX Browser with PyInstaller..."
    & $python -m PyInstaller --noconfirm --clean NYX_Browser.spec
    if ($LASTEXITCODE -ne 0) { throw "PyInstaller failed." }

    $appExe = Join-Path $sourceRoot "dist\NYX Browser\NYX Browser.exe"
    if (-not (Test-Path $appExe)) { throw "PyInstaller did not produce NYX Browser.exe." }

    $isccCandidates = @(
        "C:\Program Files\Inno Setup 6\ISCC.exe",
        "C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
    )
    $iscc = $isccCandidates | Where-Object { Test-Path $_ } | Select-Object -First 1
    if (-not $iscc) {
        $isccCommand = Get-Command ISCC.exe -ErrorAction SilentlyContinue
        if ($isccCommand) { $iscc = $isccCommand.Source }
    }
    if (-not $iscc) { throw "Inno Setup 6 was not found. Install it, then run this script again." }

    New-Item -ItemType Directory -Force -Path (Join-Path $sourceRoot "installer") | Out-Null
    Write-Host "[NYX] Creating the per-user Windows installer..."
    & $iscc /Qp (Join-Path $sourceRoot "setup\NYX_Browser.iss")
    if ($LASTEXITCODE -ne 0) { throw "Inno Setup compilation failed." }

    $installerName = "NYX_Browser_" + $sourceVersion + "_Setup_x64.exe"
    $installer = Join-Path $sourceRoot ("installer\" + $installerName)
    if (-not (Test-Path $installer)) { throw "Setup.exe was not created at the expected path: $installer" }
    Copy-Item -LiteralPath $installer -Destination $outputRoot -Force
    $publishedInstaller = Join-Path $outputRoot $installerName
    $hash = (Get-FileHash -LiteralPath $publishedInstaller -Algorithm SHA256).Hash.ToLowerInvariant()
    "$hash  $installerName" | Set-Content -LiteralPath "$publishedInstaller.sha256" -Encoding ascii

    Write-Host ""
    Write-Host "[NYX] BUILD SUCCESS"
    Write-Host "[NYX] Installer: $publishedInstaller"
    Write-Host "[NYX] SHA-256:   $hash"
}
finally {
    Pop-Location
}
