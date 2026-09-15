"""Test Elicit uncapped search for one form. Measures real paper return."""
import csv, os, json, time, subprocess, sys

ELICIT_KEY = os.environ.get('ELICIT_API_KEY', '')
ELICIT_URL = 'https://elicit.com/api/v2/sessions/systematic-reviews'

def test_uncapped(form):
    body = json.dumps({
        "researchQuestion": "Gene-" + form + " associations in closed allow-list",
        "searches": [
            {"query": form + " regulated cell death mechanism", "corpus": "pubmed", "searchMode": "semantic"},
            {"query": form + " genetic perturbation CRISPR knockout knockdown", "corpus": "pubmed", "searchMode": "semantic"},
            {"query": form + " pharmacological inhibitor drug mechanism", "corpus": "pubmed", "searchMode": "semantic"},
            {"query": form + " gene expression correlation biomarker", "corpus": "elicit", "searchMode": "semantic"}
        ],
        "abstractScreening": {"generate": True},
        "extraction": {
            "generate": False,
            "useFigures": False,
            "questions": [
                {"name": "gene_symbol", "instructions": "HGNC gene symbol from paper. Return null if none."},
                {"name": "mechanistic_role", "instructions": "EXECUTOR if KD/KO in this paper changes " + form + " death. REGULATOR if modulates. MARKER if correlation only.", "choices": ["EXECUTOR", "REGULATOR", "MARKER", "UNCERTAIN"]},
                {"name": "evidence_type", "instructions": "Type: GENETIC_PERTURBATION (KD/KO/CRISPR in this paper), PHARMACOLOGICAL, EXPRESSION_CORRELATION, CITATION_ONLY.", "choices": ["GENETIC_PERTURBATION", "PHARMACOLOGICAL", "EXPRESSION_CORRELATION", "CITATION_ONLY"]},
                {"name": "verbatim_sentence", "instructions": "Copy EXACT sentence linking gene to " + form + ". Return null if inaccessible."},
                {"name": "role_direction", "instructions": "PROMOTES if gene increases " + form + ", PROTECTS if reduces.", "choices": ["PROMOTES", "PROTECTS", "ASSOCIATED", "BIDIRECTIONAL", "UNCLEAR"]},
                {"name": "required_for_death", "instructions": "Is gene required for " + form + " execution? YES only with perturbation data.", "choices": ["YES", "PARTIAL", "NO", "NOT_TESTED", "UNCLEAR"]}
            ]
        },
        "generateReport": False
    })
    
    cmd = ['curl', '-s', '-X', 'POST', ELICIT_URL,
           '-H', 'Authorization: Bearer ' + ELICIT_KEY,
           '-H', 'Content-Type: application/json', '-d', body]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    resp = json.loads(result.stdout)
    session_id = resp.get('sessionId', '')
    print(f"Session: {session_id}")
    
    # Poll
    waited = 0
    while waited < 900:
        time.sleep(30)
        waited += 30
        poll_url = ELICIT_URL + "/" + session_id
        cmd = ['curl', '-s', poll_url, '-H', 'Authorization: Bearer ' + ELICIT_KEY]
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        resp = json.loads(r.stdout)
        status = resp.get('status', '')
        data = resp.get('data', {})
        
        # Check paper count from search/screen stages
        search_count = 0
        screen_count = 0
        if 'search' in data:
            search_count = len(data.get('search', {}).get('papers', [])) if isinstance(data.get('search', {}).get('papers'), list) else 0
        if 'screen' in data:
            screen_data = data.get('screen', {})
            if isinstance(screen_data, dict):
                screen_count = len(screen_data.get('papers', [])) if isinstance(screen_data.get('papers'), list) else 0
        
        print(f"[{waited}s] status={status} search={search_count} screen={screen_count}")
        
        if status == 'completed':
            print(f"\nCOMPLETED in {waited}s")
            # Count extraction papers
            if 'extract' in data:
                extract = data['extract']
                print(f"Extract keys: {list(extract.keys())}")
                # Check for CSV URL
                csv_url = extract.get('csv', '')
                if csv_url:
                    print(f"CSV URL present: {csv_url[:60]}...")
                    import urllib.request
                    req = urllib.request.Request(csv_url)
                    req.add_header('User-Agent', 'Mozilla/5.0')
                    csv_data = urllib.request.urlopen(req, timeout=30).read().decode('utf-8-sig')
                    rows = list(csv.DictReader(__import__('io').StringIO(csv_data)))
                    print(f"CSV ROWS: {len(rows)}")
                    if rows:
                        print(f"CSV columns: {list(rows[0].keys())[:8]}")
                else:
                    print("No CSV URL")
            return
            
        if status == 'failed':
            print("FAILED")
            return
    
    print("TIMEOUT")

if __name__ == '__main__':
    form = sys.argv[1] if len(sys.argv) > 1 else 'Cuproptosis'
    test_uncapped(form)
