# setup.ps1 — Instalador de historias-ig-skill (Windows / PowerShell)
# Uso:  .\setup.ps1

$ErrorActionPreference = "Stop"
$PROJ = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host ""
Write-Host "  Instalando historias-ig-skill..."
Write-Host ""

# 1) Python 3.10+
$py = $null
foreach ($c in @("python", "python3", "py")) {
    try {
        if ((& $c -c "import sys; print(sys.version_info >= (3,10))" 2>$null) -eq "True") {
            $py = $c; break
        }
    } catch {}
}
if (-not $py) {
    Write-Host "  [x] Necesitas Python 3.10+ . Descargalo en https://python.org (marca 'Add to PATH')."
    exit 1
}
Write-Host "  [ok] Python detectado ($py)"

# 2) Dependencias
& $py -m pip install --quiet "pillow>=10.0.0"
Write-Host "  [ok] Dependencias instaladas (Pillow)"

# 3) Fuentes (Space Grotesk)
$fonts = Join-Path $PROJ "fonts"
New-Item -ItemType Directory -Force -Path $fonts | Out-Null
$descargas = @{
    (Join-Path $fonts "SpaceGrotesk-Variable.ttf") = "https://fonts.gstatic.com/s/spacegrotesk/v22/V8mQoQDjQSkFtoMM3T6r8E7mF71Q-gOoraIAEj7oUUsj.ttf"
    (Join-Path $fonts "SpaceGrotesk-Bold.ttf")     = "https://fonts.gstatic.com/s/spacegrotesk/v22/V8mQoQDjQSkFtoMM3T6r8E7mF71Q-gOoraIAEj4PVksj.ttf"
}
foreach ($dest in $descargas.Keys) {
    if (-not (Test-Path $dest)) {
        Invoke-WebRequest -Uri $descargas[$dest] -OutFile $dest -UseBasicParsing
    }
}
Write-Host "  [ok] Fuentes listas"

# 4) Instalar el comando /historias-ig
$dest = Join-Path $env:USERPROFILE ".claude\commands\historias-ig.md"
New-Item -ItemType Directory -Force -Path (Split-Path $dest) | Out-Null
$skill = Get-Content (Join-Path $PROJ "skill\historias-ig.md") -Raw -Encoding UTF8
$skill = $skill.Replace("{{PROJ_DIR}}", $PROJ.Replace("\", "/"))
Set-Content -Path $dest -Value $skill -Encoding UTF8 -NoNewline
Write-Host "  [ok] Comando instalado en $dest"

# 5) .env
$env_file = Join-Path $PROJ ".env"
if (-not (Test-Path $env_file)) {
    Copy-Item (Join-Path $PROJ ".env.example") $env_file
    Write-Host "  [ok] .env creado (agrega tus claves)"
}

Write-Host ""
Write-Host "  Listo. Cierra y vuelve a abrir Claude Code, luego escribe: /historias-ig"
Write-Host ""
