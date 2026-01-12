@echo off
setlocal ENABLEDELAYEDEXPANSION

REM =====================================================
REM whatsapp-filter - Windows run helper (ALL VARIANTS)
REM =====================================================

set "PROJECT_ROOT=%~dp0"
cd /d "%PROJECT_ROOT%"

echo.
echo ==========================================
echo  whatsapp-filter - Run Helper (Windows)
echo ==========================================
echo Project root: %PROJECT_ROOT%
echo.

REM Activate venv
if not exist ".venv" (
    echo [ERROR] .venv not found. Run setup_windows.bat or create venv first.
    pause
    exit /b 1
)

call ".venv\Scripts\activate.bat"
if errorlevel 1 (
    echo [ERROR] Failed to activate virtual environment.
    pause
    exit /b 1
)

:main_menu
cls
echo.
echo ==========================================
echo  MAIN MENU
echo ==========================================
echo  1^) Use config.yaml (no overrides)
echo  2^) Override HEADLESS only
echo  3^) Override MODE only
echo  4^) Override MODE + HEADLESS
echo  5^) Override MODE + THREADS (+ CHUNK for threaded)
echo  6^) Override INPUT / OUTPUT paths
echo  7^) SHOW EXAMPLES (print commands only)
echo  8^) EXIT
echo.

set /p MAIN_CHOICE=Enter choice [1-8]: 

if "%MAIN_CHOICE%"=="1" goto use_config_only
if "%MAIN_CHOICE%"=="2" goto override_headless
if "%MAIN_CHOICE%"=="3" goto override_mode
if "%MAIN_CHOICE%"=="4" goto override_mode_headless
if "%MAIN_CHOICE%"=="5" goto override_mode_threads
if "%MAIN_CHOICE%"=="6" goto override_io
if "%MAIN_CHOICE%"=="7" goto show_examples
if "%MAIN_CHOICE%"=="8" goto done

echo [WARN] Invalid choice.
pause
goto main_menu

:use_config_only
echo.
echo [INFO] Running: whatsapp-filter
echo.
whatsapp-filter
pause
goto done

:override_headless
cls
echo.
echo ==========================================
echo  OVERRIDE HEADLESS
echo ==========================================
echo  1^) Headless ON   ( --headless )
echo  2^) Headless OFF  ( no flag, use config.yaml )
echo  3^) Back
echo.

set /p H_CHOICE=Enter choice [1-3]: 

if "%H_CHOICE%"=="1" (
    echo.
    echo [INFO] Running: whatsapp-filter --headless
    echo.
    whatsapp-filter --headless
    pause
    goto done
) else if "%H_CHOICE%"=="2" (
    echo.
    echo [INFO] Running: whatsapp-filter (no headless override)
    echo.
    whatsapp-filter
    pause
    goto done
) else (
    goto main_menu
)

:override_mode
cls
echo.
echo ==========================================
echo  OVERRIDE MODE ONLY
echo ==========================================
echo  1^) single
echo  2^) onedriver
echo  3^) threaded
echo  4^) Back
echo.

set /p M_CHOICE=Enter choice [1-4]: 

if "%M_CHOICE%"=="1" (
    echo.
    echo [INFO] Running: whatsapp-filter --mode single
    echo.
    whatsapp-filter --mode single
    pause
    goto done
) else if "%M_CHOICE%"=="2" (
    echo.
    echo [INFO] Running: whatsapp-filter --mode onedriver
    echo.
    whatsapp-filter --mode onedriver
    pause
    goto done
) else if "%M_CHOICE%"=="3" (
    echo.
    echo [INFO] Running: whatsapp-filter --mode threaded
    echo [NOTE] For best results, run single mode once first to create a logged-in profile.
    echo.
    whatsapp-filter --mode threaded
    pause
    goto done
) else (
    goto main_menu
)

:override_mode_headless
cls
echo.
echo ==========================================
echo  OVERRIDE MODE + HEADLESS
echo ==========================================
echo  1^) single, headless
echo  2^) onedriver, headless
echo  3^) threaded, headless
echo  4^) Back
echo.

set /p MH_CHOICE=Enter choice [1-4]: 

if "%MH_CHOICE%"=="1" (
    echo.
    echo [INFO] Running: whatsapp-filter --mode single --headless
    echo.
    whatsapp-filter --mode single --headless
    pause
    goto done
) else if "%MH_CHOICE%"=="2" (
    echo.
    echo [INFO] Running: whatsapp-filter --mode onedriver --headless
    echo.
    whatsapp-filter --mode onedriver --headless
    pause
    goto done
) else if "%MH_CHOICE%"=="3" (
    echo.
    echo [INFO] Running: whatsapp-filter --mode threaded --headless
    echo [NOTE] For best results, run single mode once first to create a logged-in profile.
    echo.
    whatsapp-filter --mode threaded --headless
    pause
    goto done
) else (
    goto main_menu
)

:override_mode_threads
cls
echo.
echo ==========================================
echo  OVERRIDE MODE + THREADS (+ CHUNK)
echo ==========================================
echo  1^) onedriver, threads=4
echo  2^) onedriver, custom threads
echo  3^) threaded, threads=4, chunk=50
echo  4^) threaded, custom threads + chunk
echo  5^) Back
echo.

set /p MT_CHOICE=Enter choice [1-5]: 

if "%MT_CHOICE%"=="1" (
    echo.
    echo [INFO] Running: whatsapp-filter --mode onedriver --threads 4
    echo.
    whatsapp-filter --mode onedriver --threads 4
    pause
    goto done
) else if "%MT_CHOICE%"=="2" (
    set /p T=Enter threads (e.g. 4): 
    echo.
    echo [INFO] Running: whatsapp-filter --mode onedriver --threads %T%
    echo.
    whatsapp-filter --mode onedriver --threads %T%
    pause
    goto done
) else if "%MT_CHOICE%"=="3" (
    echo.
    echo [INFO] Running: whatsapp-filter --mode threaded --threads 4 --chunk-size 50
    echo [NOTE] For best results, run single mode once first to create a logged-in profile.
    echo.
    whatsapp-filter --mode threaded --threads 4 --chunk-size 50
    pause
    goto done
) else if "%MT_CHOICE%"=="4" (
    set /p T=Enter threads (e.g. 4): 
    set /p C=Enter chunk size (e.g. 50): 
    echo.
    echo [INFO] Running: whatsapp-filter --mode threaded --threads %T% --chunk-size %C%
    echo [NOTE] For best results, run single mode once first to create a logged-in profile.
    echo.
    whatsapp-filter --mode threaded --threads %T% --chunk-size %C%
    pause
    goto done
) else (
    goto main_menu
)

:override_io
cls
echo.
echo ==========================================
echo  OVERRIDE INPUT / OUTPUT
echo ==========================================
set /p IN_PATH=Input file path [default: data\input_numbers.txt]: 
if "%IN_PATH%"=="" set "IN_PATH=data\input_numbers.txt"

set /p OUT_VALID=Valid output path [default: data\valid_numbers.txt]: 
if "%OUT_VALID%"=="" set "OUT_VALID=data\valid_numbers.txt"

set /p OUT_INVALID=Invalid output path [default: data\invalid_numbers.txt]: 
if "%OUT_INVALID%"=="" set "OUT_INVALID=data\invalid_numbers.txt"

echo.
echo [INFO] You can also add headless/mode overrides.
echo.

set /p EXTRA=Extra options (e.g. --headless --mode threaded --threads 4 --chunk-size 50): 

echo.
echo [INFO] Running:
echo   whatsapp-filter -i "%IN_PATH%" --valid-output "%OUT_VALID%" --invalid-output "%OUT_INVALID%" %EXTRA%
echo.

whatsapp-filter -i "%IN_PATH%" --valid-output "%OUT_VALID%" --invalid-output "%OUT_INVALID%" %EXTRA%
pause
goto done

:show_examples
cls
echo.
echo ==========================================
echo  COMMAND EXAMPLES
echo ==========================================
echo.
echo Normal:
echo   whatsapp-filter
echo.
echo Headless:
echo   whatsapp-filter --headless
echo.
echo Modes:
echo   whatsapp-filter --mode single
echo   whatsapp-filter --mode onedriver
echo   whatsapp-filter --mode threaded
echo.
echo Modes + threads/chunk:
echo   whatsapp-filter --mode onedriver --threads 4
echo   whatsapp-filter --mode threaded --threads 4 --chunk-size 50
echo.
echo Headless + modes:
echo   whatsapp-filter --mode single --headless
echo   whatsapp-filter --mode onedriver --threads 4 --headless
echo   whatsapp-filter --mode threaded --threads 4 --chunk-size 50 --headless
echo.
echo IO overrides:
echo   whatsapp-filter -i data\\my_numbers.txt --valid-output data\\my_valid.txt --invalid-output data\\my_invalid.txt
echo   whatsapp-filter -i data\\my_numbers.txt --valid-output data\\my_valid.txt --invalid-output data\\my_invalid.txt --mode threaded --threads 4 --chunk-size 50 --headless
echo.
pause
goto main_menu

:done
echo.
echo [INFO] Exiting run helper.
endlocal
exit /b 0