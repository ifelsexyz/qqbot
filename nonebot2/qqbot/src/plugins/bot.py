from nonebot import on_keyword, on_message
from nonebot.rule import to_me
from nonebot.adapters import Bot, Event
from nonebot.typing import T_State
from nonebot.adapters.onebot.v11 import GroupMessageEvent,Bot,Message,MessageSegment,Event
import os
import qianfan

os.environ["QIANFAN_AK"] = "bHMOWdRpEGMFmNTgrZY8i5qJ"
os.environ["QIANFAN_SK"] = "CSnOr9SaRUk7zhnvfnL4X8NZ4WNq8pOO"

chat_comp = qianfan.ChatCompletion()


chat = on_message(rule=to_me(), priority=5)
@chat.handle()
async def chat_handle(bot: Bot, event: Event, state: T_State):
    msg = str(event.message)
    try:
        resp = chat_comp.do(model="ERNIE-Speed-128K", messages=[{
            "role": "user",
            "content": msg
        }])
        response = resp["result"]
    except Exception as e:
        response = "抱歉，我无法回答这个问题。"
        print(f"Error in send_message: {e}")
    msg_list =[]
    msg_list.append(
        {
            "type": "node",
            "data": {
                "name": "1",
                "uin": event.self_id,
                "content": response
                }
            }
        )
    await bot.send_group_forward_msg(group_id = event.group_id, messages = msg_list)