# system

```shell
./realestate_agent/
  ├─ report_agent.py (メインスクリプト)
  ├─ .env (環境変数)
  └─ config/
       ├─ credentials.json (Google Cloud Consoleからダウンロードする「アプリの設定ファイル」)
       ├─ token.json (自動生成されるファイル)
       └─ token.json.bak (自動バックアップ)
```
- token.json の中身のイメージ
  - 最初に認証したとき、token.json には主に2つの重要なキー（鍵）が保存されます。
    - token (アクセストークン)：実際の処理（Docs作成やGmail送信など）を行うための鍵。有効期限が短い（例：1時間）。
    - refresh_token (リフレッシュトークン)：アクセストークンを再発行してもらうための鍵。有効期限が長い（条件によっては無期限）。


# init enviroment

```shell
source ./.venv/bin/activate
```

# implemnet

```cron
# cron設定（毎週月曜9時実行の例）
# user `.venv`
0 9 * * 1 cd /home/pi/realestate_agent && /home/pi/realestate_agent/.venv/bin/python report_agent.py >> /home/pi/realestate_agent/cron.log 2>&1
```
