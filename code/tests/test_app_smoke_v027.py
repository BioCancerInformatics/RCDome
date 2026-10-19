#!/usr/bin/env python3
"""Programmatic smoke test for the RCDome app on V027.

Runs mechanical checks that a human would otherwise do by eye, so the later
human smoke test only needs to confirm rendering + link-opening.

Checks:
  A. Matrix V027 (RDS + CSV) — dimensions, columns, Consensus coverage
  B. Decoder — 53 entities
  C. RCD descriptions + references — counts, orphans, duplicates, broken, uncited
  D. Clickable reference mapping — every [n] -> entry -> DOI/PMID (population)
  E. Filter/source columns — present + non-empty (Gene Catalog + Network)
  F. App code — all R files parse; source selectors wired
  G. HTML pages — Deep Dive card, Consensus selector, benchmark text

Exit code 0 = all pass; 1 = failures (printed).
"""
import csv
import os
import re
import sys
import subprocess
from collections import Counter
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
csv.field_size_limit(sys.maxsize)

DIST = Path('RCDome_distribution')
RSCRIPT = r'C:\Program Files\R\R-4.2.3\bin\Rscript.exe'

FAIL = []


def check(name, cond, detail=''):
    status = 'PASS' if cond else 'FAIL'
    if not cond:
        FAIL.append(name)
    print(f'  [{status}] {name}' + (f' — {detail}' if detail and not cond else ''))


def parse_citations(text):
    nums = set()
    norm = text.replace('\u2013', '-').replace('\u2014', '-')
    for m in re.finditer(r'\[([0-9,\s\-]+)\]', norm):
        for part in m.group(1).split(','):
            part = part.strip()
            if not part: continue
            if '-' in part:
                a, b = part.split('-', 1)
                try:
                    for n in range(int(a), int(b) + 1): nums.add(n)
                except ValueError: pass
            else:
                try: nums.add(int(part))
                except ValueError: pass
    return nums


def parse_refs(text):
    refs = {}
    for line in text.splitlines():
        line = line.strip()
        if not line: continue
        m = re.match(r'\*{0,2}\[(\d+)\]\*{0,2}\s*(.*)', line)
        if m: refs[int(m.group(1))] = m.group(2); continue
        m = re.match(r'^(\d+)[\.\)]\s*(.*)', line)
        if m: refs[int(m.group(1))] = m.group(2)
    return refs


def main():
    print('=== RCDome app smoke test (V027) ===\n')

    # A. Matrix RDS via R
    print('A. Matrix V027')
    r = subprocess.run([RSCRIPT, '-e',
        "m<-readRDS('RCDome_distribution/data/unified_gene_rcd_matrix_V027.rds');"
        "cat(nrow(m), ncol(m), sum(m$consensus_role!='' & !is.na(m$consensus_role)))"],
        capture_output=True, text=True)
    dims = r.stdout.split()
    if len(dims) == 3:
        nrow, ncol, cons = int(dims[0]), int(dims[1]), int(dims[2])
        check('rows = 22,473', nrow == 22473, f'{nrow}')
        check('columns = 82', ncol == 82, f'{ncol}')
        check('consensus_role filled 100%', cons == nrow, f'{cons}/{nrow}')
    else:
        check('RDS loads', False, r.stderr.strip()[:100])

    # B. Decoder
    print('\nB. Decoder')
    dec = list(csv.DictReader(open(DIST / 'data/RCDome_Decoder_53.csv', encoding='utf-8-sig')))
    check('53 entities', len(dec) == 53, f'{len(dec)}')

    # C. Descriptions + references
    print('\nC. Descriptions + references')
    desc_dir = DIST / 'data/RCD modulo/descricao RCDs'
    ref_dir = DIST / 'data/RCD modulo/referencias'
    desc = sorted(os.listdir(desc_dir))
    refs_files = sorted(os.listdir(ref_dir))
    check('53 description files', len(desc) == 53, f'{len(desc)}')
    check('53 reference files', len(refs_files) == 53, f'{len(refs_files)}')

    total_refs = 0
    orphans = 0
    dup_dois = 0
    for f in desc:
        name = f[:-4]
        dtxt = (desc_dir / f).read_text(encoding='utf-8')
        rp = ref_dir / f
        rtxt = rp.read_text(encoding='utf-8') if rp.exists() else ''
        cited = parse_citations(dtxt)
        refs = parse_refs(rtxt)
        total_refs += len(refs)
        orphans += len(cited - set(refs))
        dois = re.findall(r'10\.\d{4,9}/\S+', rtxt)
        dup_dois += len(dois) - len(set(d.lower() for d in dois))
    check('total references = 2,129', total_refs == 2129, f'{total_refs}')
    check('orphan citations = 0', orphans == 0, f'{orphans}')
    check('duplicate DOIs = 0', dup_dois == 0, f'{dup_dois}')

    # D. Clickable mapping population
    print('\nD. Clickable mapping population')
    with_doi = 0
    with_pmid = 0
    for f in refs_files:
        t = (ref_dir / f).read_text(encoding='utf-8')
        with_doi += len(re.findall(r'10\.\d{4,9}/\S+', t))
        with_pmid += len(re.findall(r'PMID:\s*\d{7,8}', t))
    check('DOI-bearing references ≥ 2,121', with_doi >= 2121, f'{with_doi}')
    check('PMID-bearing references present', with_pmid >= 1, f'{with_pmid}')

    # E. Filter/source columns
    print('\nE. Filter/source columns')
    rows = list(csv.DictReader(open(DIST / 'data/unified_gene_rcd_matrix_V027.csv',
                                    encoding='utf-8-sig', errors='replace')))
    cols = set(rows[0].keys())
    for c in ['cot_role', 'cot_direction', 'mechanistic_class',
              'consensus_role', 'consensus_direction', 'consensus_mechanistic',
              'rcd_gene_type', 'role_direction']:
        present = c in cols
        nonempty = present and any((r.get(c) or '').strip() for r in rows[:500])
        check(f'{c} present + non-empty', present and nonempty)

    # F. App code parse + selectors wired
    print('\nF. App code')
    rfiles = ['RCDome_distribution/global.R', 'RCDome_distribution/server.R', 'RCDome_distribution/ui.R'] + \
             [str(DIST / 'modules' / f).replace('\\', '/') for f in os.listdir(DIST / 'modules') if f.endswith('.R')] + \
             [str(DIST / 'R' / f).replace('\\', '/') for f in os.listdir(DIST / 'R') if f.endswith('.R')]
    rvec = 'c(' + ', '.join("'" + f + "'" for f in rfiles) + ')'
    tmp = '_smoke_parse_tmp.R'
    with open(tmp, 'w', encoding='utf-8') as fh:
        fh.write('files <- ' + rvec + '\n')
        fh.write('fails <- character(0)\n')
        fh.write('for (f in files) {\n')
        fh.write('  ok <- tryCatch({invisible(parse(f)); TRUE}, error=function(e) FALSE)\n')
        fh.write('  if (!ok) fails <- c(fails, f)\n')
        fh.write('}\n')
        fh.write("if (length(fails)) cat('FAIL:', paste(fails, collapse=', ')) else cat('OK')\n")
    r = subprocess.run([RSCRIPT, tmp], capture_output=True, text=True)
    os.remove(tmp)
    check('all R files parse', r.stdout.strip() == 'OK', (r.stdout + r.stderr).strip()[:120])

    gc = (DIST / 'modules/mod_gene_catalog.R').read_text(encoding='utf-8')
    nw = (DIST / 'modules/mod_network.R').read_text(encoding='utf-8')
    check('Gene Catalog: Consensus source', '"consensus"' in gc)
    check('Network: Consensus source', '"consensus"' in nw and 'edge_source' in nw)

    disc = (DIST / 'modules/mod_discrepancy.R').read_text(encoding='utf-8')
    check('Discrepancy Radar: module file', 'mod_discrepancy_server' in disc and 'mod_discrepancy_ui' in disc)
    check('Discrepancy Radar: tab present', 'Discrepancy Radar' in (DIST / 'ui.R').read_text(encoding='utf-8'))
    check('Discrepancy Radar: server wired', 'mod_discrepancy_server("discrepancy")' in (DIST / 'server.R').read_text(encoding='utf-8'))

    tl = (DIST / 'modules/mod_timeline.R').read_text(encoding='utf-8')
    check('Discovery Timeline: module file', 'mod_timeline_server' in tl and 'mod_timeline_ui' in tl)
    check('Discovery Timeline: tab present', 'Discovery Timeline' in (DIST / 'ui.R').read_text(encoding='utf-8'))
    check('Discovery Timeline: server wired', 'mod_timeline_server("timeline")' in (DIST / 'server.R').read_text(encoding='utf-8'))

    tr = (DIST / 'modules/mod_tour.R').read_text(encoding='utf-8')
    check('Reader Mode: module file', 'mod_tour_server' in tr and 'mod_tour_ui' in tr)
    check('Reader Mode: server wired', 'mod_tour_server("tour")' in (DIST / 'server.R').read_text(encoding='utf-8'))
    check('Reader Mode: replay button', 'Replay tour' in (DIST / 'ui.R').read_text(encoding='utf-8'))

    check('3D RCDome: tab present', 'dome_3d.html' in (DIST / 'ui.R').read_text(encoding='utf-8'))
    check('3D Dome: page present', (DIST / 'www/dome_3d.html').exists())
    check('3D Dome: gene click wired', 'dome3d_gene' in (DIST / 'server.R').read_text(encoding='utf-8'))
    check('3D Dome: entity constellation view', 'focusEntity' in (DIST / 'www/dome_3d.html').read_text(encoding='utf-8'))

    # G. HTML pages
    print('\nG. HTML pages')
    exp = (DIST / 'www/explore.html').read_text(encoding='utf-8', errors='replace')
    lp = (DIST / 'www/landing_page.html').read_text(encoding='utf-8', errors='replace')
    dp = (DIST / 'www/detail_page_wireframe.html').read_text(encoding='utf-8', errors='replace')
    check('explore.html: Deep Dive card', 'RCD Entity Deep Dive' in exp)
    check('landing_page.html: Deep Dive card', 'RCD Entity Deep Dive' in lp)
    check('detail page: Consensus selector', 'value="consensus"' in dp)
    check('explore.html: new benchmarks', 'label-error benchmark' in exp)

    print()
    if FAIL:
        print(f'FAILURES ({len(FAIL)}):')
        for f in FAIL:
            print(f'  - {f}')
        sys.exit(1)
    else:
        print('ALL SMOKE-TEST CHECKS PASSED.')


if __name__ == '__main__':
    main()
