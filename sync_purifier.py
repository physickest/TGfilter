import asyncio
import os
import time
import re
from telethon import TelegramClient, errors
from telethon.sessions import StringSession

# --- 环境变量读取 (SOTA 安全实践) ---
API_ID = int(os.getenv('TG_API_ID', 2040))
API_HASH = os.getenv('TG_API_HASH', 'b18441a1ff607e10a989891a5462e627')
SESSION_STR = os.getenv('TG_STRING_SESSION')
TARGET_FEED = os.getenv('PRIVATE_CHANNEL_ID')
# 云端运行不需要本地代理，将其设为 None
proxy = None

# ================= 频道规则配置表 =================
# 不同的频道对应不同的黑名单特征
CHANNEL_RULES = {
    'Seele_Leaks': {
        'blocked_keywords': ['ZZZ', 'HI3', 'AKEndfield', 'Endfield'],
        'blocked_senders': ['广告源']
    },

    # 'HXG_Leak': {
    #     'blocked_keywords': ['ZZZ', 'HI3', 'AKEndfield', 'Endfield'],
    #     'blocked_senders': ['广告源']
    # }
    
}

# ================= 核心逻辑引擎 =================

async def main():
    client = TelegramClient(StringSession(SESSION_STR), API_ID, API_HASH,proxy=proxy)
            
    now = time.time()
    lookback_seconds = 1 * 60*60  # 3hour窗口
    
    async with client:
        print(f"[*] 正在扫描 {CHANNEL_RULES}...")
        
    # 遍历你配置的所有频道
        for channel_id, rules in CHANNEL_RULES.items():
            print(f"[*] 正在处理频道: {channel_id}")
            
            blocked_group_ids = set()
            message_buffer = []
            
            # 预编译正则，提高大规模匹配速度
            # r'\b' 表示单词边界，防止把 'pizza' 里的 'zzz' 误删
            kw_pattern = re.compile('|'.join(rules['blocked_keywords']), re.IGNORECASE)

            async for msg in client.iter_messages(channel_id, limit=50):
                # ... 时间窗口逻辑 ...
                msg_age = now - msg.date.timestamp()
                if msg_age > lookback_seconds:
                    break

                async def get_fast_fwd_name(msg):
                    # 1. 优先从内存已有的属性中取，这不需要联网
                    if not msg.fwd_from: return ""
                    
                    # 尝试直接读取字段，不发起请求
                    name = msg.fwd_from.from_name
                    if name: return name
                    
                    # 2. 如果没有名字，只有 ID，则尝试从本地缓存获取，不强行联网
                    try:
                        # 仅当 client 已经缓存过该实体时，这个调用才不耗时
                        entity = await msg.client.get_entity(msg.fwd_from.from_id)
                        return getattr(entity, 'title', '') or getattr(entity, 'first_name', '')
                    except:
                        return "" # 拿不到就放弃，不要为了一个名字让整个系统停摆
                    
                content = msg.text or ""
                fwd_name = await get_fast_fwd_name(msg)

                # --- 升级版判定逻辑 ---
                is_blocked = (
                    kw_pattern.search(content) or 
                    any(name.lower() in fwd_name.lower() for name in rules['blocked_senders'])
                )

                if is_blocked and msg.grouped_id:
                    blocked_group_ids.add(msg.grouped_id)
                    continue
                
                if not is_blocked:
                    message_buffer.append(msg)

            # 第二遍过滤：剔除那些“组内有人违规”的消息
            final_buffer = []
            for msg in message_buffer:
                if msg.grouped_id and msg.grouped_id in blocked_group_ids:
                    print(f"[X] 拦截组消息: 因为该组其他成员包含黑名单关键词")
                    continue
                final_buffer.append(msg)

            # --- 关键：反转时序并转发 ---
            final_buffer.reverse()

            print(f"[*] 过滤完成，准备按时间正序转发 {len(final_buffer)} 条消息...")

            for msg in final_buffer:
                try:
                    await client.forward_messages(TARGET_FEED, msg)
                    # 稍微增加一点延迟，模拟人类行为，防止触发 TG 的 Flood Limit
                    await asyncio.sleep(0.5) 
                except Exception as e:
                    print(f"[!] 转发失败: {e}")

        print(f"[Summary] 同步任务结束。")

if __name__ == '__main__':
    print('start to twirl')
    asyncio.run(main())
