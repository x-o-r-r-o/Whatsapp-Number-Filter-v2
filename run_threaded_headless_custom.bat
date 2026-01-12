@echo off
setlocal
set "PROJECT_ROOT=%~dp0"
cd /d "%PROJECT_ROOT%"

REM Activate venv
call ".venv\Scripts\activate.bat" || (
  echo [ERROR] Failed to activate venv.
  pause
  exit /b 1
)

REM Customize these paths if you want:
set "IN=data\input_numbers.txt"
set "OUT_VALID=data\valid_numbers.txt"
set "OUT_INVALID=data\invalid_numbers.txt"

REM Customize these performance settings:
set "THREADS=4"
set "CHUNK=50"

echo [INFO] Running threaded + headless with custom IO
echo   Input:          %IN%
echo   Valid output:   %OUT_VALID%
echo   Invalid output: %OUT_INVALID%
echo   Threads:        %THREADS%
echo   Chunk size:     %CHUNK%
echo.

whatsapp-filter ^
  -i "%IN%" ^
  --valid-output "%OUT_VALID%" ^
  --invalid-output "%OUT_INVALID%" ^
  --mode threaded ^
  --threads %THREADS% ^
  --chunk-size %CHUNK% ^
  --headless

pause
endlocal