# 自分だけの弓道ノート サポートサイト公開手順

このフォルダは、そのままGitHub Pagesへ公開できる静的Webサイトです。
v7.0の正式名称、機能、使用方法、FAQ、問い合わせ先、プライバシーポリシーを
掲載しています。

## 収録ファイル
- `index.html`：公式トップページ
- `support.html`：使い方・FAQ・問い合わせ
- `privacy.html`：プライバシーポリシー
- `styles.css`：共通デザイン

## 公開前確認

- `support.html`と`privacy.html`の問い合わせ先でメールを受信できる
- 3ページすべてに旧アプリ名が残っていない
- GitHub Pages上でナビゲーションとメールリンクが動作する
- App Store ConnectのSupport URLとPrivacy Policy URLが公開ページと一致する

## v7.0のプライバシー実装

- 練習記録、プロフィール、道具、ノート、設定、画像は端末内へ保存する
- 写真は利用者が写真ライブラリから選択したものだけを使用する
- 写真から読み取るメタデータは撮影日時だけで、位置情報は利用しない
- 現行v7.0はカメラ起動機能と位置情報機能を使用しない
- アカウント、広告、解析SDK、クラッシュ解析SDK、開発者サーバー送信はない
- CSV・ZIPの書き出しと共有は利用者が操作した場合だけ実行する

## GitHub Pagesで公開する手順
1. GitHubへログインします。
2. 右上の `+` → `New repository` を選びます。
3. Repository name に `kyudo-record-support` と入力します。
4. Publicを選び、リポジトリを作成します。
5. `Add file` → `Upload files` を選びます。
6. このフォルダ内の4ファイルをアップロードします。
7. `Commit changes` を押します。
8. リポジトリの `Settings` を開きます。
9. 左側の `Pages` を開きます。
10. Sourceを `Deploy from a branch` にします。
11. Branchを `main`、フォルダを `/(root)` にしてSaveします。
12. 数分後、Pages画面に公開URLが表示されます。

## App Store Connectへ入力するURL
サポートURL：`https://<GitHubユーザー名>.github.io/kyudo-record-support/support.html`

プライバシーポリシーURL：`https://<GitHubユーザー名>.github.io/kyudo-record-support/privacy.html`

トップページ：`https://<GitHubユーザー名>.github.io/kyudo-record-support/`

既存のApp Store Connect設定を壊さないため、Repository名とURLパスの
`kyudo-record-support`は維持します。公開前に実際のGitHubユーザー名を確認してください。

## 注意
この文面は、現在のアプリが「外部サーバー送信なし・広告なし・解析SDKなし・アカウントなし」であることを前提にしています。将来、Firebase、広告、クラウド同期、ユーザー登録、クラッシュ解析などを追加した場合は、プライバシーポリシーとApp Store ConnectのApp Privacy回答を更新してください。
