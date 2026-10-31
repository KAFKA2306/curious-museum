# GitHubへの登録と公開

登録先の [KAFKA2306/curious-museum](https://github.com/KAFKA2306/curious-museum) は作成済みです。2026年10月31日の確認時点では空の状態で、GitHub Pagesの公開は未確認です。

## 1. GitHubで更新する

[リポジトリ](https://github.com/KAFKA2306/curious-museum)には試作版v0.4を登録済みです。今後の変更は作業ブランチからPRを作り、データ・画面の検証後にmainへ反映します。

候補を追加・修正する場合は `exhibit_candidates.json` を編集し、`python build_curation.py` で発掘室と候補一覧を再生成してください。公開前に秘密情報と個人情報がないことを確認します。

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
