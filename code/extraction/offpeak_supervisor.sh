#!/bin/bash
# offpeak_supervisor.sh — run deepseek_cot_v11_full.py ONLY during DeepSeek off-peak (half-price) hours.
# Peak (full price) = Mon-Fri 01:00-04:00 UTC and 06:00-10:00 UTC. Weekends are fully off-peak.
# Sends an email alert on every pause/resume (via notify_email.py).
cd "$HOME/students/aluno0549-6/RCDome/extraction code snippets"

# credentials from .env
export DEEPSEEK_KEY=$(grep '^DEEPSEEK_KEY=' .env | cut -d= -f2)
export NOTIFY_TO=$(grep '^NOTIFY_TO=' .env | cut -d= -f2)
export NOTIFY_FROM=$(grep '^NOTIFY_FROM=' .env | cut -d= -f2)
export NOTIFY_PASS=$(grep '^NOTIFY_PASS=' .env | cut -d= -f2)

notify() {
    python3 notify_email.py "$1" 2>/dev/null
}

while true; do
    HOUR=$(date -u +%H)
    DOW=$(date -u +%u)   # 1=Mon .. 7=Sun
    PEAK=0
    if [ "$DOW" -le 5 ]; then
        if [ "$HOUR" -ge 1 ] && [ "$HOUR" -lt 4 ]; then PEAK=1; fi
        if [ "$HOUR" -ge 6 ] && [ "$HOUR" -lt 10 ]; then PEAK=1; fi
    fi
    if [ "$PEAK" -eq 1 ]; then
        if pgrep -f "deepseek_cot_v11_full.py" >/dev/null; then
            pkill -TERM -f "deepseek_cot_v11_full.py"
            echo "$(date) PEAK - paused"
            notify "RCDome: extracao PAUSADA (pico) em $(date)"
        fi
    else
        if ! pgrep -f "deepseek_cot_v11_full.py" >/dev/null; then
            nohup python3 -u deepseek_cot_v11_full.py >> deepseek_cot_v11_full.log 2>&1 &
            echo "$(date) OFF-PEAK - resumed"
            notify "RCDome: extracao RETOMADA (off-peak) em $(date)"
        fi
    fi
    sleep 60
done
