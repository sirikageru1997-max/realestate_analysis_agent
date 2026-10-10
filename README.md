# init enviroment

```shell
source ./.venv/bin/activate
```

# implemnet

```cron
# 例: 毎週月曜日の朝9時に実行する場合
0 9 * * 1 cd /home/pi/realestate_agent && /usr/bin/python3 report_agent.py >> /home/pi/realestate_agent/cron.log 2>&1
```
