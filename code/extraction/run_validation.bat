@echo off
REM Keys are NOT stored here — set them in your environment or .Renviron before running.
set NCBI_KEY=
set DEEPSEEK_KEY=
echo Starting RCDome Phase 2 Validation Pipeline...
python3 -u channel_c_evidence_tier.py > validation_log.txt 2>&1
if %ERRORLEVEL% NEQ 0 (
    py -3 -u channel_c_evidence_tier.py > validation_log.txt 2>&1
)
echo Done. Check validation_log.txt
pause
