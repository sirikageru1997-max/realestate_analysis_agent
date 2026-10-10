# system

```shell
./realestate_agent/
  ├─ report_agent.py (メインスクリプト)
  ├─ .env (環境変数)
  └─ config/
       ├─ credentials.json (ダウンロードしたファイル)
       ├─ token.json (自動生成されるファイル)
       └─ token.json.bak (自動バックアップ)
```

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
