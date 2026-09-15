"""Small connectivity + fresh-code test: tiny Apoptosis extraction (maxResults=50).

Tests: (1) network to elicit.com, (2) session creation, (3) CSV download
using the FIXED poll_elicit (re-poll logic).
"""
import os, csv, io, json, subprocess, sys

sys.path.insert(0, '/mnt/sharefiles/medina/students/aluno0549-6/RCDome/extraction code snippets')
import channel_e_elicit_extract as ce

ENV = '/mnt/sharefiles/medina/students/aluno0549-6/RCDome/extraction code snippets/.env'
for line in open(ENV):
    if line.startswith('ELICIT_API_KEY='):
        os.environ['ELICIT_API_KEY'] = line.split('=', 1)[1].strip()
        break
ce.ELICIT_KEY = os.environ['ELICIT_API_KEY']
print(f"Key loaded: {ce.ELICIT_KEY[:12]}...")

# Tiny session (maxResults=50) — inline, not the production 1000
body = json.dumps({
    "researchQuestion": "Gene-Apoptosis associations",
    "searches": [
        {"query": "Apoptosis regulated cell death mechanism", "corpus": "pubmed", "searchMode": "semantic", "maxResults": 50}
    ],
    "abstractScreening": {"generate": True},
    "extraction": {
        "generate": False,
        "useFigures": False,
        "questions": [
            {"name": "gene_symbol", "instructions": "HGNC gene symbol from paper. Return null if none."},
            {"name": "mechanistic_role", "instructions": "EXECUTOR if KD/KO changes Apoptosis. REGULATOR if modulates. MARKER if correlation only.", "choices": ["EXECUTOR", "REGULATOR", "MARKER", "UNCERTAIN"]},
            {"name": "evidence_type", "instructions": "Type: GENETIC_PERTURBATION, PHARMACOLOGICAL, EXPRESSION_CORRELATION, CITATION_ONLY.", "choices": ["GENETIC_PERTURBATION", "PHARMACOLOGICAL", "EXPRESSION_CORRELATION", "CITATION_ONLY"]},
            {"name": "verbatim_sentence", "instructions": "Copy EXACT sentence linking gene to Apoptosis."},
            {"name": "role_direction", "instructions": "PROMOTES if gene increases Apoptosis, PROTECTS if reduces.", "choices": ["PROMOTES", "PROTECTS", "ASSOCIATED", "BIDIRECTIONAL", "UNCLEAR"]},
            {"name": "required_for_death", "instructions": "Is gene required for Apoptosis? YES only with perturbation data.", "choices": ["YES", "PARTIAL", "NO", "NOT_TESTED", "UNCLEAR"]}
        ]
    },
    "generateReport": False
})

cmd = ['curl', '-s', '-X', 'POST', ce.ELICIT_URL,
       '-H', 'Authorization: Bearer ' + ce.ELICIT_KEY,
       '-H', 'Content-Type: application/json', '-d', body, '--max-time', '60']
r = subprocess.run(cmd, capture_output=True, text=True, timeout=70)
try:
    resp = json.loads(r.stdout)
except Exception:
    print(f"FAIL: non-JSON response (network down). stdout={r.stdout[:200]!r}")
    sys.exit(1)

sid = resp.get('sessionId', '')
if not sid:
    print(f"FAIL: no session. response={r.stdout[:300]}")
    sys.exit(1)
print(f"Session: {sid}")

print("Polling + CSV download (fixed re-poll)...")
_, csv_data = ce.poll_elicit(sid, max_wait=3600)
if not csv_data:
    print("FAIL: no CSV after re-poll")
    sys.exit(1)

rows = list(csv.DictReader(io.StringIO(csv_data)))
papers = len(set(rr.get('Title', '').strip() for rr in rows if rr.get('Title', '').strip()))
print(f"SUCCESS: {len(rows)} rows, {papers} papers")
print("Connectivity + fresh code: WORKING")
