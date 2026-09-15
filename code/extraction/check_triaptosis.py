import subprocess, json

KEY = 'elk_live_DiyAhcQ5sshfeJCL5Fn6Y7aRCO4yHZgo1-il-a-vvpY'

r = subprocess.run(['curl','-s','https://elicit.com/api/v2/sessions/systematic-reviews',
    '-H',f'Authorization: Bearer {KEY}','--max-time','10'],
    capture_output=True,text=True,timeout=15)

sessions = json.loads(r.stdout).get('data', json.loads(r.stdout).get('sessions',[]))
for s in sessions[:10]:
    sid = s.get('sessionId','')
    rq = s.get('researchQuestion','')[:80]
    st = s.get('status','')
    if any(w in rq.lower() for w in ['tria','ferrop','cupro']):
        print(f"{sid[:50]} | {st} | {rq}")
