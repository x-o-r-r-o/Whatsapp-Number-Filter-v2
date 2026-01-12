@echo off
setlocal
set "PROJECT_ROOT=%~dp0"
cd /d "%PROJECT_ROOT%"

call ".venv\Scripts\activate.bat" || (
  echo [ERROR] Failed to activate venv.
  pause
  exit /b 1
)

echo [INFO] Running single mode (visible browser, config IO)
echo.

whatsapp-filter --mode single

pause
endlocal