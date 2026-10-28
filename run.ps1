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

$CodexPython = Join-Path $env:USERPROFILE ".cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
if (Test-Path $CodexPython) {
    $PythonCandidates += $CodexPython
}

if ($PythonCandidates.Count -eq 0) {
    throw "No Python executable found. Install Python or run this inside Codex."
}

if ($args.Count -gt 0 -and $args[0] -eq "chart") {
    $ChartScript = Join-Path $ProjectRoot "tools\create_category_chart.py"
    & $PythonCandidates[0] $ChartScript
    exit $LASTEXITCODE
}

if ($args.Count -gt 0 -and $args[0] -eq "ui") {
    $DashboardScript = Join-Path $ProjectRoot "tools\serve_dashboard.py"
    $RemainingArgs = @()
    if ($args.Count -gt 1) {
        $RemainingArgs = $args[1..($args.Count - 1)]
    }
    & $PythonCandidates[0] $DashboardScript @RemainingArgs
    exit $LASTEXITCODE
}

if ($args.Count -gt 0 -and $args[0] -eq "challenge") {
    $ChallengeScript = Join-Path $ProjectRoot "tools\run_challenge_set.py"
    & $PythonCandidates[0] $ChallengeScript
    exit $LASTEXITCODE
}

if ($args.Count -gt 0 -and $args[0] -eq "test") {
    $env:PYTHONPATH = Join-Path $ProjectRoot "src"
    & $PythonCandidates[0] -m unittest discover -s (Join-Path $ProjectRoot "tests") -v
    exit $LASTEXITCODE
}

if ($args.Count -gt 0 -and $args[0] -eq "release-check") {
    $ReleaseScript = Join-Path $ProjectRoot "tools\validate_release.py"
    & $PythonCandidates[0] $ReleaseScript
    exit $LASTEXITCODE
}

& $PythonCandidates[0] $EntryPoint @args
