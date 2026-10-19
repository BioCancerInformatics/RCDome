# -*- coding: utf-8 -*-
"""Comprehensive RCDome app test drive: every module + every filter + response time."""
import sys, time, json
sys.stdout.reconfigure(encoding='utf-8')
from playwright.sync_api import sync_playwright

URL = "http://127.0.0.1:8890/"
results = []
console_errors = []
page_errors = []


def measure(label, fn):
    t0 = time.time()
    err = None
    try:
        fn()
        status = "PASS"
    except Exception as e:
        err = str(e)[:140]
        status = "FAIL"
    dt = round(time.time() - t0, 2)
    results.append({"label": label, "status": status, "time_s": dt, "err": err})
    print(f"  {status:4s}  {dt:5.2f}s  {label}{('  ' + err) if err else ''}")


def set_selectize(page, selector, value, add=False):
    if add:
        page.evaluate(
            "([sel, val]) => { const el = document.querySelector(sel); if (el && el.selectize) el.selectize.addItem(val); }",
            [selector, value])
    else:
        page.evaluate(
            "([sel, val]) => { const el = document.querySelector(sel); if (el && el.selectize) el.selectize.setValue(val); }",
            [selector, value])


with sync_playwright() as p:
    b = p.chromium.launch(channel='chrome', headless=True)
    page = b.new_page(viewport={"width": 1400, "height": 900})
    page.on("console", lambda m: console_errors.append(m.text) if m.type == "error" else None)
    page.on("pageerror", lambda e: page_errors.append(str(e)))

    print("== load app ==")
    measure("app initial load (networkidle)", lambda: page.goto(URL, wait_until="networkidle", timeout=60000))
    page.wait_for_timeout(6000)

    # ── every tab render ──────────────────────────────────────────────
    print("\n== tab render ==")
    tabs = [("Home", 'a[data-value="Home"]'),
            ("Explore RCDome", 'a[data-value*="Explore"]'),
            ("Operational Definitions", 'a[data-value="Operational Definitions"]'),
            ("Compare Definitions", 'a[data-value="Compare Definitions"]'),
            ("RCD entities", 'a[data-value="RCD entities"]'),
            ("Gene Catalog", 'a[data-value="Gene Catalog"]'),
            ("RCDome Board", 'a[data-value*="Board"]'),
            ("Network", 'a[data-value="Network"]'),
            ("About", 'a[data-value="About"]')]
    for label, sel in tabs:
        def go(sel=sel):
            page.click(sel)
            page.wait_for_timeout(1800)
        measure(f"tab: {label}", go)

    # ── Operational Definitions: entity list + detail ─────────────────
    print("\n== Operational Definitions ==")
    page.click('a[data-value="Operational Definitions"]')
    page.wait_for_timeout(1500)
    measure("OD: entity buttons rendered (53)", lambda: (_ for _ in ()).throw(AssertionError("count!=53")) if page.locator("#od-od_list button").count() != 53 else None)
    measure("OD: click 'Apoptosis' → detail", lambda: (page.locator("#od-od_list button", has_text="Apoptosis").first.click(), page.wait_for_timeout(1200)))

    # ── Compare Definitions ───────────────────────────────────────────
    print("\n== Compare Definitions ==")
    page.click('a[data-value="Compare Definitions"]')
    page.wait_for_timeout(1500)
    measure("CD: select 3 entities", lambda: set_selectize(page, "#od_compare-cmp_entities", "Ferroptosis", add=True) or set_selectize(page, "#od_compare-cmp_entities", "Necroptosis", add=True) or set_selectize(page, "#od_compare-cmp_entities", "Pyroptosis", add=True) or page.wait_for_timeout(1500))
    measure("CD: switch mode (radio)", lambda: (page.evaluate("() => { const r = document.querySelectorAll('#od_compare-cmp_mode input'); if(r.length>1) r[1].click(); }"), page.wait_for_timeout(1200)))

    # ── RCD entities grid ─────────────────────────────────────────────
    print("\n== RCD entities (grid) ==")
    page.click('a[data-value="RCD entities"]')
    page.wait_for_timeout(1500)
    measure("RCDgrid: cells rendered", lambda: (_ for _ in ()).throw(AssertionError("no grid")) if page.locator(".rcd-cell, [class*=rcd]").count() == 0 else None)
    measure("RCDgrid: search selectize → 'Ferroptosis'", lambda: (set_selectize(page, "#rcd_grid-rcd_search", "Ferroptosis"), page.wait_for_timeout(1200)))
    measure("RCDgrid: close detail modal", lambda: (page.evaluate("() => { const m = document.getElementById('shiny-modal'); if (m) { $('.modal').modal('hide'); } }"), page.wait_for_timeout(600)))

    # ── Gene Catalog: all 9 filters ───────────────────────────────────
    print("\n== Gene Catalog filters ==")
    page.click('a[data-value="Gene Catalog"]')
    page.wait_for_timeout(2500)
    gc_filters = [
        ("GC: f_biotype → protein_coding", "#gene_catalog-f_biotype", "protein_coding", True),
        ("GC: f_rcd → Ferroptosis", "#gene_catalog-f_rcd", "Ferroptosis", True),
        ("GC: f_cancer → suppressor", "#gene_catalog-f_cancer", "suppressor", True),
        ("GC: f_tier → T1", "#gene_catalog-f_tier", "T1", True),
        ("GC: f_mech → YES", "#gene_catalog-f_mech", "YES", True),
        ("GC: f_role → EXECUTOR", "#gene_catalog-f_role", "EXECUTOR", True),
        ("GC: f_dir → PROMOTES", "#gene_catalog-f_dir", "PROMOTES", True),
        ("GC: f_db → (a source DB)", "#gene_catalog-f_db", None, True),
    ]
    for label, sel, val, add in gc_filters:
        def do(sel=sel, val=val, add=add):
            if val is None:
                page.evaluate("([s]) => { const el = document.querySelector(s); if (el && el.selectize) { const k = Object.keys(el.selectize.options)[0]; el.selectize.addItem(k); } }", [sel])
            else:
                set_selectize(page, sel, val, add=add)
            page.wait_for_timeout(1400)
        measure(label, do)
    # reset filters + death core + source radio
    measure("GC: reset filters (clear all selectize)", lambda: (page.evaluate("() => { document.querySelectorAll('#gene_catalog .selectized').forEach(e => { if (e.selectize) e.selectize.clear(); }); }"), page.wait_for_timeout(1500)))
    page.click('a[data-value="Gene Catalog"]'); page.wait_for_timeout(2500)
    measure("GC: Death core (executors) button", lambda: (page.click("#gene_catalog-death_core"), page.wait_for_timeout(1800)))
    measure("GC: source radio → Elicit", lambda: (page.evaluate("() => { const r = document.querySelectorAll('input[name^=\"gene_catalog-source_sel_r\"]'); if(r.length>1) r[1].click(); }"), page.wait_for_timeout(1500)))
    measure("GC: gene row click → detail", lambda: (page.locator("#gene_catalog-table_genes table.dataTable tbody tr, table.dataTable").first.locator("tbody tr").first.click(), page.wait_for_timeout(1500)))

    # ── RCDome Board ──────────────────────────────────────────────────
    print("\n== RCDome Board ==")
    page.click('a[data-value*="Board"]')
    page.wait_for_timeout(2000)
    measure("Board: entity selectize → Ferroptosis", lambda: (set_selectize(page, "#board-board_entity", "Ferroptosis"), page.wait_for_timeout(1500)))
    measure("Board: example query click", lambda: (page.locator("button[id^='board-ex_q']").first.click(), page.wait_for_timeout(1200)))

    # ── Network ───────────────────────────────────────────────────────
    print("\n== Network ==")
    page.click('a[data-value="Network"]')
    page.wait_for_timeout(2000)
    measure("Network: rcd_filter → Apoptosis", lambda: (set_selectize(page, "#network-rcd_filter", "Apoptosis", add=True), page.wait_for_timeout(2500)))
    measure("Network: level_filter → L1", lambda: (set_selectize(page, "#network-level_filter", "L1", add=True), page.wait_for_timeout(1500)))
    measure("Network: role_filter → EXECUTOR", lambda: (set_selectize(page, "#network-role_filter", "EXECUTOR", add=True), page.wait_for_timeout(1500)))
    measure("Network: mech_filter → MECHANISTIC", lambda: (set_selectize(page, "#network-mech_filter", "MECHANISTIC", add=True), page.wait_for_timeout(1500)))
    measure("Network: cap_select → 100", lambda: (page.evaluate("() => { const el = document.querySelector('#network-cap_select'); if (el && el.selectize) el.selectize.setValue('100'); }"), page.wait_for_timeout(1500)))
    measure("Network: canvas rendered", lambda: (_ for _ in ()).throw(AssertionError("no canvas")) if page.locator("canvas").count() == 0 else None)

    b.close()

print("\n" + "=" * 60)
npass = sum(1 for r in results if r["status"] == "PASS")
nfail = len(results) - npass
print(f"RESULTS: {npass} PASS / {nfail} FAIL  (total {len(results)})")
slow = [r for r in results if r["time_s"] > 2.0]
if slow:
    print("\nSlowest interactions (>2s):")
    for r in sorted(slow, key=lambda x: -x["time_s"]):
        print(f"  {r['time_s']:.2f}s  {r['label']}")
print(f"\nConsole errors: {len(console_errors)}")
for e in console_errors[:10]:
    print("  ", e[:120])
print(f"Page errors: {len(page_errors)}")
for e in page_errors[:10]:
    print("  ", e[:120])

with open("analysis/TESTDRIVE_full_app_2026-09-21.json", "w", encoding="utf-8") as f:
    json.dump({"results": results, "console_errors": console_errors, "page_errors": page_errors}, f, indent=2, ensure_ascii=False)
print("\nSaved: analysis/TESTDRIVE_full_app_2026-09-21.json")
