# Kyudo JAPAN 公式サイト

「自分だけの弓道ノート」の公式ポータル、サポート、プライバシーポリシーを
GitHub Pagesで公開する静的Webサイトです。

公開URL：
`https://kyudojapan.net/`

## サイト構成

```text
/
├── CNAME                     # GitHub Pages独自ドメイン
├── index.html                 # 公式ポータル
├── 404.html                   # 独自404ページ
├── support.html               # 使い方・FAQ・問い合わせ・公式X
├── privacy.html               # プライバシーポリシー
├── assets/
│   ├── css/site.css           # 共通デザイン・レスポンシブ・ダークモード
│   ├── js/analytics.js        # GA4共通ローダー・Measurement ID
│   ├── js/site.js             # モバイルナビ・年表示
│   ├── icons/                 # favicon・公式Xブランド素材
│   ├── images/                # アプリ画面・OGP・Xヘッダー
│   └── social/                # 公式SNS投稿・プロフィール用素材
├── releases/
│   ├── index.html             # リリースノート入口
│   └── README.md              # 追加手順
├── qa/screenshots/            # PC・スマートフォン表示確認
├── scripts/
│   └── generate_x_header.swift
├── robots.txt
├── manifest.webmanifest
└── sitemap.xml
```

## 公開前確認

- `index.html`、`support.html`、`privacy.html`、`releases/`が表示できる
- PC、スマートフォン、タブレット幅で文字切れ・横スクロールがない
- キーボード操作でナビゲーション、公式X、サポートへ移動できる
- `prefers-color-scheme: dark`で文字と背景のコントラストを維持する
- `prefers-reduced-motion: reduce`で不要な動きを抑制する
- App Store ConnectのSupport URLとPrivacy Policy URLが公開ページと一致する

## 独自ドメインの切り替え

公開ドメインは `kyudojapan.net` です。DNS側では、apexドメインの既存Aレコードを
GitHub Pagesの次の4レコードへ置き換えます。

```text
185.199.108.153
185.199.109.153
185.199.110.153
185.199.111.153
```

`www` を利用する場合は、`www.kyudojapan.net` のCNAMEを
`okkun1202lindalinda-ship-it.github.io` へ向けます。GitHubのドメイン所有確認用TXTは
GitHub Pages設定画面で表示された値を登録し、確認後も削除しません。

DNS反映後、Repository SettingsのPagesでCustom domainを`kyudojapan.net`へ設定し、
HTTPSが利用可能になってからEnforce HTTPSを有効にします。DNS反映には最大24時間、
HTTPS証明書の発行には追加で時間がかかる場合があります。

## GitHub Actions

`.github/workflows/pages.yml`は、push時に`python3 scripts/check_site.py`を実行し、
成功した静的ファイルだけをGitHub Pagesへ配布します。利用開始時にRepository Settingsの
Pages / Build and deployment / Sourceを`GitHub Actions`へ変更します。

## App Store・Google Playリンクの追加

`index.html` の `#download` 内にある準備中の `span.store-button` を
`a.store-button` へ変更し、各ストアの公開URLを `href` に設定します。

例：

```html
<a class="store-button" href="APP_STORE_URL">App Storeで入手</a>
```

## News・DLC・Subscriptionの追加

- News：トップページの `News` カードを記事一覧へのリンクへ変更します。
- DLC：トップページのDLCカードから、追加機能の紹介・購入案内ページへ接続します。
- Subscription：提供内容が確定した段階で、必要な案内ページへ接続します。
- 公開前の内容は必ず「準備中」または「将来対応」と明示します。

## リリースノートの追加

`releases/README.md` の手順に沿って、バージョン単位のHTMLを追加します。
既存ページへのリンクは相対パスを使い、独自ドメイン直下でも動作する状態を維持します。

## 公式X

公式アカウント：
`https://x.com/MyKyudoNote`

XロゴはX公式ブランドツールキットから取得した素材をそのまま使用しています。
利用時はXのブランドガイドラインに従います。

プロフィール画像：
`assets/social/x-profile-icon-800x800.png`

## Xヘッダー・OGP画像の再生成

ヘッダーは実際のアプリ画面3枚と、青白い霞的背景を組み合わせています。
画像やコピーを更新した場合は、macOSで次を実行します。

```bash
xcrun swiftc -parse-as-library scripts/generate_x_header.swift \
  -o /tmp/generate_x_header
/tmp/generate_x_header .
```

生成物：

- `assets/images/x-header-1500x500.png`
- `assets/images/ogp-1200x630.png`

## 自動確認

ローカルリンク、画像、基本SEO、外部リンクの安全属性、コントラスト、
GA4タグの設置・重複・旧Analyticsコードの残存を確認します。

```bash
python3 scripts/check_site.py
```

## Google Analytics

公式サイトにはGoogle Analytics 4（GA4）を導入しています。

- Measurement ID：`G-K09RH58W5E`
- 設定場所：`assets/js/analytics.js`の`measurementId`
- 読み込み場所：全HTMLページの`<head>`内にある共通ローダー参照

配信時に使うMeasurement IDは`assets/js/analytics.js`の1か所だけで管理します。
IDを変更するときは、このファイルの`measurementId`だけを変更すれば全ページへ反映されます。
READMEに記載したIDも、保守資料として実際の設定と一致するよう更新してください。

新しいHTMLページを追加するときは、階層に合う相対パスで共通ローダーを
`<head>`内へ1回だけ追加します。Google提供のタグやMeasurement IDを各ページへ
直接貼り付けないでください。変更後は`python3 scripts/check_site.py`とLighthouseを実行し、
プライバシーポリシーの説明が実際の計測内容と一致することも確認します。

## v7.1のプライバシー実装

- 練習記録、プロフィール、道具、ノート、設定、画像は端末内へ保存する
- 写真は利用者が写真ライブラリから選択したものだけを使用する
- 写真から読み取るメタデータは撮影日時だけで、位置情報は利用しない
- 現行v7.0はカメラ起動機能と位置情報機能を使用しない
- Flutterアプリ本体には、アカウント、広告、解析SDK、クラッシュ解析SDK、
  開発者サーバー送信はない
- 公式サイトのGA4アクセス解析はアプリ本体と分離している
- CSV・ZIPの書き出しと共有は利用者が操作した場合だけ実行する

将来、Firebase、広告、クラウド同期、ユーザー登録、クラッシュ解析などを
追加した場合は、サイトの説明、プライバシーポリシー、各ストアの
プライバシー回答を同じリリースで更新します。
