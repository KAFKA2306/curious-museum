"""Verify real HTTP navigation and browser persistence before/after GitHub Pages deployment.

Local: python tests/site_smoke.py
Production: MUSEUM_SITE_URL=https://... EXPECTED_SHA=$GITHUB_SHA python tests/site_smoke.py
"""

import functools
import http.server
import json
import os
from pathlib import Path
import tempfile
import threading
import time
from urllib.parse import urljoin
from urllib.request import urlopen

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *_args):
        pass


def assert_published_sha(base_url, expected):
    """Fail closed if Pages still serves an older deployment or a 404 page."""
    if not expected:
        return
    url = urljoin(base_url, 'version.txt')
    last_error = None
    for attempt in range(16):
        try:
            with urlopen(url, timeout=15) as response:
                actual = response.read(200).decode('utf-8').strip()
            if actual == expected:
                print(f'PASS Pages artifact SHA: {expected}')
                return
            last_error = f'expected {expected}, served {actual!r}'
        except Exception as error:
            last_error = str(error)
        if attempt < 15:
            time.sleep(5)
    raise AssertionError(f'Pages deployment is unavailable or stale at {url}: {last_error}')


def check_browser(base_url):
    errors = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 375, 'height': 812}, accept_downloads=True)
        page = context.new_page()
        page.on('pageerror', lambda err: errors.append(str(err)))

        home_url = urljoin(base_url, 'index.html')
        response = page.goto(home_url, wait_until='load', timeout=30000)
        assert response and response.status == 200, f'Home HTTP status: {response.status if response else None}'
        assert page.get_by_role('link', name='珍品を発掘する ↗').count() == 1, 'Home-to-curation link missing'
        page.get_by_role('link', name='珍品を発掘する ↗').click()
        page.wait_for_url('**/curation.html', timeout=15000)
        assert page.locator('.card').count() == 40, '40 candidate exhibits not rendered'

        page.get_by_role('button', name='新着25件だけ').click()
        assert page.locator('.card').count() == 25, 'New-only filter failed'
        page.get_by_role('button', name='新着25件だけ').click()
        page.get_by_label('展示候補を検索').fill('ミサイル')
        assert page.locator('.card').count() >= 2, 'Search filter failed'
        page.get_by_label('展示候補を検索').fill('')

        card = page.locator('.card').filter(has=page.get_by_role('heading', name='CIAの機械トンボ'))
        card.get_by_role('button', name='説明・クイズを見る').click()
        card.locator('.answers button').nth(1).click()
        assert card.get_by_text('正解。出典も確かめてみよう。').count() == 1, 'Answer feedback failed'
        card.get_by_role('button', name='収蔵候補に選ぶ').click()
        saved = json.loads(page.evaluate("localStorage.getItem('curious-museum-curation-v1')"))
        assert 'cia-dragonfly' in saved, 'Selection not saved to real localStorage'

        page.reload(wait_until='load')
        page.get_by_role('button', name='選んだ候補だけ').click()
        assert page.locator('.card').count() == 1, 'Selection lost across actual page reload'
        with tempfile.TemporaryDirectory() as temp_dir:
            with page.expect_download() as download:
                page.get_by_role('button', name='選んだ候補を書き出す').click()
            exported = Path(temp_dir) / 'candidate-export.json'
            download.value.save_as(str(exported))
            ids = [item['id'] for item in json.loads(exported.read_text(encoding='utf-8'))['items']]
            assert ids == ['cia-dragonfly'], f'Export mismatch: {ids}'

        page.get_by_role('button', name='選んだ候補だけ').click()
        page.set_viewport_size({'width': 320, 'height': 720})
        assert page.locator('.card').count() == 40
        assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth + 1'), 'Curation overflows at 320px'
        response = page.goto(home_url, wait_until='load')
        assert response and response.status == 200
        assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth + 1'), 'Home overflows at 320px'
        assert not errors, f'Browser JavaScript errors: {errors}'
        context.close()
        browser.close()
    print(f'PASS real HTTP browser smoke: {base_url} (40 exhibits, filters, quiz, reload, export, 320px)')


def main():
    remote_url = os.getenv('MUSEUM_SITE_URL', '').strip()
    if remote_url:
        base_url = remote_url.rstrip('/') + '/'
        assert base_url.startswith('https://'), 'Published Pages must use HTTPS'
        assert_published_sha(base_url, os.getenv('EXPECTED_SHA', '').strip())
        check_browser(base_url)
        return

    handler = functools.partial(QuietHandler, directory=str(ROOT))
    server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        check_browser(f'http://127.0.0.1:{server.server_port}/')
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


if __name__ == '__main__':
    main()
