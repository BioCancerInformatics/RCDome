# -*- coding: utf-8 -*-
from playwright.sync_api import sync_playwright

OUT = 'D:/Pré-artigo 5-optosis model/Cellular_Spatial_RCD_manuscript/RCDome_manuscript/Figures/Figure4_assets/raw'
import os
os.makedirs(OUT, exist_ok=True)

with sync_playwright() as p:
    browser = p.chromium.launch(
        executable_path='C:/Program Files/Google/Chrome/Application/chrome.exe',
        headless=True)
    page = browser.new_page(viewport={'width': 1600, 'height': 1000}, device_scale_factor=2)

    # A: Home
    page.goto('http://127.0.0.1:8890', wait_until='networkidle', timeout=90000)
    page.wait_for_timeout(6000)
    page.screenshot(path=f'{OUT}/A_home.png')

    # B: Explore RCDome
    page.click('a[data-value="Explore RCDome"]')
    page.wait_for_timeout(4000)
    page.screenshot(path=f'{OUT}/B_explore.png')

    # C: Gene Catalog
    page.click('a[data-value="Gene Catalog"]')
    page.wait_for_selector('table.dataTable tbody tr', timeout=90000)
    page.wait_for_timeout(4000)
    page.screenshot(path=f'{OUT}/C_catalog.png')

    # D: detail modal — click first gene row
    page.click('table.dataTable tbody tr td:first-child')
    page.wait_for_timeout(4000)
    page.screenshot(path=f'{OUT}/D_detail.png')

    browser.close()
print('raw screenshots saved to', OUT)
