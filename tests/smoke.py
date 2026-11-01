"""Browser smoke test for the interactive source pages (Playwright required)."""
import json
import pathlib
import tempfile
import os
import shutil
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parents[1]


def mount_page(context, page_name, selected=None):
    """Use set_content for sandboxed test environments that block file navigation."""
    page = context.new_page()
    page.goto("about:blank")
    page.evaluate(
        """seed => {
           const values = new Map(seed ? [['curious-museum-curation-v1', seed]] : []);
           Object.defineProperty(window, 'localStorage', {
             configurable: true,
             get() { return {
               getItem: key => values.get(key) || null,
               setItem: (key, value) => values.set(key, value)
             }; }
           });
         }""",
        selected,
    )
    page.set_content((ROOT / page_name).read_text(encoding="utf-8"))
    return page


def main():
    with sync_playwright() as playwright:
        browser_args = {"headless": True}
        if os.getenv("MUSEUM_USE_SYSTEM_CHROMIUM") == "1":
            browser_args.update(executable_path=shutil.which("chromium"), args=["--no-sandbox"])
        browser = playwright.chromium.launch(**browser_args)
        context = browser.new_context(viewport={"width": 375, "height": 812}, accept_downloads=True)
        errors = []
        page = mount_page(context, "curation.html")
        page.on("pageerror", lambda error: errors.append(str(error)))
        assert page.locator(".card").count() == 40
        page.get_by_role("button", name="新着25件だけ").click()
        assert page.locator(".card").count() == 25
        page.get_by_role("button", name="新着25件だけ").click()
        page.get_by_label("展示候補を検索").fill("ミサイル")
        assert page.locator(".card").count() >= 2
        page.get_by_label("展示候補を検索").fill("")
        page.get_by_label("ジャンル").select_option(label="宇宙の常識破り")
        assert page.locator(".card").count() == 11
        page.get_by_label("ジャンル").select_option("all")
        card = page.locator(".card").filter(has=page.get_by_role("heading", name="CIAの機械トンボ"))
        card.get_by_role("button", name="説明・クイズを見る").click()
        card.locator(".answers button").nth(1).click()
        assert card.get_by_text("正解。出典も確かめてみよう。").count() == 1
        card.get_by_role("button", name="収蔵候補に選ぶ").click()
        selected = page.evaluate("localStorage.getItem('curious-museum-curation-v1')")
        assert 'cia-dragonfly' in json.loads(selected)
        restored = mount_page(context, "curation.html", selected=selected)
        restored.on("pageerror", lambda error: errors.append(str(error)))
        restored.get_by_role("button", name="選んだ候補だけ").click()
        assert restored.locator(".card").count() == 1
        with tempfile.TemporaryDirectory() as temp_dir:
            with restored.expect_download() as received:
                restored.get_by_role("button", name="選んだ候補を書き出す").click()
            path = pathlib.Path(temp_dir) / "export.json"
            received.value.save_as(str(path))
            assert [i["id"] for i in json.loads(path.read_text(encoding="utf-8"))["items"]] == ["cia-dragonfly"]
        restored.get_by_role("button", name="選んだ候補だけ").click()
        restored.set_viewport_size({"width": 320, "height": 720})
        assert restored.locator(".card").count() == 40
        assert restored.evaluate("document.documentElement.scrollWidth") <= 320
        home = mount_page(context, "index.html")
        home.on("pageerror", lambda error: errors.append(str(error)))
        assert home.get_by_role("link", name="珍品を発掘する ↗").count() == 1
        assert not errors, errors
        browser.close()
        print("PASS 40 candidates, 25 new, filters, quiz, selection, export, 320px layout")


if __name__ == "__main__":
    main()
