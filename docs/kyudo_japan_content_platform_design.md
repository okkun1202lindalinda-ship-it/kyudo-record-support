# Kyudo JAPAN コンテンツ基盤設計書

- 作成日: 2026-07-24
- 状態: 実装前の基本設計
- 対象: `https://kyudojapan.net`
- 公開方針: 無料・広告なし
- コンセプト: 弓道の普及に貢献し、さらなる上達を追求する利用者へ気付きをもたらす

## 1. この設計書の目的

現在の「自分だけの弓道ノート」公式サイトを、アプリの案内だけに留まらない
弓道情報ポータル「Kyudo JAPAN」へ段階的に発展させる。

最初から投稿・コメント・在庫検索まで実装せず、次の順番を守る。

1. 正確で読みやすい公式編集コンテンツを継続公開できる基盤を作る
2. 記事、道具、人物、書籍などの情報を構造化する
3. 検索、RSS、サイトマップ、更新履歴を自動化する
4. 編集・確認・訂正の運用を確立する
5. 運用実績を作ってからユーザー参加型機能へ進む

本設計はWebサイトのみを対象とし、Flutterアプリ本体は変更しない。

## 2. 現状と前提

### 2.1 現在の構成

- GitHub Pagesで公開する静的Webサイト
- HTML、CSS、JavaScriptを直接管理
- Pythonでリンク、SEO、GA4、コントラスト、sitemapを検査
- GitHub Actionsで検査後に公開
- 独自ドメイン、HTTPS、GA4、サイトマップ生成を運用済み
- RSSは未実装
- 記事用テンプレート、共通レイアウト、全文検索は未実装

### 2.2 設計時点のGit状態

- ローカルHEAD: `297fe5a`
- remote main: `fbc9f45`
- ローカルmainはremoteより5コミット遅れている
- ローカルには未コミットの性能改善と接続障害報告書がある

実装前に既存変更を保全し、remote更新と安全に統合する必要がある。
本設計書の作成では、既存HTML、アセット、スクリプト、外部設定を変更しない。

## 3. サービス原則

### 3.1 編集原則

- 弓道の上達、継続、理解に役立つ情報を優先する
- 公式情報、編集部の見解、利用者の感想を明確に区別する
- 事実には出典と確認日を付ける
- 誤りを隠さず、訂正日と訂正内容を残す
- 特定の連盟、団体、メーカーの公式サイトと誤認させない
- 初心者、経験者、指導者のいずれかだけに偏らない
- 年齢、段位、流派、地域による優劣を作らない
- 安全性に関わる内容では自己判断を促さず、指導者や公式情報の確認を案内する

### 3.2 無料・広告なし

- 一般の編集記事、図鑑、検索、RSSは無料で提供する
- バナー広告、行動ターゲティング広告、アフィリエイト順位付けを行わない
- 提供品、取材協力、掲載料がある場合は記事冒頭で開示する
- 掲載料が記事評価、検索順位、おすすめ表示へ影響しない
- 将来の弓具店掲載料は店舗向け業務サービスとして扱い、編集記事と分離する
- 将来のサブスクリプションはアプリ・オンライン機能を対象とし、
  基本的な弓道情報を安易に有料化しない

### 3.3 モデルサイトから採用する考え方

| モデル | 採用する考え方 | 採用しないもの |
|---|---|---|
| Yahoo! JAPAN | 複数分野への入口、更新情報、横断検索 | 広告中心の画面構成 |
| J-カメラ | 店舗横断検索、在庫情報の正規化、条件絞り込み | 販売仲介や販売手数料 |
| Wikipedia | 出典、更新履歴、中立性、訂正可能性 | 誰でも即時公開できる編集方式 |
| Qiita | 経験知の共有、著者表示、タグ、関連コンテンツ | 無審査の公開、評価数だけの順位付け |

## 4. 情報設計

### 4.1 全体構成

```text
Kyudo JAPAN
├── News
├── Articles
├── Equipment
├── Equipment Search
├── Dojo
├── People
├── Books
├── Events
├── Timeline
├── Community
└── Apps
    └── 自分だけの弓道ノート
```

### 4.2 各セクションの役割

| セクション | 役割 | 初期公開 |
|---|---|---|
| News | Kyudo JAPANとアプリの公式告知 | 対象 |
| Articles | 上達、記録、インタビュー、調査報告 | 対象 |
| Equipment | 道具の種類、メーカー、特徴、歴史、レビュー | 試験公開 |
| Equipment Search | 弓具店在庫の横断検索 | 将来 |
| Dojo | 道場の所在地、設備、利用条件、確認日 | 運用確立後 |
| People | 弓道人の経歴、考え方、推薦書籍 | 対象 |
| Books | 弓道関連書籍の紹介・レビュー | 対象 |
| Events | 大会、審査、講習会、イベント | 道具・人物の次 |
| Timeline | 全公開コンテンツの更新履歴 | 自動生成 |
| Community | 投稿、コメント、訂正提案 | 規約・監視整備後 |
| Apps | アプリ紹介、サポート、リリースノート | 現行を継続 |

### 4.3 グローバルナビゲーション

項目を増やしすぎず、PCとモバイルで次を常時表示する。

1. ホーム
2. 読む
3. 道具
4. 人物
5. イベント
6. Apps
7. 検索

「読む」配下にNews、Articles、Booksをまとめる。
Dojo、Timeline、Communityは「もっと見る」またはポータル内の入口から案内する。

## 5. URL設計

URLは英小文字、数字、ハイフンで構成し、公開後は原則として変更しない。
表示上の日本語名称や記事タイトルを変更してもURLは維持する。

```text
/
/news/
/news/{slug}/
/articles/
/articles/{slug}/
/equipment/
/equipment/{category-slug}/
/equipment/{category-slug}/{item-slug}/
/equipment-search/
/dojo/
/dojo/{prefecture-slug}/{dojo-slug}/
/people/
/people/{person-slug}/
/books/
/books/{book-slug}/
/events/
/events/{event-slug}/
/timeline/
/community/
/apps/
/apps/my-kyudo-note/
/search/
```

既存URLは維持する。

```text
/support.html
/privacy
/releases/
/releases/{version}.html
```

### 5.1 URLルール

- 記事URLへ公開日を入れず、内容更新後も同じURLを使う
- 同じ記事のページ分割を避ける
- URLを変更する場合は旧URLから恒久リダイレクトを用意する
- タグ一覧は `/tags/{tag-slug}/`
- 都道府県は内部コード01〜47と英字slugを対応付ける
- canonicalは常に `https://kyudojapan.net` を使用する
- 下書き、確認中、非公開コンテンツはビルド成果物へ出力しない

## 6. コンテンツデータ仕様

記事本文はMarkdown、メタデータはfront matterで管理する。
必須項目がない場合はビルドを失敗させる。

### 6.1 全コンテンツ共通項目

```yaml
---
id: article-test-feedback-2026
type: article
title: テスト参加者から寄せられた声と改善結果
slug: test-feedback-2026
summary: テスト参加者の意見を集計し、改善した点と今後の課題を報告します。
status: draft
published_at: 2026-08-01
updated_at: 2026-08-01
last_verified_at: 2026-08-01
author_id: kyudo-japan-editorial
reviewer_ids:
  - editorial-reviewer
category: reports
tags:
  - アプリ
  - テスト
  - 改善
featured: false
hero_image: /assets/images/articles/test-feedback-2026.webp
hero_alt: テスト結果を集計したグラフ
sources:
  - title: テスト参加者アンケート
    url:
    accessed_at: 2026-07-31
disclosure: 提供・広告・アフィリエイトはありません。
rights:
  image: original
  text: kyudo-japan
---
```

### 6.2 共通項目の規則

| 項目 | 規則 |
|---|---|
| `id` | 一度公開したら変更しない内部識別子 |
| `type` | 許可されたコンテンツ種別だけを使用 |
| `slug` | 同じ種別内で一意 |
| `summary` | 検索結果とOGP説明に使える簡潔な文章 |
| `status` | `draft`、`review`、`scheduled`、`published`、`archived` |
| `published_at` | 初回公開日。更新時に変更しない |
| `updated_at` | 本文や重要情報を変更した日 |
| `last_verified_at` | 外部情報を最後に確認した日 |
| `sources` | 事実確認に使用した一次情報を優先 |
| `disclosure` | 提供、取材協力、掲載料、利益相反を表示 |
| `rights` | 文章・画像・書影の利用根拠 |

### 6.3 コンテンツ種別

#### News

追加項目:

- `importance`: normal / important
- `expires_at`: 期限付き告知だけ設定
- `related_app_version`
- `related_content_ids`

#### Articles

追加項目:

- `series`
- `audiences`: beginner / intermediate / advanced / instructor
- `practice_topics`
- `related_app_features`
- `methodology`: 調査記事の場合

#### Books

追加項目:

- 書名
- 著者
- 出版社
- ISBN
- 対象版・発行年
- 想定読者
- レビュー担当者
- 書影利用許可
- 引用箇所と出典ページ
- 購入リンクの種類

購入リンクは出版社、著者、一般書店の通常リンクとし、アフィリエイトを使用しない。
「真由の本」は正式な書名、著者、ISBN、対象版、書影利用条件を確認するまで公開しない。

#### Equipment

事実情報とレビューを別セクションとして保存する。

- `manufacturer_id`
- `category`
- `model_name`
- `status`: current / discontinued / historical
- `release_period`
- `materials`
- `specifications`
- `official_sources`
- `history_sources`
- `review_summary`
- `reviewer_ids`
- `provided_sample`

メーカー提供品の場合でも評価内容への関与を認めず、その事実を表示する。

#### People

- `display_name`
- `name_reading`
- `consent_status`
- `consent_record_id`
- `portrait_rights`
- `rank_as_of`
- `titles_as_of`
- `career_summary`
- `philosophy`
- `recommended_book_ids`
- `interviewed_at`
- `transcript_approved_at`

段位、称号、所属、経歴には確認日を付ける。未成年者は保護者同意を必須とする。

#### Events

- `event_type`: tournament / examination / seminar / trial / other
- `organizer`
- `starts_at`
- `ends_at`
- `prefecture_code`
- `venue_name`
- `eligibility`
- `application_deadline`
- `official_url`
- `status`: scheduled / postponed / cancelled / completed
- `last_verified_at`

開催可否、申込条件、締切は主催者の公式情報を正とする。
イベントページから公式情報へ必ずリンクする。

#### Dojo

- `operator`
- `prefecture_code`
- `municipality`
- `public_address`
- `public_access`
- `facilities`
- `usage_requirements`
- `opening_hours`
- `common_name`
- `official_url`
- `contact_policy`
- `last_verified_at`
- `correction_contact`

公開施設であることと掲載許可を確認する。
個人宅、非公開施設、会員限定施設の情報を推測で掲載しない。
通称は「通称」と明記し、差別的・侮蔑的表現を掲載しない。

#### Shops・Inventory

弓具店は将来の在庫検索に備え、Equipmentとは別の内部エンティティとして管理する。

- 店舗ID
- 店舗名
- 所在地
- 営業時間
- 取扱分野
- 取扱メーカー
- 通販可否
- 公式URL
- 掲載契約状態
- 在庫更新日時
- 在庫取得方式

在庫情報には必ず更新日時を表示し、最終的な在庫と価格は店舗へ確認するよう案内する。

## 7. 編集・公開・訂正フロー

```text
企画
  ↓
取材・資料収集
  ↓
執筆
  ↓
事実確認
  ↓
権利・同意確認
  ↓
校正
  ↓
プレビュー
  ↓
公開
  ↓
定期確認・訂正・アーカイブ
```

### 7.1 公開条件

- 必須メタデータが揃っている
- 事実と意見が区別されている
- 出典URLと確認日がある
- 人物・道場・店舗は必要な同意がある
- 画像の利用根拠とaltがある
- 提供、協力、掲載料が開示されている
- 誤認を招く「公式」「公認」表現がない
- スマートフォン、キーボード、読み上げで確認済み
- sitemap、RSS、検索インデックスへ正しく反映される

### 7.2 訂正方針

- 誤りの連絡窓口を全記事から確認できるようにする
- 軽微な誤字は `updated_at` だけを更新する
- 意味が変わる訂正は記事末尾へ訂正履歴を表示する
- 重大な誤情報は一時非公開にできる
- 削除して終わらせず、必要に応じて訂正告知を出す
- 外部情報が古くなった場合は「最終確認日」を目立つ位置へ表示する

### 7.3 定期確認の目安

| 種別 | 確認頻度 |
|---|---|
| News | 期限到来時 |
| Articles | 年1回または前提変更時 |
| Books | 新版確認時 |
| Equipment | 6〜12か月ごと |
| People | 本人から更新連絡を受けた時 |
| Events | 公開時、締切前、開催直前 |
| Dojo | 6か月ごと |
| Shops | 3〜6か月ごと |
| Inventory | 店舗データ更新ごと |

## 8. 初期記事企画

### 8.1 テスト参加者フィードバック結果報告

目的:

- 利用者の意見をどのように改善へ反映したか透明にする
- アプリの長所だけでなく未解決課題も共有する
- テスト参加への感謝を示す

構成:

1. テストの目的と期間
2. 参加人数と属性の集計
3. 実施した操作・質問
4. 良かった点
5. 困った点
6. 改善した内容
7. 今後対応する内容
8. 対応しない内容と理由
9. 集計方法と限界

個人が推測できる少人数区分、自由記述、端末情報は匿名化・要約する。
実際の人数、割合、発言を確認せず作らない。

### 8.2 私の「弓道ノート」の使い方

年代だけで人物を分類せず、弓歴、練習頻度、目的、記録方法の違いを中心に紹介する。

共通質問:

- 弓道歴と現在の稽古環境
- 何を記録しているか
- 稽古後に何を見返すか
- 道具の変化をどう残すか
- 記録から得た気付き
- 初心者へすすめる使い方
- 改善してほしい点

年代は本人同意のある幅広い区分で表示し、生年月日を収集しない。

### 8.3 弓道関連書籍レビュー

評価軸:

- 想定読者
- 主なテーマ
- 読みやすさ
- 稽古での活用方法
- 印象に残った点
- 他の資料と併読する際の位置付け
- レビュー担当者の経験と視点

長い引用、本文の代替になる要約、許可のない書影転載を避ける。

### 8.4 道具図鑑の試験記事

最初は1カテゴリ・1〜3件でデータ項目と表示方法を検証する。
メーカー間の優劣ランキングは行わず、用途、特徴、確認可能な仕様、利用者の感想を分離する。

### 8.5 弓道人インタビュー

経歴紹介だけでなく、考え方、失敗、継続方法、推薦書籍、記録方法を中心にする。
公開前に本人へ原稿確認を依頼し、承認日を記録する。

## 9. 技術設計

### 9.1 採用方針

段階移行先としてEleventyを採用候補の第一とする。

理由:

- 現在のHTML、CSS、JavaScriptを再利用しやすい
- Markdown、front matter、レイアウト、コレクションを扱える
- 静的ファイルを生成するためGitHub Pagesを継続できる
- サーバーやデータベースを追加せず初期コンテンツを運用できる
- RSSと一覧ページを同じコンテンツデータから生成できる

2026-07-24の確認時点でEleventy公式の安定版はv3系で、v4はプレリリースだった。
初期実装では安定版のメジャーバージョンと依存関係をlock fileへ固定する。

### 9.2 検索

Pagefindをビルド後検索の第一候補とする。

- 静的サイト生成後のHTMLから検索インデックスを生成
- 検索用サーバーや外部検索サービスが不要
- `lang="ja"`を使用し、日本語の単語分割へ対応
- 記事種別、タグ、都道府県、目的をフィルターとして保持
- 本文だけを `data-pagefind-body` で索引対象にする
- ナビゲーション、フッター、Cookie案内は索引対象外
- 検索ページを開くまで検索用JavaScriptと索引を遅延読み込みする

初期対象:

- News
- Articles
- Equipment
- People
- Books
- Events
- Dojo
- Support
- Release Notes

除外対象:

- 404
- Privacy
- 下書き
- アーカイブ済みの非公開情報
- 重複互換ページ

日本語の表記揺れ、送り仮名、旧字体、メーカー名の別表記は実データで評価し、
必要なら同義語フィールドを追加する。

### 9.3 RSS

`/feed.xml` へRSS 2.0を生成する。

対象:

- News
- Articles
- Books
- Equipment
- People
- AppsのRelease Notes

フィード項目:

- title
- link
- guid
- description
- pubDate
- updated date
- author
- category

全文ではなく概要と記事リンクを配信する。
将来、利用要望があればAtomまたはJSON Feedを追加する。

### 9.4 メールマガジン

初期はRSSと月例記事を先に運用し、メールアドレスを収集しない。
メールマガジン開始前に次を確定する。

- 配信事業者
- 同意取得
- 配信停止
- メールアドレスの保管場所
- 保存期間
- プライバシーポリシー
- 誤配信対応

月例構成:

1. 今月の新着記事
2. 道具・人物・書籍の追加
3. アプリの更新内容
4. 訂正・重要なお知らせ
5. 翌月の予定

### 9.5 sitemap自動生成

既存の手入力一覧から、ビルド済み公開コレクションを唯一の情報源とする方式へ移行する。

- `published`だけを掲載
- canonical URLを使用
- `lastmod`は`updated_at`
- 現行priority方針を種別ごとに保持
- URL重複をビルドエラーにする
- XML Sitemap Protocol準拠
- UTF-8、2スペースインデント
- draft、noindex、404、互換重複URLは除外

移行完了後、`scripts/generate_sitemap.py`は生成元ではなく出力検査へ役割を変更する。
移行期間中は新旧2系統でsitemapを生成しない。

### 9.6 構造化データ

| ページ | Schema.org |
|---|---|
| トップ | Organization、WebSite |
| News | NewsArticle |
| Articles | Article |
| Books | Book、Review |
| Equipment | ProductまたはArticleを内容に応じて選択 |
| People | Person |
| Events | Event |
| Dojo | PlaceまたはSportsActivityLocation |
| 全詳細ページ | BreadcrumbList |

実態のない価格、在庫、評価点、主催者情報を構造化データへ入れない。

### 9.7 推奨ディレクトリ

```text
/
├── src/
│   ├── _data/
│   │   ├── site.json
│   │   ├── authors.json
│   │   ├── manufacturers.json
│   │   └── prefectures.json
│   ├── _includes/
│   │   ├── layouts/
│   │   └── components/
│   ├── news/
│   ├── articles/
│   ├── equipment/
│   ├── people/
│   ├── books/
│   ├── events/
│   ├── dojo/
│   ├── apps/
│   ├── search/
│   ├── feed.njk
│   └── sitemap.njk
├── public/
│   ├── assets/
│   ├── CNAME
│   ├── robots.txt
│   └── manifest.webmanifest
├── scripts/
│   ├── check_site.py
│   └── validate_content.py
├── _site/                 # ビルド成果物。Git管理しない
├── eleventy.config.js
├── pagefind.yml
├── package.json
└── package-lock.json
```

### 9.8 ビルド

```text
Markdown・データ
        ↓
Eleventy
        ↓
静的HTML (_site)
        ↓
Pagefind検索索引
        ↓
Python検査
        ↓
GitHub Pages artifact
```

GitHub Actionsの想定:

1. checkout
2. Node.jsの安定したLTSメジャーを固定
3. `npm ci`
4. `npm run build`
5. `python3 scripts/check_site.py --root _site`
6. sitemap、RSS、Pagefind索引を検査
7. `_site`だけをPages artifactとしてアップロード
8. deploy

`docs/`、`outputs/`、`src/`、`node_modules/`、設定ファイルは公開artifactへ含めない。
公開検査はリポジトリ全体ではなく、実際に配布する`_site`だけを対象にする。

### 9.9 段階移行

一度に全ページを移行しない。

#### 技術検証

- remote最新から独立した作業ブランチまたはworktreeを作成
- 現行アセットをpass-through copy
- `/articles/`と非公開のサンプル記事1件だけを生成
- RSS、sitemap、検索をローカルで検証
- 現行トップ、Support、Privacy、Release Notesの出力差分を確認

#### 共通レイアウト移行

- head
- GA4ローダー
- header
- navigation
- footer
- OGP
- JSON-LD

#### 現行ページ移行

- Top
- Support
- Privacy
- Release Notes
- 404

#### コンテンツ公開

- News
- Articles
- Books
- Equipment
- People

## 10. 品質要件

### 10.1 アクセシビリティ

- 見出し階層を維持
- 色だけで状態を表さない
- キーボードだけで検索・フィルター・メニューを操作可能
- 画像に適切なalt
- 表は見出しセルを設定
- `prefers-reduced-motion`を維持
- Light/Dark ModeでWCAG AA以上
- 検索結果件数と更新を読み上げ可能にする

### 10.2 パフォーマンス

- 記事本文の表示に検索用JavaScriptを必須としない
- Pagefindは検索操作時に読み込む
- 画像へwidth、height、srcset、WebPまたはAVIFを用意
- 外部埋め込みを原則使用しない
- SNS投稿や動画はクリック後読み込みを検討
- 広告スクリプトを追加しない
- GA4以外の計測SDKは目的・プライバシーを確認してから追加

目標:

- Lighthouse Accessibility: 100
- Lighthouse Best Practices: 100
- Lighthouse SEO: 100
- モバイルLCP: 2.5秒以下を目標
- CLS: 0.1以下

### 10.3 自動検査

- 必須メタデータ
- ID、slug、canonicalの重複
- 公開日・更新日の形式
- 下書きの公開混入
- 内部リンク切れ
- 外部出典URL
- 画像、alt、寸法
- OGP、Twitter Card、JSON-LD
- sitemapとRSSのXML
- 検索インデックス生成
- GA4重複
- Mixed Content
- 古い公開URLからの互換性

## 11. Community開始条件

コメント欄やユーザー投稿は、次が揃うまで開始しない。

- 利用規約
- 投稿ガイドライン
- プライバシーポリシー更新
- 著作権と利用許諾
- 通報・削除・異議申立て
- 投稿前審査または公開後監視
- スパム、荒らし、なりすまし対策
- 名誉毀損、個人情報、危険行為への対応
- 未成年者への配慮
- アカウント削除とデータ削除
- 運営者不在時の非公開手順

用語辞典のコメント欄は自由掲示板にせず、「補足」「出典付き訂正」「地域差」の
3種類から投稿目的を選び、公開前審査を行う。

## 12. 弓具店在庫検索の設計原則

### 12.1 ビジネス原則

- 販売手数料を受け取らない
- 店舗への遷移・問い合わせまでを提供する
- 掲載料を検索順位へ反映しない
- 掲載店舗と未契約店舗を誤認させない
- 編集レビューと店舗情報を別データとして管理する
- 在庫、価格、営業情報の更新日時を明示する

### 12.2 技術的な開始条件

- メーカー・商品名の正規化
- 店舗IDと商品IDの共通仕様
- CSVまたはAPIの取込仕様
- 差分更新
- 重複商品の統合
- 在庫の有効期限
- 店舗管理画面
- 誤情報の訂正
- 障害時の古い在庫表示停止
- 利用規約、店舗契約、プライバシーの確認

GitHub Pagesだけでは更新頻度、認証、店舗管理へ対応できないため、
在庫検索開始時にバックエンドを別途設計する。

## 13. 展開ロードマップ

### Phase 0: アプリ正式リリース

- App Store・Google Playの実公開状態を確認
- 公式サイト、Support、Privacy、Release Notesを同期

### Phase 1: Kyudo JAPAN開始

- コンテンツ基盤
- News、Articles、Books
- 初期記事3〜5本
- RSS
- sitemap自動生成
- 全文検索

### Phase 2: 図鑑・人物

- Equipment
- People
- メーカー・著者・人物のデータ整備
- 訂正・最終確認日の運用

### Phase 3: Events・Dojo

- 都道府県・目的別フィルター
- 公式情報へのリンク
- 情報の期限切れ表示
- 訂正受付

### Phase 4: ユーザー参加

- 投稿規約
- アカウント
- コメント
- 用語辞典への補足
- レビュー
- モデレーション

### Phase 5: 弓具店在庫検索

- 店舗契約
- 商品・在庫データ
- 横断検索
- 更新監視

### Phase 6: オンライン・Subscription

- アプリ同期やオンライン機能
- 提供条件
- 価格
- 解約・返金
- 利用規約
- Privacyとの整合

## 14. 実装着手前の決定事項

次の内容は管理者確認後に確定する。

1. 最初に公開する3〜5記事
2. 「真由の本」の正式情報と書影利用条件
3. 編集責任者と事実確認者
4. 人物インタビューの同意書
5. メーカー・店舗から提供を受ける場合の開示文
6. 訂正窓口
7. 記事著者の実名・ハンドルネーム方針
8. Eleventy技術検証の結果
9. Pagefind日本語検索の実データ評価
10. メールマガジン開始時期

## 15. 最初の実装単位

最初の実装は「公開を変えない技術検証」とする。

成果物:

- Eleventyの最小構成
- 現行CSS・画像の再利用
- `/articles/`一覧
- 非公開サンプル記事1件
- RSS
- 自動sitemap
- Pagefind検索
- `_site`向け検査
- GitHub Actionsのプレビュー用ビルド
- 移行前後のLighthouse比較

この技術検証が成功し、現行ページのURL、デザイン、SEO、GA4、表示速度を
維持できることを確認してから公開移行へ進む。

## 16. 参考資料

- Eleventy公式ドキュメント: https://www.11ty.dev/docs/
- Eleventy RSS公式ドキュメント: https://www.11ty.dev/docs/plugins/rss/
- Pagefind公式ドキュメント: https://pagefind.app/docs/
- Pagefind日本語検索: https://pagefind.app/docs/multilingual/
- XML Sitemap Protocol: https://www.sitemaps.org/protocol.html
