@echo off
set NCBI_KEY=***REMOVED***
set DEEPSEEK_KEY=***REMOVED***
echo Starting RCDome Phase 2 Validation Pipeline...
python3 -u channel_c_evidence_tier.py > validation_log.txt 2>&1
if %ERRORLEVEL% NEQ 0 (
    py -3 -u channel_c_evidence_tier.py > validation_log.txt 2>&1
)
echo Done. Check validation_log.txt
pause
