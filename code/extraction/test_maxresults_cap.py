"""Decisive test: does Elicit impose a hidden cap when maxResults is omitted?

Runs the SAME 4 Ferroptosis searches with EXPLICIT maxResults=500.
If paper count > 315 (the 'uncapped' result), then omission hit a default cap.
If paper count ~ 315, then 315 is the true semantic-relevance ceiling.
"""
import subprocess, json, urllib.request, io, os, csv, time

KEY = os.environ.get('ELICIT_API_KEY', '')
BASE = 'https://elicit.com/api/v2/sessions/systematic-reviews'

def call_elicit(maxr):
    body = json.dumps({
        "researchQuestion": "Gene-Ferroptosis associations in closed allow-list",
        "searches": [
            {"query": "Ferroptosis regulated cell death mechanism", "corpus": "pubmed", "searchMode": "semantic", "maxResults": maxr},
            {"query": "Ferroptosis genetic perturbation CRISPR knockout knockdown", "corpus": "pubmed", "searchMode": "semantic", "maxResults": maxr},
            {"query": "Ferroptosis pharmacological inhibitor drug mechanism", "corpus": "pubmed", "searchMode": "semantic", "maxResults": maxr},
            {"query": "Ferroptosis gene expression correlation biomarker", "corpus": "elicit", "searchMode": "semantic", "maxResults": maxr}
        ],
        "abstractScreening": {"generate": True},
        "extraction": {
            "generate": False,
            "useFigures": False,
            "questions": [
                {"name": "gene_symbol", "instructions": "HGNC gene symbol from paper. Return null if none."},
                {"name": "mechanistic_role", "instructions": "EXECUTOR if KD/KO changes Ferroptosis death. REGULATOR if modulates. MARKER if correlation only.", "choices": ["EXECUTOR", "REGULATOR", "MARKER", "UNCERTAIN"]},
                {"name": "evidence_type", "instructions": "Type: GENETIC_PERTURBATION, PHARMACOLOGICAL, EXPRESSION_CORRELATION, CITATION_ONLY.", "choices": ["GENETIC_PERTURBATION", "PHARMACOLOGICAL", "EXPRESSION_CORRELATION", "CITATION_ONLY"]},
                {"name": "verbatim_sentence", "instructions": "Copy EXACT sentence linking gene to Ferroptosis. Return null if inaccessible."},
                {"name": "role_direction", "instructions": "PROMOTES if gene increases Ferroptosis, PROTECTS if reduces.", "choices": ["PROMOTES", "PROTECTS", "ASSOCIATED", "BIDIRECTIONAL", "UNCLEAR"]},
                {"name": "required_for_death", "instructions": "Is gene required for Ferroptosis execution? YES only with perturbation data.", "choices": ["YES", "PARTIAL", "NO", "NOT_TESTED", "UNCLEAR"]}
            ]
        },
        "generateReport": False
    })
    cmd = ['curl', '-s', '-X', 'POST', BASE,
           '-H', 'Authorization: Bearer ' + KEY,
           '-H', 'Content-Type: application/json', '-d', body]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    resp = json.loads(r.stdout)
    return resp.get('sessionId', '')

def poll_and_count(sid):
    waited = 0
    while waited < 1200:
        time.sleep(20)
        waited += 20
        r = subprocess.run(['curl', '-s', f'{BASE}/{sid}',
                            '-H', f'Authorization: Bearer {KEY}', '--max-time', '20'],
                           capture_output=True, text=True, timeout=30)
        resp = json.loads(r.stdout)
        if resp.get('status') == 'completed':
            csv_url = resp.get('data', {}).get('extract', {}).get('csv', '')
            if not csv_url:
                return None, 0
            req = urllib.request.Request(csv_url)
            req.add_header('User-Agent', 'Mozilla/5.0')
            csv_data = urllib.request.urlopen(req, timeout=60).read().decode('utf-8-sig')
            rows = list(csv.DictReader(io.StringIO(csv_data)))
            papers = len(set(r.get('Title', '') for r in rows if r.get('Title', '').strip()))
            return rows, papers
        if resp.get('status') == 'failed':
            return None, -1
    return None, -2

for maxr in [100, 500]:
    sid = call_elicit(maxr)
    print(f'maxResults={maxr}: session={sid}')
    rows, papers = poll_and_count(sid)
    print(f'  papers={papers}')
    print()

print('REFERENCE:')
print('  omitted maxResults -> 315 papers')
print('  maxResults=50 -> 67 papers')
