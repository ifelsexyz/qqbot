from nonebot import on_keyword, on_message
from nonebot.rule import to_me
from nonebot.adapters import Bot, Event
from nonebot.typing import T_State
from nonebot.adapters.onebot.v11 import GroupMessageEvent,Bot,Message,MessageSegment,Event

import json
import types
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.hunyuan.v20230901 import hunyuan_client, models
import os
import time
import psutil
# 获取系统运行时间
def get_system_uptime():
    boot_time = psutil.boot_time()
    now = time.time()
    uptime_seconds = int(now - boot_time)
    days = uptime_seconds // 86400
    hours = (uptime_seconds % 86400) // 3600
    minutes = (uptime_seconds % 3600) // 60
    seconds = uptime_seconds % 60
    return days, hours, minutes, seconds

# 获取 CPU 使用率
def get_cpu_usage(interval=0.1):
    return psutil.cpu_percent(interval=interval)

# 获取内存使用情况
def get_memory_usage():
    memory = psutil.virtual_memory()
    used = memory.used // (1024 ** 2)  # 转为MB
    total = memory.total // (1024 ** 2)  # 转为MB
    percent = memory.percent
    return used, total, percent

# 获取 Swap 使用情况
def get_swap_usage():
    swap = psutil.swap_memory()
    used = swap.used // (1024 ** 2)  # 转为MB
    total = swap.total // (1024 ** 2)  # 转为MB
    percent = swap.percent
    return used, total, percent

# 获取磁盘使用情况
def get_disk_usage():
    disk_path = 'C:\\' if os.name == 'nt' else '/'
    disk = psutil.disk_usage(disk_path)
    used = disk.used // (1024 ** 3)  # 转为GB
    total = disk.total // (1024 ** 3)  # 转为GB
    percent = disk.percent
    return used, total, percent

# 系统信息获取
def get_system_info():
    days, hours, minutes, seconds = get_system_uptime()
    cpu_usage = get_cpu_usage()
    memory_used, memory_total, memory_percent = get_memory_usage()
    swap_used, swap_total, swap_percent = get_swap_usage()
    disk_used, disk_total, disk_percent = get_disk_usage()

    # 格式化所有信息为一个字符串
    system_info = (
        f"系统已运行: {days} 天 {hours} 小时 {minutes} 分钟 {seconds} 秒\n"
        f"CPU: {cpu_usage}%\n"
        f"内存: {memory_used}MB / {memory_total}MB ({memory_percent}%)\n"
        f"Swap: {swap_used}MB / {swap_total}MB ({swap_percent}%)\n"
        f"存储: {disk_used}GB / {disk_total}GB ({disk_percent}%)"
    )
    return system_info

# 创建一个监听器，监听所有消息
chat = on_message(priority=4)

@chat.handle()
async def chat_handle(bot: Bot, event: Event, state: T_State):
    msg = str(event.message)
    
    # 如果消息包含“在吗”，回复系统信息
    if "在吗" in msg:
        system_info = get_system_info()
        await bot.send(event, system_info)

chat = on_message(rule=to_me(), priority=3)
@chat.handle()
async def chat_handle(bot: Bot, event: Event, state: T_State):
    msg = str(event.message)
    try:
        # 实例化一个认证对象，入参需要传入腾讯云账户 SecretId 和 SecretKey，此处还需注意密钥对的保密
        # 代码泄露可能会导致 SecretId 和 SecretKey 泄露，并威胁账号下所有资源的安全性。以下代码示例仅供参考，建议采用更安全的方式来使用密钥，请参见：https://cloud.tencent.com/document/product/1278/85305
        # 密钥可前往官网控制台 https://console.cloud.tencent.com/cam/capi 进行获取
        cred = credential.Credential("1", "2")
        # 实例化一个http选项，可选的，没有特殊需求可以跳过
        httpProfile = HttpProfile()
        httpProfile.endpoint = "hunyuan.tencentcloudapi.com"

        # 实例化一个client选项，可选的，没有特殊需求可以跳过
        clientProfile = ClientProfile()
        clientProfile.httpProfile = httpProfile
        # 实例化要请求产品的client对象,clientProfile是可选的
        client = hunyuan_client.HunyuanClient(cred, "", clientProfile)

        # 实例化一个请求对象,每个接口都会对应一个request对象
        req = models.ChatCompletionsRequest()
        params = {
            "Model": "hunyuan-lite",
            "Messages": [
                {
                    "Role": "user",
                    "Content": msg
                }
            ]
        }
        req.from_json_string(json.dumps(params))

        # 返回的resp是一个ChatCompletionsResponse的实例，与请求对象对应
        resp = client.ChatCompletions(req)
        # 输出json格式的字符串回包
        if isinstance(resp, types.GeneratorType):  # 流式响应
            for event in resp:
                print(event)
        else:  # 非流式响应
            response_data = json.loads(resp.to_json_string())
            message_content = response_data.get("Choices", [{}])[0].get("Message", {}).get("Content", "")
            print(message_content)


    except Exception as e:
        message_content = "抱歉，我无法回答这个问题。"
        print(f"Error in send_message: {e}")
    msg_list =[]
    msg_list.append(
        {
            "type": "node",
            "data": {
                "name": "1",
                "uin": event.self_id,
                "content": message_content
                }
            }
        )
    await bot.send_group_forward_msg(group_id = event.group_id, messages = msg_list)