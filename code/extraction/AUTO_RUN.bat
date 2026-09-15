@echo off
D:
cd "D:\Pré-artigo 5-optosis model\Cellular_Spatial_RCD_manuscript\RCDome_manuscript\extraction code snippets"
set NCBI_KEY=YOUR_NCBI_KEY
set DEEPSEEK_KEY=YOUR_DEEPSEEK_KEY

echo ============================================================
echo RCDome Phase 2A - AUTONOMOUS VALIDATION ENGINE
echo ============================================================
echo Watchdog active. Pipeline will auto-restart on any failure.
echo Keep this window OPEN. Minimize, do NOT close.
echo ============================================================
echo.

:loop
echo [%date% %time%] Launching pipeline...
python channel_c_evidence_tier.py
echo.
echo [%date% %time%] Pipeline exited. Auto-restart in 30 seconds...
timeout /t 30 /nobreak >nul
goto loop
