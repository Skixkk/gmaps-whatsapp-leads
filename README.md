# gmaps-whatsapp-leads skill

## 流程

### 提示用户把 api key 从 [serpapi](https://serpapi.com/) 获取 api key

### 如果是使用 claude code

- 创建 .env 文件在 .claude\skills\gmaps-whatsapp-leads 文件夹下，其他 agent 在对应的位置skill 下进行创建即可

### 将 api key 放在 .env 中

### 修改 api key 也在 .env 中修改

### 询问是否创建虚拟环境 .venv 或 直接使用全局环境

检测 电脑安装 的python 位置和版本，优先使用 python12，python13(如果用户选择其他版本，出现报错，提示用户 使用 python 12 运行)

- 是：创建 虚拟环境 是则 `pip install virtualenv` 然后在项目目录 创建 虚拟环境
- 否：使用全局环境运行 python

安装依赖：

`pip install -r requirements.txt`

### 先查找数据

使用脚本：

### 先获取数据

为了让用户节省 用量/降低费用，先运行脚本`web-search\webbrowser-open-web.py`使用默认浏览器打开:

google map: 右键查找 纬度 精度 和 z值/m值

whatsapp: 扫码登录 WhatsApp 后续自动化 WhatsApp 均再 WhatsApp 网页上使用

### 再导出数据

用户第一次使用次skill的时候，提示用户每使用均花费 [serpapi](https://serpapi.com/) 额度，目前每月免费250次免费搜索，如果付费，可访问 [serpapi-planning](https://serpapi.com/change-plan)  ，提示用户定期 更换token保证安全，防止出现异常调用的情况

导出数据

- google map data: `get-data\google_map_to_path_csv.py`
- google search data: `get-data\SerpApi-search.py`

使用这两个脚本，后面做成 skill 的时候需要将路径和命名规范化修改后放在 `.claude\skills` 下的脚本文件夹

### 发送 模板信息给 对应手机号并将没有联系到的联系人进行导出，提供给用户名单，便于业务处理

将 google map data: `get-data\google_map_to_path_csv.py` 导出的按月份分文件夹的数据

创建选择，让用户选择使用哪个 文件夹内的哪个数据，`get-data\dist\data` 下提供了部分数据用于创建skill 时候的数据学习

将用户选择的 csv 中的 数据 `title,phone`,转换成 `name,phone_number,reminder_time` 提取到 `send-msg\dist\data` 同样按月份分类名称加后缀 `_send`，
`reminder_time`时间，读取当前时间为`{HH:mm}`,提供用户选择：

- 2min
- 5min
- 15min
- 自定义时间（今日内且为今日未过时间）

后基于`send-msg\scheduled-times.py`发送，同时提示用户进行选择Q

- {name}用户，是否有 whatsApp 账号

- 有，则记录为有效用户
- 无，则记录为WhatsApp无此用户

并将导出的 两组 放在 `send-msg\dist\output`下，按月份保存， csv 分别命名添加后缀 `_{unable}` 或 `_{avtive}`

之后将获得的数据绝对路径给到用户，去检查

提示用户到 Excel-数据-从文本/CSV 中，将路径粘贴进去，选择对应的 csv 即可在 excel 0中查看，如果有问题 提供用户 [CSV文件在Excel中打开-教程](https://blog.csdn.net/wyxtx/article/details/134428001)

### 另外，创建 `/` 命令

- `send-msg\scheduled-times.py` 发送消息维护老用户/推送信息
- `send-msg\send_to_group.py` 发送信息到群聊
- `send-msg\send-image.py` 发送图片给某位用户
- `send-msg\send-msg-csv.py` 从csv中批量发送 信息 给 WhatsApp 用户
