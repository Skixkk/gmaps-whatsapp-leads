import serpapi
import csv
import os
from dotenv import load_dotenv

"""
这是google搜索 api
以后可以使用
"""

# 加载当前目录下的 .env 文件
load_dotenv()

# 从环境变量读取 API Key，读取失败则抛出明确提示
api_key = os.getenv("SERPAPI_API_KEY")
if not api_key:
    raise ValueError("未读取到 SERPAPI_API_KEY，请检查 .env 文件是否配置正确")

# 初始化 SerpApi 客户端
client = serpapi.Client(
    api_key=api_key
)

# 执行 Google 搜索
results = client.search({
    "q": "Coffee",
    "location": "Austin, Texas, United States",
    "hl": "en",
    "gl": "us",
    "google_domain": "google.com"
})

# 提取自然搜索结果列表（无结果则返回空列表）
organic_results = results.get("organic_results", [])

# CSV 配置：文件名 + 导出字段
csv_filename = "../dist/data/google_coffee_organic_results.csv"
export_fields = [
    "position",  # 搜索排名
    "title",  # 结果标题
    "link",  # 目标页面链接
    "displayed_link",  # 搜索结果显示的短链接
    "snippet",  # 摘要片段
    "source"  # 网站来源
]

# 写入 CSV 文件（utf-8-sig 兼容 Excel 打开不乱码）
with open(csv_filename, mode="w", newline="", encoding="utf-8-sig") as f:
    writer = csv.DictWriter(f, fieldnames=export_fields)
    writer.writeheader()

    for item in organic_results:
        # 逐层提取字段，缺失字段填充空字符串
        source_info = item.get("about_this_result", {}).get("source", {})
        row = {
            "position": item.get("position", ""),
            "title": item.get("title", ""),
            "link": item.get("link", ""),
            "displayed_link": item.get("displayed_link", ""),
            "snippet": item.get("snippet", ""),
            "source": source_info.get("name", "")
        }
        writer.writerow(row)

print(f"导出完成！文件：{csv_filename}，共 {len(organic_results)} 条结果")