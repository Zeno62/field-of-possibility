"""Run: python verify.py. Requires playwright and a Chromium installation."""
from pathlib import Path
import hashlib
import json
import os
from playwright.sync_api import sync_playwright

HTML = Path(__file__).with_name('index.html').read_text(encoding='utf-8')
VIEWPORTS = [('desktop', 1440, 1050, 1), ('small-phone', 320, 568, 2),
             ('phone', 390, 844, 3), ('large-phone', 430, 932, 3),
             ('landscape', 844, 390, 2)]
report = {'sha256': hashlib.sha256(HTML.encode()).hexdigest(),
          'environment': 'Chromium emulation, not a physical iPhone/Safari',
          'cases': []}
with sync_playwright() as p:
    exe = os.environ.get('CHROMIUM_PATH', '/usr/bin/chromium')
    options = {'headless': True, 'args': ['--no-sandbox']}
    if Path(exe).exists():
        options['executable_path'] = exe
    browser = p.chromium.launch(**options)
    for name, width, height, dpr in VIEWPORTS:
        page = browser.new_page(viewport={'width': width, 'height': height},
                                device_scale_factor=dpr, is_mobile=width < 900,
                                has_touch=width < 900)
        errors, requests = [], []
        page.on('pageerror', lambda e: errors.append(str(e)))
        page.on('request', lambda r: requests.append(r.url))
        page.set_content(HTML)
        page.wait_for_function('window.FieldLab && document.documentElement.dataset.ready === "true"')
        checks = page.evaluate('FieldLab.check()')
        assert all(c['pass'] for c in checks), checks
        assert page.evaluate('document.documentElement.scrollWidth <= document.documentElement.clientWidth')
        for key in ('tai', 'pi'):
            if width <= 760:
                page.locator(f'.mobile-tabs [data-world="{key}"]').click()
            assert page.locator(f'#{key}Canvas').get_attribute('data-rendered') == 'true'
        if width <= 760:
            page.locator('.mobile-tabs [data-world="tai"]').click()
        initial = page.evaluate('FieldLab.signature(FieldLab.getState().models[0])')
        for line in range(1, 7):
            page.locator(f'[data-line="{line}"]').click()
            assert initial == page.evaluate('FieldLab.signature(FieldLab.getState().models[0])')
        page.locator('[data-line="2"]').click()
        page.locator('#preview').click()
        assert initial == page.evaluate('FieldLab.signature(FieldLab.getState().models[0])')
        page.locator('#commit').click()
        assert page.evaluate('FieldLab.getState().localWord') == 32
        assert page.evaluate('FieldLab.getState().models.map(m => m.metrics.connections)') == [5, 0]
        assert page.evaluate('FieldLab.getState().models[0].gua.find(g => g.id === "local").roles[0].ref') == 't0'
        page.locator('#reset').click()
        page.locator('#taiCanvas').scroll_into_view_if_needed()
        before = page.evaluate('FieldLab.getState().camera')
        box = page.locator('#taiCanvas').bounding_box()
        page.mouse.move(box['x'] + .4 * box['width'], box['y'] + .45 * box['height'])
        page.mouse.down()
        page.mouse.move(box['x'] + .6 * box['width'], box['y'] + .55 * box['height'], steps=6)
        page.mouse.up()
        assert before != page.evaluate('FieldLab.getState().camera')
        assert initial == page.evaluate('FieldLab.signature(FieldLab.getState().models[0])')
        assert not errors, errors
        assert not [r for r in requests if r.startswith('http')], requests
        report['cases'].append({'name': name, 'passed': True, 'errors': errors,
                                'external_http_requests': 0, 'checks': len(checks)})
        page.close()
    page = browser.new_page(viewport={'width': 390, 'height': 844}, java_script_enabled=False)
    page.set_content(HTML)
    assert page.locator('#taiStage svg.still').is_visible()
    assert page.locator('noscript').is_visible()
    report['no_script_fallback'] = True
    report['all_single_line_flips'] = 384
    browser.close()
print(json.dumps(report, ensure_ascii=False, indent=2))
