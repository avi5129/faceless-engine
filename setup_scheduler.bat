@echo off
REM setup_scheduler.bat — register a Windows Task Scheduler job that runs
REM run_daily.bat N times per day. Human still publishes from publish/.
REM Run this ONCE (as admin) to create the schedule. Edit TIMES for cadence.
setlocal
cd /d %~dp0
set TASKNAME=FacelessEngineDaily
set BAT=%~dp0run_daily.bat
set COUNT=1
REM Cadence: 3 runs/day at 09:00, 13:00, 19:00 (edit to taste / N per day).
REM FIXED 2026-07-17 (autoplan decision #14): use explicit per-time tasks, NOT the
REM /RI 240 /DU 24h loop (that repeated every 4h from midnight = 6 runs/day at wrong times).
schtasks /Create /TN "%TASKNAME%"    /TR "\"%BAT%\" %COUNT%" /SC DAILY /ST 09:00 /F
schtasks /Create /TN "%TASKNAME%-2"  /TR "\"%BAT%\" %COUNT%" /SC DAILY /ST 13:00 /F
schtasks /Create /TN "%TASKNAME%-3"  /TR "\"%BAT%\" %COUNT%" /SC DAILY /ST 19:00 /F
echo Scheduler tasks registered. Verify: schtasks /Query /TN "%TASKNAME%"
endlocal
