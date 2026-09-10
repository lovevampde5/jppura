import os
import requests
import datetime


# ==================================
# Puratya 配置
# ==================================

BASE_URL = "https://cloud.puratya.com"


# ==================================
# Bot 列表
# ==================================

BOTS = [
    {
        "id": "9341",
        "name": "jpbot"
    },

    # 添加更多 Bot：
    #
    # {
    #     "id": "9342",
    #     "name": "usbot"
    # },
]


# ==================================
# GitHub Secrets
# ==================================

PURATYA_TOKEN = os.getenv("PURATYA_TOKEN")
TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
TG_CHAT_ID = os.getenv("TG_CHAT_ID")


# ==================================
# 浏览器请求 Headers
# 尽量模拟 Puratya 网站实际请求
# ==================================

BASE_HEADERS = {
    "Accept": "*/*",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,de;q=0.7",
    "Content-Type": "application/json",
    "Origin": BASE_URL,
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/605.1.15 "
        "(KHTML, like Gecko) "
        "Version/18.5 Safari/605.1.15"
    ),
}


# ==================================
# Puratya Cookie
# ==================================

cookies = {
    "__Host-mrtcloud_token": PURATYA_TOKEN or ""
}


# ==================================
# 续期结果
# ==================================

reports = []


# ==================================
# Telegram 推送
# ==================================

def send_telegram(message):

    if not TG_BOT_TOKEN or not TG_CHAT_ID:
        print("Telegram 未配置")
        return

    url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"

    data = {
        "chat_id": TG_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    }

    try:

        response = requests.post(
            url,
            data=data,
            timeout=10
        )

        print("Telegram:", response.status_code)

        if response.status_code != 200:
            print("Telegram 返回:", response.text[:500])

    except Exception as e:

        print("TG发送失败:", e)


# ==================================
# Puratya 续期
# ==================================

def renew(bot):

    bot_id = bot["id"]
    name = bot["name"]

    url = f"{BASE_URL}/api/bots/{bot_id}/renew"

    # 每个 Bot 使用对应页面作为 Referer
    headers = BASE_HEADERS.copy()
    headers["Referer"] = f"{BASE_URL}/bots/{bot_id}"

    print(f"正在续期 {name} ({bot_id})")

    try:

        # 注意：
        # 不传 data/json，保持浏览器请求 Content-Length: 0
        response = requests.post(
            url,
            headers=headers,
            cookies=cookies,
            timeout=20
        )

        print(
            f"{name} HTTP状态:",
            response.status_code
        )

        # ==================================
        # 续期失败
        # ==================================

        if response.status_code != 200:

            # 读取服务器错误信息
            error_text = response.text.strip()

            # 防止 Telegram 消息过长
            if len(error_text) > 300:
                error_text = error_text[:300] + "..."

            if not error_text:
                error_text = "服务器没有返回错误信息"

            reports.append(
                f"❌ **{name}续期失败**\n"
                f"🆔 Bot: `{bot_id}`\n"
                f"⚠️ HTTP: `{response.status_code}`\n"
                f"📄 返回: `{error_text}`"
            )

            print(
                f"{name} 续期失败:",
                error_text
            )

            return

        # ==================================
        # 解析成功响应
        # ==================================

        try:
            data = response.json()

        except Exception:

            reports.append(
                f"❌ **{name}续期失败**\n"
                f"🆔 Bot: `{bot_id}`\n"
                f"⚠️ 错误: `返回数据不是JSON`"
            )

            print(
                f"{name} 返回:",
                response.text[:500]
            )

            return

        # ==================================
        # 获取 timer
        # ==================================

        timer = data.get("timer", {})

        seconds = timer.get(
            "remaining_seconds",
            0
        )

        try:
            hours = int(seconds) // 3600
        except Exception:
            hours = 0

        stop_at = timer.get(
            "stop_at",
            "-"
        )

        # ==================================
        # 格式化到期时间
        # ==================================

        if stop_at and stop_at != "-":

            stop_at = (
                stop_at
                .replace("T", " ")
                .replace("Z", "")
                [:16]
            )

        else:

            stop_at = "-"

        # ==================================
        # 成功
        # ==================================

        reports.append(
            f"✅ **{name}续期成功**\n"
            f"🆔 Bot: `{bot_id}`\n"
            f"⏰ 剩余: **{hours}小时**\n"
            f"📅 到期: {stop_at}"
        )

        print(
            f"{name} 续期成功 | "
            f"剩余 {hours} 小时 | "
            f"到期 {stop_at}"
        )

    except requests.exceptions.Timeout:

        reports.append(
            f"❌ **{name}续期失败**\n"
            f"🆔 Bot: `{bot_id}`\n"
            f"⚠️ 错误: `请求超时`"
        )

        print(f"{name} 请求超时")

    except requests.exceptions.RequestException as e:

        reports.append(
            f"❌ **{name}续期失败**\n"
            f"🆔 Bot: `{bot_id}`\n"
            f"⚠️ 错误: `{e}`"
        )

        print(
            f"{name} 网络错误:",
            e
        )

    except Exception as e:

        reports.append(
            f"❌ **{name}续期失败**\n"
            f"🆔 Bot: `{bot_id}`\n"
            f"⚠️ 错误: `{e}`"
        )

        print(
            f"{name} 未知错误:",
            e
        )


# ==================================
# 主程序
# ==================================

if __name__ == "__main__":

    print("====== Puratya Auto Renew ======")

    # ==================================
    # 检查 Token
    # ==================================

    if not PURATYA_TOKEN:

        print("错误：未配置 PURATYA_TOKEN")

        reports.append(
            "❌ **Puratya续期失败**\n"
            "⚠️ 错误: `未配置 PURATYA_TOKEN`"
        )

    else:

        # ==================================
        # 续期所有 Bot
        # ==================================

        for bot in BOTS:

            renew(bot)

    # ==================================
    # UTC 时间
    # ==================================

    now = datetime.datetime.now(
        datetime.timezone.utc
    )

    checkin_time = now.strftime(
        "%Y-%m-%d %H:%M"
    )

    # ==================================
    # Telegram 消息
    # 不留空行
    # ==================================

    message = (
        "🤖 **Puratya续期通知**\n"
        + "\n".join(reports)
        + f"\n🕒 签到时间：{checkin_time} UTC"
    )

    # ==================================
    # 控制台输出
    # ==================================

    print()
    print(message)
    print()

    # ==================================
    # Telegram
    # ==================================

    send_telegram(message)
