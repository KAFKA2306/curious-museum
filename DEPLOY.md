# GitHub Pagesの公開と検証

公開対象: [KAFKA2306/curious-museum](https://github.com/KAFKA2306/curious-museum)

## 初回のPages設定

リポジトリの **Settings → Pages → Build and deployment → Source** で **GitHub Actions** を選びます。公開権限や組織ポリシーによっては、この操作をリポジトリ管理者が行う必要があります。

公開URLの想定値は https://kafka2306.github.io/curious-museum/ です。URLが存在することや公開できたことは、GitHub Actionsで検証するまで確定しません。

## .github/workflows/site.yml

1. **verify（PRとmain）**: Pythonの展示データ検証、候補40件からのHTML再生成一致、従来のDOMテストを実行します。
2. **verify（実HTTP）**: PlaywrightがローカルHTTPサーバー経由で2ページを開き、画面遷移・40件の表示・25件の新着絞り込み・検索・クイズ・選択・本物のlocalStorageへの保存と再読み込み・JSON書き出し・320px幅を検査します。
3. **publish（mainのみ）**: verifyが成功した場合だけ、GitHub Pagesへ `index.html`、`curation.html`、`.nojekyll` と `version.txt` を公開します。version.txtには公開対象のGitコミットSHAを入れます。
4. **validate-live（mainのみ）**: デプロイ完了後、公開URLの `version.txt` とGitコミットSHAの一致を確認し、**実際の公開サイト**に対して手順2と同じPlaywright操作を実行します。404、旧版、画面操作の不具合があればActionを失敗にします。

PRでは公開しません。実際のPagesへのデプロイと公開後検査はmainのみです。公開サイトの正常性をCIの単体テスト成功で代用しません。

## 開発時の検査

```bash
python -m unittest discover -s tests -p 'test_*.py' -v
python build_curation.py
git diff --exit-code -- curation.html CANDIDATES.md
python -m pip install playwright==1.56.0
python -m playwright install --with-deps chromium
python tests/smoke.py
python tests/site_smoke.py
```

`tests/site_smoke.py` はHTTP通信が制限された環境では動きません。GitHub Actions上のローカルHTTP検証と、本番デプロイ後の公開URL検証を最終的な実行証拠にします。

## 失敗時の対処

- `verify` が失敗: データや生成物、ブラウザ操作の差分を修正。公開は実行しません。
- `publish` が失敗: PagesのSourceがGitHub Actionsか、github-pages環境とPages権限を確認。
- `validate-live` が失敗: Actionは失敗のままにし、公開URL・version.txtのコミット・ブラウザ操作ログを見て原因を特定。
- `validate-live` が成功して初めて、**その実行のコミットが公開URLで動作した**と記録します。

なお、本検証はスマートフォン実機での操作性や、出典40件の記述をすべて確認したことを証明するものではありません。
