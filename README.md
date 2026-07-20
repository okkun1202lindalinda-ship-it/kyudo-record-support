# 自分だけの弓道ノート 公式サイト

「自分だけの弓道ノート」の公式ポータル、サポート、プライバシーポリシーを
GitHub Pagesで公開する静的Webサイトです。

公開URL：
`https://okkun1202lindalinda-ship-it.github.io/kyudo-record-support/`

## サイト構成

```text
/
├── index.html                 # 公式ポータル
├── support.html               # 使い方・FAQ・問い合わせ・公式X
├── privacy.html               # プライバシーポリシー
├── assets/
│   ├── css/site.css           # 共通デザイン・レスポンシブ・ダークモード
│   ├── js/site.js             # モバイルナビ・年表示
│   ├── icons/                 # favicon・公式Xブランド素材
│   └── images/                # アプリ画面・OGP・Xヘッダー
├── releases/
│   ├── index.html             # リリースノート入口
│   └── README.md              # 追加手順
├── qa/screenshots/            # PC・スマートフォン表示確認
├── scripts/
│   └── generate_x_header.swift
├── robots.txt
└── sitemap.xml
```

## 公開前確認

- `index.html`、`support.html`、`privacy.html`、`releases/`が表示できる
- PC、スマートフォン、タブレット幅で文字切れ・横スクロールがない
- キーボード操作でナビゲーション、公式X、サポートへ移動できる
- `prefers-color-scheme: dark`で文字と背景のコントラストを維持する
- `prefers-reduced-motion: reduce`で不要な動きを抑制する
- App Store ConnectのSupport URLとPrivacy Policy URLが公開ページと一致する

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
- Subscription：Subscriptionカードから、対象者、機能、料金表、規約へ接続します。
- 公開前の内容は必ず「準備中」または「将来対応」と明示します。

## リリースノートの追加

`releases/README.md` の手順に沿って、バージョン単位のHTMLを追加します。
既存ページへのリンクは相対パスを使い、GitHub Pagesの
`/kyudo-record-support/` 配下でも動作する状態を維持します。

## 公式X

公式アカウント：
`https://x.com/MyKyudoNote`

XロゴはX公式ブランドツールキットから取得した素材をそのまま使用しています。
利用時はXのブランドガイドラインに従います。

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

ローカルリンク、画像、基本SEO、外部リンクの安全属性、コントラストを確認します。

```bash
python3 scripts/check_site.py
```

## v7.0のプライバシー実装

- 練習記録、プロフィール、道具、ノート、設定、画像は端末内へ保存する
- 写真は利用者が写真ライブラリから選択したものだけを使用する
- 写真から読み取るメタデータは撮影日時だけで、位置情報は利用しない
- 現行v7.0はカメラ起動機能と位置情報機能を使用しない
- アカウント、広告、解析SDK、クラッシュ解析SDK、開発者サーバー送信はない
- CSV・ZIPの書き出しと共有は利用者が操作した場合だけ実行する

将来、Firebase、広告、クラウド同期、ユーザー登録、クラッシュ解析などを
追加した場合は、サイトの説明、プライバシーポリシー、各ストアの
プライバシー回答を同じリリースで更新します。
