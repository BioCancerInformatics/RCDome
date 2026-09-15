#!/bin/bash
# restart_p3.sh — kill any P3 runner, set key, start exactly one Phase 3B P3 runner
pkill -9 -f phase3b_p3
sleep 2
cd "$HOME/students/aluno0549-6/RCDome/extraction code snippets"
export ELICIT_API_KEY=$(grep ELICIT_API_KEY "$HOME/students/aluno0549-6/RCDome/extraction code snippets/.env" | cut -d= -f2)
nohup python3 -u phase3b_p3.py >> phase3b_p3.log 2>&1 &
echo "Started PID: $!"
