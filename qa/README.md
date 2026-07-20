# 表示確認

2026年7月20日にローカルHTTP配信で確認しました。

- `screenshots/portal-desktop-1440x900.png`：PC、1440 × 900
- `screenshots/portal-mobile-390x844.png`：スマートフォン、390 × 844
- `screenshots/support-ratio-before-desktop.png`：Support画像の修正前
- `screenshots/support-ratio-after-desktop.png`：Support画像の修正後、PC 1440 × 900
- `screenshots/support-ratio-after-mobile.png`：Support画像の修正後、スマートフォン 390 × 844
- `screenshots/support-ratio-after-tablet.png`：Support画像の修正後、タブレット 820 × 1180

追加確認：

- タブレット 820 × 1180
- 横スクロールなし
- モバイル／タブレットのナビゲーション開閉
- Support、Privacy、Release Notesのローカルリンク
- 画像読み込み
- 全画像の元画像比率と表示比率が一致
- Supportスクリーンショットは `height: auto` / `object-fit: contain`
- ブラウザコンソールエラーなし

ダークモードは共通CSSの `prefers-color-scheme: dark`、
Reduce Motionは `prefers-reduced-motion: reduce` で対応しています。
