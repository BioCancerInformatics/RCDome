@echo off
D:
cd "D:\Pré-artigo 5-optosis model\Cellular_Spatial_RCD_manuscript\RCDome_manuscript\extraction code snippets"
set NCBI_KEY=YOUR_NCBI_KEY
set DEEPSEEK_KEY=YOUR_DEEPSEEK_KEY
echo Resuming Phase 2A validation...
python channel_c_evidence_tier.py
pause
