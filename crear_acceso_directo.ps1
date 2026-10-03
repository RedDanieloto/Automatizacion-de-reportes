$DesktopPath = [System.Environment]::GetFolderPath([System.Environment+SpecialFolder]::Desktop)
if (-not $DesktopPath -or -not (Test-Path $DesktopPath)) {
    $DesktopPath = "$env:USERPROFILE\Desktop"
}

$TargetDirectory = "$PSScriptRoot\dist\ReportesDowntime"
$TargetExe = "$TargetDirectory\ReportesDowntime.exe"

if (-not (Test-Path $TargetExe)) {
    Write-Host "No se encontró el ejecutable en: $TargetExe" -ForegroundColor Red
    exit 1
}

$ShortcutPath = Join-Path $DesktopPath "Reportes Downtime.lnk"

$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = $TargetExe
$Shortcut.WorkingDirectory = $TargetDirectory
$Shortcut.Description = "Acceso directo a Automatización de Reportes Downtime"
$Shortcut.Save()

Write-Host "¡Acceso directo creado exitosamente en el Escritorio!" -ForegroundColor Green
Write-Host "Ubicación: $ShortcutPath" -ForegroundColor Cyan
