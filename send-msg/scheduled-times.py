import pywhatkit
import time

"""
所有账户都要求是可联系用户（适合直接再开发老用户发送）
"""

numbers = ["+1234567890", "+9876543210", "+8617832679310"]
message = "这是一条群发消息"

for number in numbers:
    pywhatkit.sendwhatmsg(
        phone_no=number,
        message=message,
        time_hour=21,
        time_min=38,
        wait_time=15,
        tab_close=True,
        close_time=3,
    )
    time.sleep(30)  # 等待 30s 再发送下一条
