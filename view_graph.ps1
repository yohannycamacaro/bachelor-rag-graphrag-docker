$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$Exporter = Join-Path $ProjectRoot "tools\export_graph_viewer.py"

$PythonCandidates = @()

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

& $PythonExecutable @PythonPrefixArgs $Exporter

