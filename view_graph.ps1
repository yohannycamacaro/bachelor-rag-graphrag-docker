$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$Exporter = Join-Path $ProjectRoot "tools\export_graph_viewer.py"

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

& $PythonCandidates[0] $Exporter

