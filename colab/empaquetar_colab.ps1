param(
    [string]$Salida
)

$ErrorActionPreference = 'Stop'

$proyecto = Split-Path -Parent $PSScriptRoot
$version = 'v10.3.10'

if (-not $Salida) {
    $escritorio = [Environment]::GetFolderPath('Desktop')
    $Salida = Join-Path $escritorio ("FinovaTech_" + $version + "_Colab.zip")
}

$padre = Split-Path -Parent $Salida
if (-not (Test-Path -LiteralPath $padre)) {
    throw "No existe la carpeta de destino: $padre"
}

$temporal = Join-Path $env:TEMP 'finovatech_colab_stage'
$raiz = Join-Path $temporal ("FinovaTech_" + $version)

if (Test-Path -LiteralPath $temporal) {
    Remove-Item -LiteralPath $temporal -Recurse -Force
}
New-Item -ItemType Directory -Path $raiz -Force | Out-Null

$excluir = @(
    '.git', '.venv', '.venvpy', '.pytest_cache', '.agents', '.vscode',
    '__pycache__', 'data', '.env', '.env.bak'
)

$elementos = Get-ChildItem -LiteralPath $proyecto -Force | Where-Object {
    ($excluir -notcontains $_.Name) -and ($_.Name -notlike 'FinovaTech_*_Colab.zip')
}

foreach ($elemento in $elementos) {
    if ($elemento.PSIsContainer) {
        $archivos = Get-ChildItem -LiteralPath $elemento.FullName -Recurse -Force -File | Where-Object {
            ($_.Extension -notin @('.pyc', '.pyo')) -and
            ($_.FullName -notmatch '\\__pycache__(\\|$)')
        }
        foreach ($archivo in $archivos) {
            $relativo = $archivo.FullName.Substring($proyecto.Length + 1)
            $destino = Join-Path $raiz $relativo
            New-Item -ItemType Directory -Path (Split-Path -Parent $destino) -Force | Out-Null
            Copy-Item -LiteralPath $archivo.FullName -Destination $destino -Force
        }
    }
    else {
        Copy-Item -LiteralPath $elemento.FullName -Destination (Join-Path $raiz $elemento.Name) -Force
    }
}

if (Test-Path -LiteralPath $Salida) {
    Remove-Item -LiteralPath $Salida -Force
}
Compress-Archive -Path $raiz -DestinationPath $Salida -CompressionLevel Optimal
Remove-Item -LiteralPath $temporal -Recurse -Force

Write-Host "ZIP listo: $Salida"
Write-Host "Sube el ZIP al notebook de Colab cuando lo pida."
