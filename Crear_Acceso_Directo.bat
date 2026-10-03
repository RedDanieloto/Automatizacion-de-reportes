emp@echo off
chcp 65001 > nul
echo Creando acceso directo en el Escritorio...
powershell -ExecutionPolicy Bypass -File "%~dp0crear_acceso_directo.ps1"
echo.
pause
