# MWS Bot 续期教程（脱敏版）

## 原理

MWS Bot 的租期由服务端控制。调用续期接口后，通常会重新获得 **168 小时（7 天）**租期。

续期接口：

```text
POST https://cloud.puratya.com/api/bots/<BOT_ID>/renew
```

需要使用你自己账号的 MWS Cookie，不能使用别人的 Cookie。

## curl 续期

```bash
export MWS_COOKIE='你的MWS Cookie'
export BOT_ID='你的Bot ID'

curl -X POST \
  "https://cloud.puratya.com/api/bots/${BOT_ID}/renew" \
  -H "Cookie: __Host-mrtcloud_token=${MWS_COOKIE}"
```

## 查询续期结果

```bash
curl \
  "https://cloud.puratya.com/api/bots/${BOT_ID}" \
  -H "Cookie: __Host-mrtcloud_token=${MWS_COOKIE}"
```

重点查看返回值中的：

```json
{
  "timer": {
    "last_renewed_at": "续期时间",
    "stop_at": "到期时间",
    "remaining_seconds": 604800
  }
}
```

## Python 自动续期示例

```python
import os
import time
import requests

API = "https://cloud.puratya.com/api"
COOKIE = os.environ["MWS_COOKIE"]
BOT_IDS = ["你的Bot ID"]

headers = {
    "Cookie": f"__Host-mrtcloud_token={COOKIE}",
    "User-Agent": "mws-renew-example/1.0",
}


def renew(bot_id):
    response = requests.post(
        f"{API}/bots/{bot_id}/renew",
        headers=headers,
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


while True:
    for bot_id in BOT_IDS:
        try:
            result = renew(bot_id)
            print(f"Bot {bot_id} 续期成功：", result)
        except Exception as error:
            print(f"Bot {bot_id} 续期失败：{error}")

    # 12 小时执行一次
    time.sleep(12 * 60 * 60)
```

运行前设置自己的 Cookie：

```bash
export MWS_COOKIE='你的MWS Cookie'
python renew.py
```

> 不要把 Cookie、Token 或密码写进代码、截图或公开教程。
