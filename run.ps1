$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$EntryPoint = Join-Path $ProjectRoot "run_compare.py"

$PythonCandidates = @()

$VirtualEnvPython = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
if (Test-Path $VirtualEnvPython) {
    $PythonCandidates += $VirtualEnvPython
}

$PythonCommand = Get-Command python -ErrorAction SilentlyContinue
if ($PythonCommand) {
    $PythonCandidates += $PythonCommand.Source
}

$PyLauncher = Get-Command py -ErrorAction SilentlyContinue
if ($PyLauncher) {
    $PythonCandidates += $PyLauncher.Source
}

if ($PythonCandidates.Count -eq 0) {
    throw "No Python executable found. Install Python 3 or create a local .venv."
}

$PythonExecutable = $PythonCandidates[0]
$PythonPrefixArgs = @()
if ([System.IO.Path]::GetFileName($PythonExecutable) -ieq "py.exe") {
    $PythonPrefixArgs = @("-3")
}

if ($args.Count -gt 0 -and $args[0] -eq "chart") {
    $ChartScript = Join-Path $ProjectRoot "tools\create_category_chart.py"
    & $PythonExecutable @PythonPrefixArgs $ChartScript
    exit $LASTEXITCODE
}

if ($args.Count -gt 0 -and $args[0] -eq "ui") {
    $DashboardScript = Join-Path $ProjectRoot "tools\serve_dashboard.py"
    $RemainingArgs = @()
    if ($args.Count -gt 1) {
        $RemainingArgs = $args[1..($args.Count - 1)]
    }
    & $PythonExecutable @PythonPrefixArgs $DashboardScript @RemainingArgs
    exit $LASTEXITCODE
}

if ($args.Count -gt 0 -and $args[0] -eq "challenge") {
    $ChallengeScript = Join-Path $ProjectRoot "tools\run_challenge_set.py"
    & $PythonExecutable @PythonPrefixArgs $ChallengeScript
    exit $LASTEXITCODE
}

if ($args.Count -gt 0 -and $args[0] -eq "test") {
    $env:PYTHONPATH = Join-Path $ProjectRoot "src"
    & $PythonExecutable @PythonPrefixArgs -m unittest discover -s (Join-Path $ProjectRoot "tests") -v
    exit $LASTEXITCODE
}

if ($args.Count -gt 0 -and $args[0] -eq "release-check") {
    $ReleaseScript = Join-Path $ProjectRoot "tools\validate_release.py"
    & $PythonExecutable @PythonPrefixArgs $ReleaseScript
    exit $LASTEXITCODE
}

& $PythonExecutable @PythonPrefixArgs $EntryPoint @args
