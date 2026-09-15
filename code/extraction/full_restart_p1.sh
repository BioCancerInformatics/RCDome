#!/bin/bash
# full_restart_p1.sh — kill runner, clear ALL progress, set key, restart from scratch
pkill -9 -f phase3b_p1
sleep 2
rm -f "$HOME/students/aluno0549-6/RCDome/extraction code snippets/phase3b_p1_output/phase3b_p1_progress.json"
rm -f "$HOME/students/aluno0549-6/RCDome/extraction code snippets/phase3b_p1_output/"*.csv
cd "$HOME/students/aluno0549-6/RCDome/extraction code snippets"
export ELICIT_API_KEY=$(grep ELICIT_API_KEY "$HOME/students/aluno0549-6/RCDome/extraction code snippets/.env" | cut -d= -f2)
nohup python3 -u phase3b_p1.py >> phase3b_p1.log 2>&1 &
echo "Started PID: $! (full restart, all 20 forms)"
