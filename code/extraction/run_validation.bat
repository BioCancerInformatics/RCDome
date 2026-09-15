@echo off
set NCBI_KEY=3bff5d2e2fd0ed2346c11ffc15ab3b512109
set DEEPSEEK_KEY=sk-fdc01745edbd474aa19606d22d600afb
echo Starting RCDome Phase 2 Validation Pipeline...
python3 -u channel_c_evidence_tier.py > validation_log.txt 2>&1
if %ERRORLEVEL% NEQ 0 (
    py -3 -u channel_c_evidence_tier.py > validation_log.txt 2>&1
)
echo Done. Check validation_log.txt
pause
