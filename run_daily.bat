@echo off
REM run_daily.bat — produce N faceless videos via engine_pro.py.
REM Human publishes from publish/ afterward (no auto-post, per plan).
REM Edit COUNT below or pass via config [engine] videos_per_run.
setlocal
cd /d %~dp0
set PY=C:\Users\Avishkar\AppData\Local\Programs\Python\Python312\python.exe
set COUNT=%1
if "%COUNT%"=="" set COUNT=1
echo [%date% %time%] engine_pro run count=%COUNT% >> work\scheduler.log
"%PY%" engine_pro.py --count %COUNT% >> work\scheduler.log 2>&1
echo [%date% %time%] done (exit %errorlevel%) >> work\scheduler.log
endlocal
