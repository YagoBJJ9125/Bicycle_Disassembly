@echo off
setlocal
title Officina - Avvio
cd /d "%~dp0"
if errorlevel 1 goto cartella_errore
set "OFFICINA_NODE=node.exe"
where node.exe >nul 2>&1
if errorlevel 1 (
  if exist "%ProgramFiles%\nodejs\node.exe" (
    set "OFFICINA_NODE=%ProgramFiles%\nodejs\node.exe"
  ) else (
    echo Node.js non trovato. Installa Node.js 22.13 o successivo e riprova.
    goto fine
  )
)
echo Avvio Officina...
echo Indirizzo del programma: http://127.0.0.1:5173/
echo.
"%OFFICINA_NODE%" scripts\start-local.mjs %*
if errorlevel 1 goto avvio_errore
echo.
echo Se Officina era gia avviata, apri http://127.0.0.1:5173/ nel browser.
goto fine
:cartella_errore
echo Impossibile aprire la cartella del progetto.
goto fine
:avvio_errore
echo.
echo Avvio non completato. Leggi il messaggio sopra e docs\AVVIO.md.
:fine
echo.
pause
endlocal
