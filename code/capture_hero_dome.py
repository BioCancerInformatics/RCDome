# -*- coding: utf-8 -*-
# Re-capture the hero_dome.png (Home page hero: title + dome + ontology legend)
from playwright.sync_api import sync_playwright

OUT = 'D:/RCDome_github/docs/hero_dome.png'

with sync_playwright() as p:
    browser = p.chromium.launch(
        executable_path='C:/Program Files/Google/Chrome/Application/chrome.exe',
        headless=True)
    page = browser.new_page(viewport={'width': 1360, 'height': 900}, device_scale_factor=2)
    page.goto('http://127.0.0.1:8890', wait_until='networkidle', timeout=90000)
    page.wait_for_timeout(7000)  # let the dome + legend render
    hero = page.locator('.hero').first
    hero.screenshot(path=OUT)
    browser.close()
    print('hero_dome.png re-captured ->', OUT)
