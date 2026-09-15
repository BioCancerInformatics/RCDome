#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
notify_email.py — sends a one-line email alert from the RCDome supervisor.
Reads credentials from environment variables (set by offpeak_supervisor.sh from .env):

  NOTIFY_TO     recipient email
  NOTIFY_FROM   sender email (the account used to log into SMTP)
  NOTIFY_PASS   SMTP password (for Gmail: an App Password, not the account password)
  NOTIFY_HOST   SMTP host (default smtp.gmail.com)
  NOTIFY_PORT   SMTP port (default 587)

Usage:  python3 notify_email.py "message text"
"""
import os
import sys
import smtplib
from email.mime.text import MIMEText

def main():
    msg_text = sys.argv[1] if len(sys.argv) > 1 else "RCDome extraction event"

    to = os.environ.get("NOTIFY_TO", "").strip()
    frm = os.environ.get("NOTIFY_FROM", "").strip()
    pwd = os.environ.get("NOTIFY_PASS", "").strip()
    host = os.environ.get("NOTIFY_HOST", "smtp.gmail.com").strip()
    port = int(os.environ.get("NOTIFY_PORT", "587"))

    if not (to and frm and pwd):
        print("notify: missing NOTIFY_TO / NOTIFY_FROM / NOTIFY_PASS", file=sys.stderr)
        return 1

    msg = MIMEText(msg_text, "plain", "utf-8")
    msg["Subject"] = "[RCDome] " + msg_text
    msg["From"] = frm
    msg["To"] = to

    try:
        server = smtplib.SMTP(host, port, timeout=20)
        server.starttls()
        server.login(frm, pwd)
        server.sendmail(frm, [to], msg.as_string())
        server.quit()
        print("notify: sent ->", to)
        return 0
    except Exception as e:
        print("notify: FAILED:", e, file=sys.stderr)
        return 2

if __name__ == "__main__":
    sys.exit(main())
