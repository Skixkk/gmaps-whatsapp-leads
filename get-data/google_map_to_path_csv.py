import os
import csv
from datetime import datetime
from dotenv import load_dotenv
import serpapi

# 加载 .env 配置文件，自动读取环境变量
load_dotenv()


class GoogleMapSearcher:
    """
    Google Maps 商户搜索与导出工具类
    """

    # CSV导出字段定义（与输出列一一对应）
    CSV_FIELDS = [
        "position", "title", "place_id", "rating", "reviews_count",
        "price_level", "extracted_price", "business_type", "address", "country",
        "open_state", "latitude", "longitude", "phone", "website",
        "user_review"
    ]

    def __init__(self):
        """
        初始化搜索客户端，API Key 强制从 .env 文件的 API_KEY 变量读取，不支持参数传入
        :raises ValueError: 密钥为空时抛出异常
        """
        self.api_key = os.getenv("API_KEY")
        if not self.api_key:
            raise ValueError("SerpAPI API Key 未配置，请在项目根目录 .env 文件中设置 API_KEY 变量")

        self.client = serpapi.Client(api_key=self.api_key)
        self.raw_results = None
        self.local_results = []

    def search(self, query: str, location_ll: str, start: int = None) -> list:
        """
        执行 Google Maps 商户搜索
        :param query: 搜索关键词
        :param location_ll: 经纬度+缩放级别，格式: @lat,lng,zoom
        :param start: 分页偏移量，None表示第一页（前20条），可选值：20、40、60... 建议不超过60，后续结果重复率较高
        :return: 商户结果列表
        """
        params = {
            "engine": "google_maps",
            "q": query,
            "ll": location_ll,
            "type": "search",
        }
        # 仅当传入有效start时才添加分页参数
        if start is not None:
            params["start"] = start

        self.raw_results = self.client.search(params)
        self.local_results = self.raw_results.get("local_results", [])
        return self.local_results

    def export_to_csv(self, keyword: str, start_value: int, location_label: str, base_dir: str = "dist//data") -> str:
        """
        将搜索结果按年月分目录导出为 CSV 文件
        目录规则: dist/data/yyyy-MM/
        文件规则: yyyy_MM_dd_HH_mm_ss_<keyword>_<start>_<地域标识>.csv
        :param keyword: 文件名关键词
        :param start_value: 分页偏移量数值，用于文件名拼接
        :param location_label: 地域标识（用户输入名称或经纬度），用于文件名拼接
        :param base_dir: 基础根目录，默认 dist/data
        :return: 最终保存的完整文件路径
        :raises RuntimeError: 无搜索结果时抛出异常
        """
        if not self.local_results:
            raise RuntimeError("暂无搜索结果，请先调用 search() 方法获取数据")

        # 1. 生成时间维度的目录名与文件名前缀
        now = datetime.now()
        month_dir_name = now.strftime("%Y-%m")  # 文件夹：yyyy-MM
        file_time_prefix = now.strftime("%Y_%m_%d_%H_%M_%S")  # 文件名时间前缀

        # 2. 构建目标目录并递归创建（已存在则跳过）
        target_dir = os.path.join(base_dir, month_dir_name)
        os.makedirs(target_dir, exist_ok=True)

        # 3. 按指定顺序拼接完整文件名
        file_name = f"{file_time_prefix}_{keyword}_{start_value}_{location_label}.csv"
        full_file_path = os.path.join(target_dir, file_name)

        # 4. 写入 CSV 文件（utf-8-sig 兼容Excel中文不乱码）
        with open(full_file_path, mode="w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=self.CSV_FIELDS)
            writer.writeheader()

            for item in self.local_results:
                gps = item.get("gps_coordinates", {})
                row = {
                    "position": item.get("position"),
                    "title": item.get("title"),
                    "place_id": item.get("place_id"),
                    "rating": item.get("rating"),
                    "reviews_count": item.get("reviews"),
                    "price_level": item.get("price"),
                    "extracted_price": item.get("extracted_price"),
                    "business_type": item.get("type"),
                    "address": item.get("address"),
                    "country": item.get("country"),
                    "open_state": item.get("open_state"),
                    "latitude": gps.get("latitude"),
                    "longitude": gps.get("longitude"),
                    "phone": item.get("phone", ""),
                    "website": item.get("website", ""),
                    "user_review": item.get("user_review", "").strip('"')
                }
                writer.writerow(row)

        return full_file_path


def generate_location_label(location_ll: str, user_input: str) -> str:
    """
    生成文件名中的地域标识
    :param location_ll: 经纬度参数字符串
    :param user_input: 用户输入的地域名称
    :return: 处理后的安全文件名字符串
    """
    user_input = user_input.strip()
    if user_input:
        # 空格替换为下划线，支持中英文UTF-8
        return user_input.replace(' ', '_')
    else:
        # 未输入则从ll参数中提取经纬度，移除@和缩放信息，逗号替换为下划线
        clean_ll = location_ll.lstrip('@')
        lat, lng = clean_ll.split(',')[:2]
        return f"{lat.strip()}_{lng.strip()}"


if __name__ == "__main__":
    # ==================== 基础坐标配置 ====================
    # 搜索中心点经纬度与缩放级别，可自行修改
    location_ll = "@33.98180156974693,-118.2479095654263,15.6z"
    # 示例坐标对应洛杉矶区域: 33.98180156974693, -118.2479095654263

    # ==================== 交互输入区 ====================
    query = input("请输入搜索关键词：").strip()
    if not query:
        print("错误：搜索关键词不能为空，程序退出")
        exit(1)

    location_input = input("请输入地域名称（直接回车将使用经纬度命名，建议使用英文）：")

    start_input = input(
        "请输入分页偏移量start（直接回车默认第一页/前20条，可选值：20、40、60，建议不超过60）："
    ).strip()

    # 处理start参数与异常校验
    if start_input:
        try:
            start = int(start_input)
        except ValueError:
            print("错误：start必须为整数数字，程序退出")
            exit(1)
    else:
        start = None
    # 文件名中统一用数字标识：None对应0（第一页）
    start_value = start if start is not None else 0

    # 生成文件名地域标识 + 关键词格式化（空格转横杠）
    location_label = generate_location_label(location_ll, location_input)
    file_keyword = query.replace(' ', '-')

    # ==================== 执行搜索与导出 ====================
    searcher = GoogleMapSearcher()
    searcher.search(
        query=query,
        location_ll=location_ll,
        start=start
    )

    saved_path = searcher.export_to_csv(
        keyword=file_keyword,
        start_value=start_value,
        location_label=location_label
    )

    print(f"\n执行完成，共导出 {len(searcher.local_results)} 条商户数据")
    print(f"文件已保存至：{saved_path}")

"""
核心修改说明
分页参数动态化
search 方法新增 start 参数，默认 None（对应第一页前 20 条），仅在传入有效值时才添加到请求参数中
输入提示明确标注取值规则：回车 = 第一页，20/40/60 对应后续分页，建议不超过 60
文件名中 None 统一映射为 0，保持命名全数字、语义清晰
地域名称命名规则落地
新增 generate_location_label 工具函数，自动处理两种命名模式
用户输入名称：空格自动替换为下划线，支持中英文 UTF-8
用户未输入（直接回车）：自动从 location_ll 提取经纬度，移除 @和缩放级别，逗号转下划线，保证文件名合法
命名顺序严格遵循：时间前缀_关键词_start值_地域标识.csv
健壮性增强
关键词非空校验
start 参数数字格式异常捕获
关键词空格自动转横杠，避免文件名含空格导致的兼容问题
兼容性保持
保留原有 CSV 字段映射、目录结构、编码格式
类结构与核心搜索逻辑无破坏性变更
跨平台路径拼接与目录自动创建逻辑不变
"""
