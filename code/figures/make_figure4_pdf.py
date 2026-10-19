# -*- coding: utf-8 -*-
from playwright.sync_api import sync_playwright

HTML = 'file:///D:/Pré-artigo 5-optosis model/Cellular_Spatial_RCD_manuscript/RCDome_manuscript/Shiny app/landing_page.html'
OUT = 'D:/Pré-artigo 5-optosis model/Cellular_Spatial_RCD_manuscript/RCDome_manuscript/Figures/Figure_4_app'

with sync_playwright() as p:
    browser = p.chromium.launch(
        executable_path='C:/Program Files/Google/Chrome/Application/chrome.exe',
        headless=True)
    page = browser.new_page(viewport={'width': 1600, 'height': 1000})
    page.goto(HTML, wait_until='networkidle', timeout=90000)
    page.wait_for_timeout(9000)  # let the dome + D3 render fully
    page.pdf(path=f'{OUT}.pdf', format='A4', landscape=True, print_background=True)
    browser.close()
print('vector PDF saved')
