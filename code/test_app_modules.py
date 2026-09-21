# -*- coding: utf-8 -*-
"""Headless browser smoke test — every RCDome module."""
import sys, time
sys.stdout.reconfigure(encoding='utf-8')
from playwright.sync_api import sync_playwright

console_errors = []
page_errors = []

with sync_playwright() as p:
    b = p.chromium.launch(channel='chrome', headless=True)
    page = b.new_page(viewport={"width": 1400, "height": 900})
    page.on("console", lambda m: console_errors.append(m.text) if m.type == "error" else None)
    page.on("pageerror", lambda e: page_errors.append(str(e)))

    print("== open app ==")
    page.goto("http://127.0.0.1:8890/", wait_until="networkidle", timeout=60000)
    page.wait_for_timeout(3000)
    print("  title:", page.title()[:60])
    print("  body has tabs:", page.locator('a[data-value="Home"]').count() > 0)

    tabs = ["Home", "Operational Definitions", "Compare Definitions",
            "RCD entities", "Gene Catalog", "RCDome Board", "Network", "About"]
    for tab in tabs:
        try:
            if tab == "Home":
                sel = page.locator('a[data-value="Home"]')
            elif tab == "Explore RCDome":
                sel = page.locator('a[data-value*="Explore"]')
            elif tab == "RCDome Board":
                sel = page.locator('a[data-value*="Board"]')
            else:
                sel = page.locator(f'a[data-value="{tab}"]')
            if sel.count() == 0:
                print(f"  [{tab}] TAB NOT FOUND")
                continue
            sel.first.click()
            page.wait_for_timeout(2500)
            body = page.inner_text("body")[:120].replace("\n", " ")
            print(f"  [{tab}] OK | body: {body[:90]}")
        except Exception as e:
            print(f"  [{tab}] ERROR: {str(e)[:100]}")

    # ── Gene Catalog: click a gene row → gene detail ──
    print("\n== Gene Catalog interaction ==")
    try:
        page.locator('a[data-value="Gene Catalog"]').first.click()
        page.wait_for_timeout(4000)
        # the genes table (DT)
        tbl = page.locator("#table_genes table, #gene_catalog table, table.dataTable")
        print("  table found:", tbl.count() > 0)
        if tbl.count() > 0:
            # click the first data row (skip header)
            row = page.locator("table.dataTable tbody tr").first
            if row.count() > 0:
                row.click()
                page.wait_for_timeout(3000)
                # after navigation, the home iframe should show the gene detail
                iframe = page.locator("#home_iframe")
                print("  home_iframe present:", iframe.count() > 0)
                if iframe.count() > 0:
                    src = iframe.get_attribute("src")
                    print("  iframe src:", src)
                    # check the overlay appears then hides
                    ov = page.locator("#home_loading_overlay")
                    print("  overlay present:", ov.count() > 0)
            else:
                print("  no data rows to click")
        else:
            print("  gene table not found")
    except Exception as e:
        print("  gene catalog ERROR:", str(e)[:150])

    # ── Operational Definitions: entity list ──
    print("\n== Operational Definitions ==")
    try:
        page.locator('a[data-value="Operational Definitions"]').first.click()
        page.wait_for_timeout(3000)
        items = page.locator("#od-od_list button").count()
        print("  od_list items:", items)
    except Exception as e:
        print("  OD ERROR:", str(e)[:100])

    b.close()

print("\n== console errors ==", len(console_errors))
for e in console_errors[:10]:
    print("  ", e[:120])
print("== page errors ==", len(page_errors))
for e in page_errors[:10]:
    print("  ", e[:120])
