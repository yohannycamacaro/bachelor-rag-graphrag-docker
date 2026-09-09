$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$EntryPoint = Join-Path $ProjectRoot "run_compare.py"

$PythonCandidates = @()

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

& $PythonCandidates[0] $EntryPoint @args
