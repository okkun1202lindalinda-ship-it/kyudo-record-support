# リリースノート追加手順

1. `v7-1-0.html` のように、バージョン単位のHTMLをこのフォルダへ追加します。
2. `index.html` のリリース一覧へ日付、バージョン、概要、リンクを追加します。
3. 重要な更新はトップページの `News` または `Release Notes` にも反映します。
4. `scripts/generate_sitemap.py`の`SITEMAP_ENTRIES`へ公開URL、HTMLファイル、
   `lastmod`、`priority`を追加し、リポジトリ直下で生成スクリプトを実行します。
5. 公開前にローカル表示、リンク、スマートフォン表示を確認します。

```bash
python3 scripts/generate_sitemap.py
python3 scripts/check_site.py
```

リリースページでは、公開済みの機能だけを記載します。将来予定の内容は
トップページのロードマップへ分け、リリース済みと誤認されないようにします。
