from telethon.sync import TelegramClient
from telethon.sessions import StringSession

# 依然使用 2040 方案
API_ID = 2040
API_HASH = 'b18441a1ff607e10a989891a5462e627'

# 代理设置（如果你本地需要挂梯子才能连 TG）
# 请确保端口与你的 Clash/V2Ray 一致，通常是 7890 或 1080
proxy = ("socks5", "127.0.0.1", 7897) 

with TelegramClient(StringSession(), API_ID, API_HASH, proxy=proxy) as client:
    session_str = client.session.save()
    print("\n--- 你的 STRING_SESSION 如下，请妥善保存，切勿外泄 ---\n")
    print(session_str)
    print("\n---------------------------------------------------\n")