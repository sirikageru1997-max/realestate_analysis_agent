新しい認証方式（OAuth 2.0によるトークン自動更新）を中核に据えた、システム構成と各モジュールの再設計です。

Google DocsAPIとGmail APIの認証を「1つのOAuth 2.0システム」に統合することで、セキュリティと保守性が大幅に向上します。

```text
[Raspberry Pi]
  └─ cron (週1回トリガー)
       ↓
  [Pythonスクリプト: report_agent.py]
       ├─ Module 1: 🔑 認証基盤 (OAuth 2.0 トークン管理)
       ├─ Module 2: 🌐 国交省API (データ取得)
       ├─ Module 3: 🧠 Gemini API (データ分析)
       ├─ Module 4: 📄 Google Docs API (レポート生成)
       └─ Module 5: ✉️ Gmail API (完了通知)

```

---

## 統括モジュール設計

### Module 1: 認証基盤 (Google OAuth 2.0)

システム全体の心臓部となる、最も重要なモジュールです。Google DocsとGmailの両方へアクセスするための「鍵束」を管理します。

* **役割:** `token.json`の読み込み、有効期限の確認、リフレッシュトークンを用いたアクセストークンの自動更新。
* **必要なファイル:**
* `credentials.json`: Google Cloud Consoleからダウンロードする「アプリの設定ファイル」。
* `token.json`: 初回認証時に自動生成される「アクセストークンとリフレッシュトークンが保存されたファイル」。


* **要求する権限（スコープ）:**
* `[https://www.googleapis.com/auth/documents](https://www.googleapis.com/auth/documents)` (Docsの編集)
* `[https://www.googleapis.com/auth/drive.file](https://www.googleapis.com/auth/drive.file)` (Docsファイルの新規作成)
* `[https://www.googleapis.com/auth/gmail.send](https://www.googleapis.com/auth/gmail.send)` (Gmailでの送信のみ)


* **処理フロー:**
1. `token.json` があるか確認。
2. 有効期限が切れていれば、内部の `refresh_token` をGoogleに送り、新しいアクセストークンを取得。
3. 新しい状態を `token.json` に上書き保存し、以降のモジュール（DocsとGmail）に認証情報（Credentialsオブジェクト）を引き渡す。



### Module 2: データ取得 (国交省 不動産情報ライブラリAPI)

* **役割:** 指定された条件（地域、期間など）に基づいて、時系列分析の元となるJSONまたはCSVデータを取得します。
* **ポイント:** Geminiのコンテキスト制限やAPI課金を抑えるため、取得段階で不要なカラム（列）や対象外エリアのデータをPythonの `pandas` 等で事前に削ぎ落とす（前処理する）処理をここに挟むと、システムが安定します。

### Module 3: データ分析 (Gemini API)

* **役割:** Module 2で整形したデータと、ご自身で作成した「分析プロンプト」を結合し、Gemini APIに送信します。
* **ポイント:** 分析プロンプト内で「Markdown形式で見出しや表を使って出力してください」と指示しておくことで、次のDocs生成モジュールでのレイアウトが美しくなります。

### Module 4: レポート生成 (Google Docs API & Drive API)

* **役割:** Module 1で生成した認証情報を使い、Googleドライブ上に新規ドキュメントを作成し、Module 3の分析結果を書き込みます。
* **処理フロー:**
1. Drive APIで新規ドキュメント（空ファイル）を作成し、`Document ID` を取得。
2. Docs APIの `batchUpdate` メソッドを使用し、取得したIDのドキュメントへGeminiのテキストを挿入。
3. 生成したドキュメントのURL（`[https://docs.google.com/document/d/](https://docs.google.com/document/d/)【Document ID】/edit`）をModule 5へ渡す。



### Module 5: 完了通知 (Gmail API)

* **役割:** Module 1の認証情報を使って、ご自身のGmailアドレス宛に完了通知とレポートURLを送信します。
* **処理フロー:**
1. Pythonの標準ライブラリ（`email.mime.text`）でメールの件名、本文（DocsのURLを含む）を作成。
2. 作成したメールデータをBase64形式にエンコード。
3. Gmail APIの `users().messages().send(userId='me', body=...)` を呼び出して送信。送信箱（Sent）にも履歴が残ります。



---

## 実装に向けた重要チェックポイント

この構成をラズパイで実現するにあたり、以下の事前準備が成功の鍵となります。

**1. 初回のみ「ブラウザのあるPC」でトークンを作る**
ラズパイは通常、画面（ブラウザ）のない環境で動かします。しかしOAuth 2.0は「一番最初だけブラウザでログイン承認」が必要です。

* **解決策:** まずお手元のWindowsやMacでこのPythonスクリプトを1回だけ実行し、ブラウザで承認して `token.json` を生成します。その後、生成された `token.json` とプログラム一式をラズパイにコピー（配置）してください。これでラズパイ上では完全に自動で動くようになります。

**2. Google Cloud プロジェクトの「本番環境」化**
テスト状態（Testing）のままだと、リフレッシュトークンを発行しても**7日間で強制的に期限切れ**になります。Google Cloud Consoleの「OAuth 同意画面」の設定で、公開ステータスを必ず「本番環境 (In production)」に変更してください。（個人利用の範囲であれば、Googleの厳しい審査等は不要でボタン一つで変更できます）。
