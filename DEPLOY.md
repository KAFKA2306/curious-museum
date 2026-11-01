# GitHub Pagesで公開して検証する

対象: [KAFKA2306/curious-museum](https://github.com/KAFKA2306/curious-museum)

## 初回設定

[Pages設定](https://github.com/KAFKA2306/curious-museum/settings/pages)の **Build and deployment → Source** で **GitHub Actions** を選びます。設定画面にアクセスできない場合は、リポジトリの管理権限を確認してください。

公開予定URL: https://kafka2306.github.io/curious-museum/

公開できたかどうかは、[Actions](https://github.com/KAFKA2306/curious-museum/actions/workflows/site.yml)の結果で判断します。URLを設定しただけでは公開完了になりません。

## 自動検証の流れ

`.github/workflows/site.yml` は次の順に実行します。

| ジョブ | 動く条件 | 確認する内容 |
|---|---|---|
| `verify` | PR、mainへのpush、手動実行 | 展示データ、再生成したHTMLとの差分、クイズ・検索、実際のHTTP通信での画面遷移、保存・再読み込み、JSON出力、320px幅 |
| `publish` | mainで `verify` 成功後 | `index.html`、`curation.html`、`.nojekyll` とコミット番号入り `version.txt` をPagesへ公開 |
| `validate-live` | mainで `publish` 成功後 | 公開URLのコミット番号が一致することと、公開サイトで検索・クイズ・保存・再読み込み・JSON出力が動くこと |

PRでは公開しません。公開サイトの動作を確認できたと判断するのは、同じコミットの `validate-live` が成功した場合だけです。

## 手元で確認する

```bash
python -m unittest discover -s tests -p 'test_*.py' -v
python build_curation.py
git diff --exit-code -- curation.html CANDIDATES.md
python -m pip install playwright==1.56.0
python -m playwright install --with-deps chromium
python tests/smoke.py
python tests/site_smoke.py
```

`tests/site_smoke.py` はローカルHTTPサーバーを立ててブラウザを操作します。HTTP通信が制限された環境では失敗するため、最終結果はGitHub Actionsで確認します。

## 失敗した場合

- `verify`: テストログにある展示データ、生成物、画面操作の失敗箇所を修正します。
- `publish`: PagesのSource設定と `github-pages` 環境、Actionsの公開権限を確認します。
- `validate-live`: 公開URL、`version.txt` のコミット番号、ブラウザのエラーを確認します。失敗した実行を成功扱いにしません。

このテストはスマートフォン実機の使いやすさや、候補40件の出典の正確さまでは検証しません。
