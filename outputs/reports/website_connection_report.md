# Kyudo JAPAN公式サイト 接続障害調査報告書

## 1. 結論

利用中Wi-Fiのプライマリ再帰DNSに、**旧IPと新IPを交互に返すキャッシュ不整合**があることを特定した。接続障害が発生したiPhoneも同じWi-Fiを使用していたことをユーザーへ確認したため、このDNS不整合が接続障害の直接原因である。

公式の権威DNSはGitHub Pages向けの正しいAレコードを返している。しかし、調査に使用したMacのプライマリ再帰DNS `2001:a7ff:5f01::a` は、同じ `kyudojapan.net` に対して次の2種類の応答を交互に返した。

- 正常: GitHub Pagesの4アドレス
- 異常: 移行前の旧アドレス `150.95.255.38`

旧アドレスへHTTPS接続すると8秒でタイムアウトし、HTTPステータスも取得できなかった。したがって、DNS問い合わせ時にどちらのキャッシュへ当たるかによって、正常表示と接続失敗が入れ替わる状態を実測で再現できた。

GitHub Pages、最新デプロイ、現在のGitHub Status、証明書、CDN、サイトソースには、現時点で接続障害を起こす異常は確認されなかった。

## 2. 発生日・調査日時

- 発生日: 2026-07-23（申告日。iPhoneで確認。正確な発生開始時刻は未確認）
- 関連するDNS移行: 2026-07-21に旧Aレコード `150.95.255.38` からGitHub Pages向けAレコードへ変更
- 調査日時: 2026-07-23 10:15〜10:45 JSTを中心に実施
- 調査対象: `https://kyudojapan.net`

## 3. 再現有無

**再現あり。**

### DNS問い合わせの再現結果

Macの既定DNSを使用してAレコードを20回問い合わせた結果:

- 12回: `185.199.108.153`〜`185.199.111.153` の正常な4件
- 8回: 旧IP `150.95.255.38`

`www.kyudojapan.net` を10回問い合わせた結果:

- 7回: 正しいCNAMEとGitHub Pagesの4アドレス
- 3回: 旧IP `150.95.255.38`

DNSサーバーを個別に指定した結果:

| 問い合わせ先 | apexの結果 | 判定 |
|---|---:|---|
| `2001:a7ff:5f01::a` | 12回中5回が旧IP、7回が正常 | 不整合あり |
| `2001:a7ff:5f01:1::a` | 12回すべて正常 | 正常 |
| `192.168.11.1` | 12回すべて正常 | 正常 |
| Cloudflare `1.1.1.1` | 正常 | 正常 |
| Google `8.8.8.8` | 正常 | 正常 |
| Quad9 `9.9.9.9` | 正常 | 正常 |

異常応答には再帰DNSからTTL 300秒の旧IPが含まれていた。権威DNS4台には同じ旧IPやワイルドカードレコードは存在しないため、ドメイン側の現在設定ではなく、再帰DNS側に残った古いキャッシュである。

申告された実際の症状はiPhoneで発生し、発生時は調査Macと同じWi-Fiを使用していた。MacのDNS試験は同じWi-Fi環境から利用回線側DNSの不整合を測定したものであり、iPhoneの症状と直接整合する。

### 旧IPでの接続再現

- HTTP: 応答途中に接続リセットが発生
- HTTPS: 8秒で接続タイムアウト
- HTTPSステータス: `000`

この結果は、利用者が旧IPを受け取った場合の「ページを開けない」症状と一致する。

## 4. 原因分類

| 分類 | 判定 | 根拠 |
|---|---|---|
| DNS | **原因確定** | 同じWi-Fiのプライマリ再帰DNSが新旧IPを交互に返した |
| GitHub Pages | 正常 | `built`、Custom Domain正常、最新Deploy成功 |
| SSL | 正常 | 証明書検証成功、TLS 1.3、期限内 |
| CDN | 正常 | Fastlyの全4配信先がHTTP 200 |
| ブラウザ | 原因ではない | Mac Safariで安全な接続と表示を確認 |
| ネットワーク | **影響あり** | 利用中ネットワークのプライマリ再帰DNSに限定して不整合 |
| ソースコード | 原因なし | HTTP資源やMixed Contentなし、ローカル検査成功 |
| 外部要因 | **該当** | 利用回線側の再帰DNSキャッシュ |
| 再現せず | 非該当 | DNS問い合わせと旧IP接続で再現済み |

## 5. DNS調査

### 権威DNS

- ネームサーバー: `01.dnsv.jp`〜`04.dnsv.jp`
- NS TTL: 86400秒
- SOA refresh: 3600秒
- SOA retry: 900秒
- SOA negative TTL: 300秒
- 4台の権威DNSで回答は一致

### apex Aレコード

TTL 3600秒で、4台すべてが次を返した。

```text
185.199.108.153
185.199.109.153
185.199.110.153
185.199.111.153
```

これはGitHub公式ドキュメントに掲載されたGitHub Pages用Aレコードと一致する。

### AAAAレコード

- apex: 未設定
- `www`: CNAME先を含め、ネイティブAAAA応答なし

AAAAがないこと自体は今回の新旧Aレコード混在の原因ではない。ただし、GitHub PagesはIPv6用AAAAレコードも公式に案内しているため、将来のIPv6到達性と経路冗長性の改善候補とする。

### CNAME

```text
www.kyudojapan.net. 3600 IN CNAME （GitHub Pages既定ドメイン）
```

設定はGitHub公式の推奨と一致する。apexにCNAMEはなく、Aレコードを使用している。

### DNS伝播・名前解決時間

- 権威DNS4台: すべて正常
- Cloudflare、Google、Quad9: すべて正常
- 公開DNSの応答時間: 約32〜174ms
- Mac既定DNSの通常応答: 約18〜22ms

世界的なDNS伝播は完了している。問題は特定のプライマリ再帰DNS内部のキャッシュ群に限定されている。

### その他

- CAA: 未設定
- DNSSEC DS: 未設定
- 権威DNS上のワイルドカード: なし
- GitHub Pages所有確認TXT: 権威DNSと公開DNSに正しい値が存在
- GitHub API上の所有確認状態: `unverified`

TXTは登録済みだが、GitHubの個人設定側で最終の「Verify」が完了していない状態と考えられる。これは今回の接続障害の原因ではないが、ドメイン乗っ取り防止のため完了を推奨する。

## 6. GitHub Pages・Actions調査

### Pages設定

- Pages status: `built`
- Build type: `workflow`
- Custom Domain: `kyudojapan.net`
- 公開URL: `https://kyudojapan.net/`
- Enforce HTTPS: 有効
- Pending domain verification: なし
- Protected domain state: `unverified`

### 最新デプロイ

- 公開コミット: `e04a9f4eb8486ab3a1957d8d26ad5c9eab0241f1`
- タイトル: `fix: remove X link from v7.1.0 release card`
- Workflow run: `29925064600`
- 開始: 2026-07-22 22:41:51 JST
- 完了: 2026-07-22 22:42:20 JST
- 結果: success
- validate: success
- deploy: success

直近10回のPages workflowはすべて成功しており、Deploy失敗は確認されなかった。

### ローカルRepository状態

- ローカルHEAD: `297fe5a`
- `origin/main`: `e04a9f4`
- ローカルmainはremoteより2コミット遅れている
- 既存の未コミット性能改善があるため、調査中にmerge、rebase、reset、commit、pushは行っていない
- 本報告書だけを新規作成し、既存変更は保全した

## 7. GitHub Status

調査時点ではGitHubの全システムがOperationalで、PagesもOperationalだった。

直近では次の公式障害履歴がある。

1. 2026-07-23 05:43〜07:09 JST: GitHub Actions hosted runnersの遅延。一部runの開始遅延であり、Pages配信障害ではない。
2. 2026-07-20 09:49〜10:37 JSTごろ: Actions障害の波及でPagesが一時的にdegraded performance。すでに解消済み。

今回の調査時間帯の接続障害は再帰DNSだけで再現できるため、現在のGitHub障害は原因ではない。発生報告が2026-07-20の上記時間帯を含む場合に限り、当時のGitHub Pages障害も一部影響した可能性がある。

## 8. HTTPS・証明書

- 証明書CN: `kyudojapan.net`
- SAN: `kyudojapan.net`, `www.kyudojapan.net`
- 発行者: Let's Encrypt `YR1`
- 有効期間: 2026-07-21 22:59:28 UTC〜2026-10-19 22:59:27 UTC
- 証明書チェーン検証: `Verify return code: 0 (ok)`
- TLS: TLS 1.3
- 暗号スイート: `AEAD-CHACHA20-POLY1305-SHA256`
- HTTPからHTTPS: 301で正常転送
- `www`からapex: 301で正常転送
- Mixed Content: 検出なし

証明書、証明書チェーン、HTTPS強制に異常はない。

## 9. ネットワーク・CDN・curl

### GitHub Pagesの4配信先

`--resolve`で各IPへ直接接続した結果、すべてHTTP 200だった。

| IP | HTTP | 総時間 |
|---|---:|---:|
| `185.199.108.153` | 200 | 0.096秒 |
| `185.199.109.153` | 200 | 0.053秒 |
| `185.199.110.153` | 200 | 0.041秒 |
| `185.199.111.153` | 200 | 0.041秒 |

### 通常の反復接続

- IPv4 HTTPSを10回実行: 10回すべてHTTP 200
- 初回総時間: 0.342秒
- 2回目以降: おおむね0.041〜0.075秒
- HTTP/2: 有効
- 接続再利用: 2リクエスト目の新規接続数0を確認
- CDN: `via: 1.1 varnish`、`x-served-by: cache-...` を確認
- Cache: HITを確認

通常のcurl反復中はOSキャッシュが正常IPを保持したため失敗しなかったが、DNSサーバーへの直接問い合わせでは新旧応答の混在を再現した。

### IPv6

ドメインにネイティブAAAAはない。調査環境の `curl -6` はIPv4-mappedアドレス `::ffff:185.199.108.153` を使用して成功したため、現在回線の変換経路では到達できる。ただし、これはネイティブIPv6での公開を意味しない。

## 10. ブラウザ・端末

| 環境 | 結果 |
|---|---|
| Mac Safari | `IsSecure=true`、トップページを正常表示 |
| Chrome | このMacに未導入のため実アプリ確認不可 |
| iPhone | 実際の発生端末。発生時は調査Macと同じWi-Fiへ接続。SafariのiCloudタブにも「ページを開けません - kyudojapan.net」の過去表示あり |
| Android | 実機なし。未確認 |
| Windows | 実機なし。未確認 |

iPhoneが同じWi-Fiへ接続中に発生したため、Wi-Fi側のプライマリ再帰DNS不整合を原因として確定した。

## 11. Search Console・robots・sitemap

### Search Console

- ドメインプロパティ `kyudojapan.net` のサマリーへアクセス可能
- インデックス作成: 「データを処理しています。1日後にもう一度確認」
- HTTPS: 4 URL
- HTTPS以外: 0 URL
- 検索クリック: 0（公開直後のため異常とは判定しない）

Search Console内の個別サイトマップ詳細までは確認していない。

### 公開ファイル

- `robots.txt`: HTTP 200、クロール許可、サイトマップURL正常
- `sitemap.xml`: HTTP 200、`application/xml`
- XML構文: 正常
- サイトマップ掲載13 URL: すべてHTTP 200、不要なリダイレクトなし
- Googlebot User-Agent相当のトップページ取得: HTTP 200
- `manifest.webmanifest`: HTTP 200

検索クローラーの公開到達性に問題はない。

## 12. 実施した修正

### 外部設定

権威DNS、GitHub Pages、ルーター、iPhoneの設定は変更していない。

原因確認のため、ユーザー承認後にMacのWi-Fi DNSだけを一時的にCloudflare `1.1.1.1` / `1.0.0.1` へ変更した。変更後はDNS問い合わせ20回すべてがGitHub Pagesの正しい4アドレスとなり、HTTPS接続10回すべてがHTTP 200だった。

ユーザーから「発生端末はiPhoneであり、Macの変更は不要」と連絡を受けたため、MacのWi-Fi DNSは直ちに変更前の自動取得へ復元した。最終確認結果は「手動DNSなし」で、次の自動配布DNSへ戻っている。

```text
2001:a7ff:5f01::a
2001:a7ff:5f01:1::a
192.168.11.1
```

Macに恒久的な設定変更は残っていない。

### Repository

- `outputs/reports/website_connection_report.md` を新規作成
- サイトコード、Flutterアプリ、DNS、GitHub Pages設定は変更していない

## 13. 現状

- 世界向けの権威DNSと主要公開DNSは正常
- GitHub PagesとHTTPSは正常
- 利用中ネットワークのプライマリ再帰DNSだけが旧IPを断続的に返す
- 旧IPを受け取った利用者はHTTPS接続がタイムアウトする
- DNSキャッシュが正常IPへ更新された端末では問題なく表示できる

## 14. 一時対応

設定変更は影響を確認し、承認後に行う。

1. iPhoneがWi-Fi接続中だった場合、Wi-Fiを一時的に切り、モバイル回線で `https://kyudojapan.net` を確認する。
2. モバイル回線では正常でWi-Fiだけ失敗する場合、対象Wi-FiのDNSをCloudflare `1.1.1.1` / `1.0.0.1` などの正常なDNSへ一時変更して確認する。
3. Wi-Fiとモバイル回線の両方で失敗する場合、iPhoneの機内モードをオン・オフし、Safariを終了して再試行する。
4. Macの設定は変更せず、自動取得のまま維持する。
5. Androidでは機内モードのオン・オフ、Private DNSの切り替え、別回線での確認を行う。
6. Windowsでは `ipconfig /flushdns` 後に再確認し、必要ならアダプターDNSを変更する。

DNS変更は、ISP固有の名前解決、フィルタリング、IPTV等へ影響する可能性があるため、恒久設定前に利用中サービスを確認する。

## 15. 恒久対応

優先順は次のとおり。

1. 利用回線またはDNSサービス提供元へ、`2001:a7ff:5f01::a` が `kyudojapan.net` に旧IP `150.95.255.38` とTTL 300秒を断続的に返す事実を連絡し、キャッシュ削除・同期を依頼する。
2. 当面、端末またはルーターのDNSを正常な再帰DNSへ切り替える。ISP固有サービスとの互換性を確認してから恒久化する。
3. GitHub公式のAAAAレコード4件を追加し、ネイティブIPv6経路を用意する。これは今回のAキャッシュ不整合そのものを直すものではないが、IPv6利用者の経路冗長性を改善する。
4. GitHub Pagesのドメイン所有確認画面でTXTを最終確認し、「Verify」を完了する。既存TXTは削除しない。

GitHub公式AAAA候補:

```text
2606:50c0:8000::153
2606:50c0:8001::153
2606:50c0:8002::153
2606:50c0:8003::153
```

## 16. 再発防止・監視案

### Repository内監視

GitHub Actionsへ定期監視workflowを追加する。

- `https://kyudojapan.net/` のHTTPステータスと応答時間
- HTTP→HTTPS、`www`→apexのリダイレクト
- 権威DNS4台のA、AAAA、CNAME一致
- GitHub Pagesの4IPへの個別HTTPS接続
- TLS有効期限
- `robots.txt`、`sitemap.xml`、`manifest.webmanifest`
- sitemap掲載URLのHTTP 200
- 失敗時にGitHub Issueまたは通知を作成

ただし、GitHub Actionsの実行地点から特定ISPの再帰DNS `2001:a7ff:5f01::a` へ到達できる保証はないため、今回と同種の地域・回線限定障害を完全には検知できない。

### 外形監視

- 日本国内を含む複数拠点の外形監視を使用
- GitHub StatusのPagesとActionsを購読
- DNSレコード変更後24〜48時間は、権威DNS・Cloudflare・Google・利用回線DNSを並行確認
- DNS変更前後の値、TTL、変更時刻を運用記録へ残す

### 端末側確認

- Mac、iPhone、Android、Windowsの各1台で、Wi-Fiとモバイル回線を分けて確認
- 障害時は、時刻、回線、DNS結果、ブラウザエラー、取得IPを記録

## 17. 未確認事項

- 申告された最初の発生時刻
- Android実機とWindows実機での再現
- Chrome実アプリでの表示（調査Macに未導入）
- iPhoneでの現在の制御された再試験
- Search Consoleの個別サイトマップ送信・取得ステータス
- 利用回線/DNSサービス提供元によるキャッシュ不整合の正式な障害回答
- DNS変更がIPTV等の契約サービスへ与える影響

## 18. 参照先

- GitHub Pages custom domain設定: https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/managing-a-custom-domain-for-your-github-pages-site
- GitHub Pages domain verification: https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/verifying-your-custom-domain-for-github-pages
- GitHub Status: https://www.githubstatus.com/
- GitHub Status API: https://www.githubstatus.com/api/v2/summary.json
- GitHub incident API: https://www.githubstatus.com/api/v2/incidents.json
