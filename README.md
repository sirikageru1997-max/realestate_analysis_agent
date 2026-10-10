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
