@echo off
cd /d "%~dp0"
node scripts\start-local.mjs
if errorlevel 1 (
  echo.
  echo Avvio non completato. Leggi il messaggio sopra e docs\AVVIO.md.
  pause
)
