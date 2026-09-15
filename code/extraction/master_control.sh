#!/bin/bash
# master_control.sh — bring ALL jobs to a known-good state.
# Kills every stray process, then starts EXACTLY ONE Phase 3B P1 and ONE Phase 2B RAG.
# Resume mode (does NOT wipe progress). Use this from now on — no more ad-hoc kill/start.

echo "=== 1. KILLING ALL STRAY PROCESSES ==="
pkill -9 -f phase3b_p1 2>/dev/null
pkill -9 -f channel_c_deep_xml_rag 2>/dev/null
pkill -9 -f complete_recovery 2>/dev/null
sleep 2

echo "=== 2. STARTING PHASE 3B P1 (resume) ==="
cd "$HOME/students/aluno0549-6/RCDome/extraction code snippets"
export ELICIT_API_KEY=$(grep ELICIT_API_KEY "$HOME/students/aluno0549-6/RCDome/extraction code snippets/.env" | cut -d= -f2)
nohup python3 -u phase3b_p1.py >> phase3b_p1.log 2>&1 &
echo "  P1 PID: $!"

echo "=== 3. STARTING PHASE 2B RAG (resume) ==="
cd "$HOME/students/aluno0549-6/RCDome/extraction code snippets/phase2b_rag"
export DEEPSEEK_KEY=$(grep DEEPSEEK_KEY "$HOME/students/aluno0549-6/RCDome/extraction code snippets/.env" | cut -d= -f2)
nohup python3 -u channel_c_deep_xml_rag.py >> phase2b_v011.log 2>&1 &
echo "  RAG PID: $!"

sleep 3
echo "=== 4. CURRENT STATE ==="
ps aux | grep -E "phase3b_p1|channel_c_deep_xml_rag" | grep -v grep
