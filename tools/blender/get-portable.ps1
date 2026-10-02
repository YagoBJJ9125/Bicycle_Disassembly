param([switch]$Direct)
$ErrorActionPreference = 'Stop'
$taskProjectRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
$taskToolsRoot = Join-Path $taskProjectRoot '.tools'
$taskArchive = Join-Path $taskToolsRoot 'blender-4.5.14-windows-x64.zip'
$taskExecutable = Join-Path $taskToolsRoot 'blender-4.5.14-windows-x64/blender.exe'
$taskExpectedHash = 'b9533d2397ac1984db4466fb23a7a4649391cca93f6e84209f9bcc60d071c8b9'
New-Item -ItemType Directory -Force -Path $taskToolsRoot | Out-Null
$taskValidArchive = (Test-Path -LiteralPath $taskArchive) -and ((Get-FileHash -LiteralPath $taskArchive -Algorithm SHA256).Hash -eq $taskExpectedHash)
if (-not $taskValidArchive) {
    $taskCurlArgs = @('--fail', '--location', '--connect-timeout', '30', '--retry', '2', '--output', $taskArchive)
    if ($Direct) { $taskCurlArgs += @('--noproxy', '*') }
    $taskCurlArgs += 'https://download.blender.org/release/Blender4.5/blender-4.5.14-windows-x64.zip'
    & curl.exe @taskCurlArgs
    if ($LASTEXITCODE -ne 0) { throw 'Download Blender non completato.' }
}
if ((Get-FileHash -LiteralPath $taskArchive -Algorithm SHA256).Hash -ne $taskExpectedHash) {
    throw 'SHA-256 non corrispondente: il pacchetto non verra eseguito.'
}
if (-not (Test-Path -LiteralPath $taskExecutable)) {
    Expand-Archive -LiteralPath $taskArchive -DestinationPath $taskToolsRoot
}
& $taskExecutable --version
if ($LASTEXITCODE -ne 0) { throw 'Blender portabile non avviabile.' }
Write-Output "Blender portabile: $taskExecutable"
