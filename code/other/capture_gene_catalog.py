# -*- coding: utf-8 -*-
from playwright.sync_api import sync_playwright

OUT = 'D:/Pré-artigo 5-optosis model/Cellular_Spatial_RCD_manuscript/RCDome_manuscript/Figures/Figure4_assets/panel_C_catalog.png'

with sync_playwright() as p:
    browser = p.chromium.launch(
        executable_path='C:/Program Files/Google/Chrome/Application/chrome.exe',
        headless=True)
    page = browser.new_page(viewport={'width': 1600, 'height': 1000})
    page.goto('http://127.0.0.1:8890', wait_until='networkidle', timeout=90000)
    # click Gene Catalog tab
    page.wait_for_selector('a[data-value="Gene Catalog"]', timeout=60000)
    page.click('a[data-value="Gene Catalog"]')
    # wait for the DT table to render
    try:
        page.wait_for_selector('table.dataTable tbody tr', timeout=90000)
    except Exception as e:
        print('DT rows wait issue:', e)
    page.wait_for_timeout(5000)
    page.screenshot(path=OUT)
    print('panel C screenshot saved')
    browser.close()
