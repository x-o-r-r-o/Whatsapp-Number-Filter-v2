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

echo [INFO] Running onedriver mode with %THREADS% threads (visible browser)
echo.

whatsapp-filter --mode onedriver --threads %THREADS%

pause
endlocal