@echo off
REM Local Windows nightly wrapper. The pipeline itself lives in scheduler.py
REM so the local job and the GitHub Actions workflow run the same steps.
REM
REM To schedule this in Windows Task Scheduler:
REM   schtasks /create /tn "PWIN Nightly" /tr "C:\Users\User\Documents\GitHub\PWIN\pwin-competitive-intel\agent\nightly.bat" /sc daily /st 02:00

cd /d "C:\Users\User\Documents\GitHub\PWIN\pwin-competitive-intel"
echo [%date% %time%] === Nightly pipeline start === >> "agent\ingest-scheduled.log"
".venv\Scripts\python.exe" agent\scheduler.py >> "agent\ingest-scheduled.log" 2>&1
echo [%date% %time%] === Nightly pipeline done === >> "agent\ingest-scheduled.log"
