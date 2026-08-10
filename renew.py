import os
import requests
import datetime


# ==================================
# Puratya 配置
# ==================================

BASE_URL = "https://cloud.puratya.com"


# Bot列表
# 增加服务器只需要复制一组

BOTS = [
    {
        "id": "9341",
        "name": "jpbot"
    }

    # 示例:
    #
    # {
    #     "id": "9342",
    #     "name": "usbot"
    # }

]


# ==================================
# GitHub Secrets
# ==================================

PURATYA_TOKEN = os.getenv(
    "PURATYA_TOKEN"
)


TG_BOT_TOKEN = os.getenv(
    "TG_BOT_TOKEN"
)


TG_CHAT_ID = os.getenv(
    "TG_CHAT_ID"
)



# ==================================
# 请求配置
# ==================================

headers = {

    "User-Agent":
        "Mozilla/5.0",

    "Accept":
        "*/*",

    "Origin":
        BASE_URL

}


cookies = {

    "__Host-mrtcloud_token":
        PURATYA_TOKEN

}



reports = []



# ==================================
# Telegram 推送
# ==================================

def send_telegram(message):

    if not TG_BOT_TOKEN or not TG_CHAT_ID:
        print("Telegram 未配置")
        return


    url = (
        f"https://api.telegram.org/"
        f"bot{TG_BOT_TOKEN}/sendMessage"
    )


    data = {

        "chat_id":
            TG_CHAT_ID,

        "text":
            message,

        "parse_mode":
            "HTML",

        "disable_web_page_preview":
            True

    }


    try:

        r = requests.post(
            url,
            data=data,
            timeout=10
        )

        print(
            "Telegram:",
            r.status_code
        )


    except Exception as e:

        print(
            "TG发送失败:",
            e
        )



# ==================================
# Puratya续期
# ==================================

def renew(bot):

    bot_id = bot["id"]

    name = bot["name"]


    url = (
        f"{BASE_URL}/api/bots/"
        f"{bot_id}/renew"
    )


    print(
        f"开始续期: {name} ({bot_id})"
    )


    try:

        response = requests.post(

            url,

            headers=headers,

            cookies=cookies,

            timeout=20

        )


        print(
            "HTTP:",
            response.status_code
        )


        if response.status_code != 200:

            raise Exception(
                f"HTTP {response.status_code}"
            )


        data = response.json()


        timer = data.get(
            "timer",
            {}
        )


        seconds = timer.get(
            "remaining_seconds",
            0
        )


        hours = seconds // 3600


        stop_at = timer.get(
            "stop_at",
            "-"
        )


        # 时间格式:
        # 2026-08-17 00:36

        if stop_at != "-":

            stop_at = (
                stop_at
                .replace("T", " ")
                [:16]
            )


        reports.append(

f"""
✅ <b>{name}续期成功</b>
🆔 Bot: <code>{bot_id}</code>
⏰ 剩余: <b>{hours}小时</b>
📅 到期: {stop_at}
"""

        )


    except Exception as e:


        reports.append(

f"""
❌ <b>{name}续期失败</b>
🆔 Bot: <code>{bot_id}</code>
⚠️ 错误: <code>{e}</code>
"""

        )



# ==================================
# 主程序
# ==================================

if __name__ == "__main__":


    print(
        "====== Puratya Auto Renew ======"
    )


    for bot in BOTS:

        renew(bot)



    now = datetime.datetime.utcnow()


    message = (

f"""🤖 <b>Puratya续期通知</b>

"""

    )


    message += "\n".join(
        reports
    )


    message += (

f"""

🕒 {now.strftime('%Y-%m-%d %H:%M')} UTC
⚡ GitHub Actions
"""

    )


    print(
        message
    )


    send_telegram(
        message
    )
