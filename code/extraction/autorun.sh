#!/bin/bash
cd "$(dirname "$0")"
source .env
echo "RCDome Phase 2A v2"
while true; do
    python3 channel_c_evidence_tier.py
    sleep 30
done
