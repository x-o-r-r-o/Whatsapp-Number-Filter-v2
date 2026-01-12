@echo off
setlocal
set "PROJECT_ROOT=%~dp0"
cd /d "%PROJECT_ROOT%"

call ".venv\Scripts\activate.bat" || (
  echo [ERROR] Failed to activate venv.
  pause
  exit /b 1
)

set "THREADS=4"
set "CHUNK=50"

echo [INFO] Running threaded + headless (default IO)
echo   Threads:    %THREADS%
echo   Chunk size: %CHUNK%
echo.

whatsapp-filter --mode threaded --threads %THREADS% --chunk-size %CHUNK% --headless

pause
endlocal