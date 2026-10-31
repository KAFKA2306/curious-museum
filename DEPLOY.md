# GitHubへの登録と公開

登録先の [KAFKA2306/curious-museum](https://github.com/KAFKA2306/curious-museum) は作成済みです。2026年10月31日の確認時点では空の状態で、GitHub Pagesの公開は未確認です。

## 1. ファイルを登録する

ZIPを展開し、`index.html` があるディレクトリで次を実行します。Gitの認証設定が必要です。

```bash
git init -b main
git add .
git commit -m "feat: start curious museum v0.4"
git remote add origin https://github.com/KAFKA2306/curious-museum.git
git push -u origin main
```

上の方法はGitHubにまだコミットがない場合の手順です。登録済みのリポジトリには、既存履歴を確認してからPRで変更を取り込みます。

公開前に、秘密情報や個人情報が含まれていないか確認します。

## 2. GitHub Pagesを設定する

`Settings > Pages > Build and deployment > Source` で `GitHub Actions` を選びます。`main` へのpush時に `.github/workflows/site.yml` がデータ検証・ブラウザ操作テストを実行し、成功後に静的ページを公開する設計です。PRでは検証だけを行います。

予定URL: https://kafka2306.github.io/curious-museum/

このURLは**公開完了を示すものではありません**。Actionsのデプロイが成功したら、実際にページを開いて遊べるか確認します。

## 3. 手元で検証する

```bash
python -m unittest discover -s tests -p 'test_*.py' -v
python build_curation.py
git diff --exit-code -- curation.html CANDIDATES.md
python -m pip install playwright==1.56.0
python -m playwright install chromium
python tests/smoke.py
```

展示候補の文章や出典を直したときは `exhibit_candidates.json` を編集してから `python build_curation.py` を実行します。生成されたHTMLと出典一覧は一緒にコミットしてください。

画面デザインの正式な共有UIへの移行では [KAFKA2306/design](https://github.com/KAFKA2306/design) の同期契約を使います。現在の画面は独立した試作版です。
