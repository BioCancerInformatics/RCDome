# -*- coding: utf-8 -*-
import json
from playwright.sync_api import sync_playwright

URL = "http://127.0.0.1:8892"
CHROME = "C:/Program Files/Google/Chrome/Application/chrome.exe"

# (label, navbar selector)
TABS = [
    ("Home",                    "a[data-value='Home']"),
    ("Explore RCDome",          "a[data-value*='Explore']"),
    ("Operational Definitions", "a[data-value='Operational Definitions']"),
    ("Compare Definitions",     "a[data-value='Compare Definitions']"),
    ("RCD entities",            "a[data-value='RCD entities']"),
    ("Gene Catalog",            "a[data-value='Gene Catalog']"),
    ("RCDome Board",            "a[data-value*='Board']"),
    ("Network",                 "a[data-value='Network']"),
    ("About",                   "a[data-value='About']"),
]

results = {"tabs": {}, "network": {}}

with sync_playwright() as p:
    browser = p.chromium.launch(executable_path=CHROME, headless=True)
    page = browser.new_page(viewport={"width": 1400, "height": 900})

    page_errors, console_errors = [], []
    page.on("pageerror", lambda e: page_errors.append(str(e)))
    page.on("console", lambda m: console_errors.append(m.text) if m.type == "error" else None)

    page.goto(URL, wait_until="domcontentloaded", timeout=60000)
    page.wait_for_timeout(12000)

    for label, sel in TABS:
        page_errors.clear(); console_errors.clear()
        try:
            page.click(sel, timeout=10000)
            page.wait_for_timeout(5000)
            results["tabs"][label] = {
                "clicked": True,
                "page_errors": list(page_errors),
                "console_errors": list(console_errors),
            }
        except Exception as e:
            results["tabs"][label] = {"clicked": False, "error": str(e)}

    # ── Network interaction ─────────────────────────────────────────────────
    try:
        page.click("a[data-value='Network']", timeout=10000)
        page.wait_for_timeout(3000)
        page_errors.clear(); console_errors.clear()

        results["network"]["validate_message_visible"] = (
            page.locator("text=Select one or more RCD entities").count() > 0
        )

        # open the entity selectize + choose Apoptosis via its JS API
        page.evaluate(
            "() => { var el = document.querySelector('#network-rcd_filter');"
            " if (el && el.selectize) { el.selectize.addItem('Apoptosis'); } }"
        )
        page.wait_for_timeout(10000)  # render capped network

        results["network"]["stats_visible"] = page.locator("text=genes").count() > 0
        results["network"]["canvas_count"] = page.locator("canvas").count()
        results["network"]["page_errors"] = list(page_errors)
        results["network"]["console_errors"] = list(console_errors)
    except Exception as e:
        results["network"]["error"] = str(e)

    browser.close()

print(json.dumps(results, indent=2))
