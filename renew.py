import os
import requests
import datetime


BASE_URL = "https://cloud.puratya.com"


# ==========================
# Bot 配置
# ==========================

BOTS = [
    {
        "id": "9341",
        "name": "主服务器"
    },

    # 多个继续添加
    #
    # {
    #     "id":"9342",
    #     "name":"测试服务器"
    # }

]


# ==========================
# GitHub Secrets
# ==========================

TOKEN = os.getenv(
    "PURATYA_TOKEN"
)


TG_BOT_TOKEN = os.getenv(
    "TG_BOT_TOKEN"
)


TG_CHAT_ID = os.getenv(
    "TG_CHAT_ID"
)



headers = {

    "User-Agent":
    "Mozilla/5.0",

    "Origin":
    BASE_URL

}



cookies = {

    "__Host-mrtcloud_token":
    TOKEN

}



report=[]



# ==========================
# Telegram
# ==========================

def tg_send(msg):

    if not TG_BOT_TOKEN:
        print(
            "TG 未配置"
        )
        return


    url=f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"


    data={

        "chat_id":
        TG_CHAT_ID,

        "text":
        msg,

        "parse_mode":
        "HTML",

        "disable_web_page_preview":
        True

    }


    requests.post(
        url,
        data=data,
        timeout=10
    )



# ==========================
# 续期
# ==========================

def renew(bot):

    bot_id = bot["id"]

    name = bot["name"]


    url=f"{BASE_URL}/api/bots/{bot_id}/renew"


    try:


        r=requests.post(

            url,

            headers=headers,

            cookies=cookies,

            timeout=20

        )


        data=r.json()


        timer=data.get(
            "timer",
            {}
        )


        seconds=timer.get(
            "remaining_seconds",
            0
        )


        hours=seconds//3600


        stop=timer.get(
            "stop_at",
            "-"
        )


        report.append(
f"""
✅ <b>续期成功</b>

🖥 {name}

🆔 Bot:
<code>{bot_id}</code>

⏰ 剩余:
<b>{hours}小时</b>

📅 到期:
{stop}

"""
        )



    except Exception as e:


        report.append(
f"""
❌ <b>续期失败</b>

🖥 {name}

🆔 Bot:
<code>{bot_id}</code>

错误:
<code>{e}</code>

"""
        )



# ==========================
# 主程序
# ==========================


print(
"====== Puratya Renew ======"
)



for bot in BOTS:

    renew(bot)



now=datetime.datetime.utcnow()


msg=f"""
🤖 <b>Puratya续期通知</b>

━━━━━━━━━━━━

"""


msg += "\n".join(report)


msg += f"""

━━━━━━━━━━━━

🕒 执行时间:
{now}

⚡ GitHub Actions
"""


print(msg)


tg_send(msg)
