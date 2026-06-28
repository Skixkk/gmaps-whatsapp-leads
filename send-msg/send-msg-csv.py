import pywhatkit
import pandas as pd
import time

try:
    # 读取联系人信息，强制指定电话号码列为字符串类型，保留+号与完整格式
    df = pd.read_csv("contacts.csv", dtype={"phone_number": str})

    for index, row in df.iterrows():
        name = row['name']
        # 显式转为字符串，去除首尾空格
        phone_number = str(row['phone_number']).strip()
        reminder_time_str = row['reminder_time']  # 格式如 "HH:MM"

        # 解析时间
        hour, minute = map(int, reminder_time_str.split(':'))

        message = f"Hi {name}，这是一个来自系统的提醒！"

        print(f"设定给 {name} ({phone_number}) 的提醒：{hour:02d}:{minute:02d}")

        # 发送调度：wait_time为打开页面后等待发送的秒数，tab_close发送后自动关闭标签页
        pywhatkit.sendwhatmsg(
            phone_no=phone_number,
            message=message,
            time_hour=hour,
            time_min=minute,
            wait_time=15,
            tab_close=True,
            close_time=3
        )
        print(f"{name} 的提醒已排程。")
        time.sleep(10)  # 间隔避免请求过快

    print("所有提醒已调度完成！")

except FileNotFoundError:
    print("错误：找不到 contacts.csv 文件。请确保联系人文件在正确目录下")
except pd.errors.EmptyDataError:
    print("错误：contacts.csv 文件是空的。")
except Exception as e:
    print(f"Error occurred: {e}")
