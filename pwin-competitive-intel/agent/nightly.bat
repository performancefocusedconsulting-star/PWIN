@echo off
cd /d "C:\Users\User\Documents\GitHub\PWIN\pwin-competitive-intel"
echo [%date% %time%] === Nightly ingest start === >> "C:\Users\User\Documents\GitHub\PWIN\pwin-competitive-intel\agent\ingest-scheduled.log"
python agent\ingest.py >> "C:\Users\User\Documents\GitHub\PWIN\pwin-competitive-intel\agent\ingest-scheduled.log" 2>&1
echo [%date% %time%] === Ingest done. Starting CH enrichment === >> "C:\Users\User\Documents\GitHub\PWIN\pwin-competitive-intel\agent\ingest-scheduled.log"
python agent\enrich-ch.py --limit 200 >> "C:\Users\User\Documents\GitHub\PWIN\pwin-competitive-intel\agent\ingest-scheduled.log" 2>&1
echo [%date% %time%] === Nightly run complete === >> "C:\Users\User\Documents\GitHub\PWIN\pwin-competitive-intel\agent\ingest-scheduled.log"
