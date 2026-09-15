@echo off
D:
cd "D:\Pré-artigo 5-optosis model\Cellular_Spatial_RCD_manuscript\RCDome_manuscript\extraction code snippets"
set NCBI_KEY=***REMOVED***
set DEEPSEEK_KEY=***REMOVED***
echo Resuming Phase 2A validation...
python channel_c_evidence_tier.py
pause
