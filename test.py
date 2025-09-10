# # 安装依赖 pip3 install requests html5lib bs4 schedule
#
# import time
# import requests
# import json
# import schedule
# from bs4 import BeautifulSoup
#
# # 从测试号信息获取（请自行替换为你自己的）
# appID = "wxfbe89da0d2a07d8c"
# appSecret = "04a626b0f97c915b24e7e5a26ec7bd8e"
# openId = "oMWsX2KFXQR-9ozM36fI_3Is9wOg"
#
# # 模板 ID（确认与你公众号里的一致）
# weather_template_id = "0AOjNs8PvVbiKXI4rpT0Fp-APIvm273FjXqqpFHuVIU"
# timetable_template_id = "HORJJYNnEVEZ8nczZAbzqrxUODhoBAD5lBbqdr1sx3U"
#
# UA = {
#     "User-Agent": (
#         "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
#         "AppleWebKit/537.36 (KHTML, like Gecko) "
#         "Chrome/122.0.0.0 Safari/537.36"
#     )
# }
# JSON_HEADERS = {"Content-Type": "application/json; charset=utf-8"}
#
# def get_weather(my_city: str):
#     """从 weather.com.cn 抓城市当天预报，返回 (city, '低—高摄氏度', 天气现象, 风向风力) 或 None"""
#     urls = [
#         "http://www.weather.com.cn/textFC/hb.shtml",
#         "http://www.weather.com.cn/textFC/db.shtml",
#         "http://www.weather.com.cn/textFC/hd.shtml",
#         "http://www.weather.com.cn/textFC/hz.shtml",
#         "http://www.weather.com.cn/textFC/hn.shtml",
#         "http://www.weather.com.cn/textFC/xb.shtml",
#         "http://www.weather.com.cn/textFC/xn.shtml",
#     ]
#     for url in urls:
#         try:
#             resp = requests.get(url, headers=UA, timeout=10)
#             resp.encoding = "utf-8"
#             text = resp.text
#         except Exception as e:
#             print(f"[get_weather] 请求失败 {url}: {e}")
#             continue
#
#         soup = BeautifulSoup(text, "html5lib")
#         div_conMidtab = soup.find("div", class_="conMidtab")
#         if not div_conMidtab:
#             # 页面结构偶尔变动
#             continue
#         tables = div_conMidtab.find_all("table")
#         for table in tables:
#             trs = table.find_all("tr")
#             if len(trs) <= 2:
#                 continue
#             for tr in trs[2:]:
#                 tds = tr.find_all("td")
#                 # 防御：长度不足直接跳
#                 if len(tds) < 8:
#                     continue
#                 try:
#                     # 省会与地级市列结构略不同，原逻辑用倒序索引
#                     city_td = tds[-8]
#                     this_city = next(city_td.stripped_strings)
#                 except Exception:
#                     continue
#
#                 if this_city == my_city:
#                     try:
#                         high_temp_td = tds[-5]
#                         low_temp_td = tds[-2]
#                         weather_type_day_td = tds[-7]
#                         weather_type_night_td = tds[-4]
#                         wind_td_day = tds[-6]
#                         wind_td_night = tds[-3]
#
#                         high_temp = next(high_temp_td.stripped_strings, "-")
#                         low_temp = next(low_temp_td.stripped_strings, "-")
#                         weather_typ_day = next(weather_type_day_td.stripped_strings, "-")
#                         weather_type_night = next(weather_type_night_td.stripped_strings, "-")
#
#                         # 可能只有一段风向/风力，取前两个字符串，不足则补 "--"
#                         wind_day_parts = list(wind_td_day.stripped_strings)
#                         wind_night_parts = list(wind_td_night.stripped_strings)
#                         wind_day = "".join(wind_day_parts[:2]) if wind_day_parts else "--"
#                         wind_night = "".join(wind_night_parts[:2]) if wind_night_parts else "--"
#
#                         temp = f"{low_temp}——{high_temp}摄氏度" if high_temp != "-" else f"{low_temp}摄氏度"
#                         weather_typ = weather_typ_day if weather_typ_day != "-" else weather_type_night
#                         wind = wind_day if wind_day != "--" else wind_night
#                         return this_city, temp, weather_typ, wind
#                     except Exception as e:
#                         print(f"[get_weather] 解析 {my_city} 行失败: {e}")
#                         return None
#     return None
#
#
# def get_access_token():
#     url = (
#         "https://api.weixin.qq.com/cgi-bin/token"
#         f"?grant_type=client_credential&appid={appID.strip()}&secret={appSecret.strip()}"
#     )
#     try:
#         response = requests.get(url, timeout=10).json()
#     except Exception as e:
#         print(f"[get_access_token] 请求失败: {e}")
#         return None
#
#     print("[get_access_token]", response)
#     access_token = response.get("access_token")
#     if not access_token:
#         print("[get_access_token] 获取失败，请检查 appID/appSecret 是否正确，或是否为测试号/服务号权限。")
#     return access_token
#
#
# def get_daily_love():
#     """优先尝试 lovelive API；失败则用一言；还失败返回固定文案。"""
#     # 1) 主接口
#     try:
#         r = requests.get("https://api.lovelive.tools/api/SweetNothings/Serialization/Json", timeout=8)
#         # 某些时候此接口返回空或 HTML，先判断 Content-Type 和内容
#         if r.ok:
#             try:
#                 data = r.json()
#                 if isinstance(data, dict) and "returnObj" in data and data["returnObj"]:
#                     return str(data["returnObj"][0]).strip()
#             except Exception:
#                 pass
#     except Exception as e:
#         print(f"[get_daily_love] 主接口失败: {e}")
#
#     # 2) 备用接口：一言
#     try:
#         r2 = requests.get("https://v1.hitokoto.cn/?encode=json", timeout=8)
#         if r2.ok:
#             data2 = r2.json()
#             if "hitokoto" in data2:
#                 return str(data2["hitokoto"]).strip()
#     except Exception as e:
#         print(f"[get_daily_love] 备用接口失败: {e}")
#
#     # 3) 最终兜底
#     return "愿你与世界温柔相拥。"
#
#
# def send_weather(access_token, weather):
#     if not access_token:
#         print("[send_weather] 无 access_token")
#         return
#     if not weather:
#         print("[send_weather] 未获取到天气数据")
#         return
#
#     import datetime
#     today = datetime.date.today()
#     today_str = today.strftime("%Y年%m月%d日")
#
#     body = {
#         "touser": openId.strip(),
#         "template_id": weather_template_id.strip(),
#         "url": "https://weixin.qq.com",
#         "data": {
#             "date": {"value": today_str},
#             "region": {"value": weather[0]},
#             "weather": {"value": weather[2]},
#             "temp": {"value": weather[1]},
#             "wind_dir": {"value": weather[3]},
#             "today_note": {"value": get_daily_love()},
#         },
#     }
#     url = f"https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={access_token}"
#     try:
#         resp = requests.post(url, headers=JSON_HEADERS, json=body, timeout=10)
#         print("[send_weather]", resp.text)
#     except Exception as e:
#         print(f"[send_weather] 发送失败: {e}")
#
#
# def send_timetable(access_token, message):
#     if not access_token:
#         print("[send_timetable] 无 access_token")
#         return
#     body = {
#         "touser": openId.strip(),
#         "template_id": timetable_template_id.strip(),
#         "url": "https://weixin.qq.com",
#         "data": {
#                 "message": {"value": str(message)}
#         },
#     }
#     url = f"https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={access_token}"
#     try:
#         resp = requests.post(url, headers=JSON_HEADERS, json=body, timeout=10)
#         print("[send_timetable]", resp.text)
#     except Exception as e:
#         print(f"[send_timetable] 发送失败: {e}")
#
#
# def weather_report(city):
#     access_token = get_access_token()
#     weather = get_weather(city)
#     print(f"天气信息： {weather}")
#     send_weather(access_token, weather)
#
#
# def timetable(message):
#     access_token = get_access_token()
#     send_timetable(access_token, message)
#
#
# if __name__ == "__main__":
#     # 立即跑一次
#     weather_report("咸宁")
#
#     # # 定时任务示例（按需开启）
#     schedule.every().day.at("08:00").do(weather_report, "咸宁")
#     schedule.every().monday.at("8:01").do(timetable, "第二教学楼十分钟后开始英语课")
#     while True:
#         schedule.run_pending()
#         time.sleep(1)

# 安装依赖：pip3 install requests html5lib bs4 schedule
# pip3 install requests html5lib bs4 schedule

import time
import requests
from bs4 import BeautifulSoup
import schedule
import datetime
from typing import Dict, List, Optional

# ====== 你的公众号配置（请替换） ======
appID = "wxfbe89da0d2a07d8c"
appSecret = "04a626b0f97c915b24e7e5a26ec7bd8e"
openId = "oMWsX2LrSc_lRo10RwJ0lt8kP6Iw"

# 模板 ID（必须与你公众号里的一致）
weather_template_id = "0AOjNs8PvVbiKXI4rpT0Fp-APIvm273FjXqqpFHuVIU"
timetable_template_id = "HORJJYNnEVEZ8nczZAbzqrxUODhoBAD5lBbqdr1sx3U"

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"}
JSON_HEADERS = {"Content-Type": "application/json; charset=utf-8"}

# ====== 推送时间与城市 ======
WEATHER_CITY = "咸宁"
WEATHER_PUSH_TIME = "07:55"
TIMETABLE_PUSH_TIME = "07:56"
SKIP_WHEN_EMPTY = False  # 当天无课时是否跳过不推送

# —— 每条卡片建议的最大“字符”长度（中文按1计），超过会加省略号 —— #
CARD_CHAR_LIMIT = 26   # 经验值：24~28 更稳；过长仍会被微信省略
LOVE_FIELD_CHAR_LIMIT = 80

# ====== 学期配置：用于自动计算“第几周” ======
TERM_START_DATE = datetime.date(2025, 9, 1)
CN_WEEK = {1:"一",2:"二",3:"三",4:"四",5:"五",6:"六",7:"日"}

# ====== 课程名/地点缩写（可按需增删） ======
COURSE_NAME_SHORT = {
    "习近平新时代中国特色社会主义思想概论": "习思想",
    "临床医学概要": "临床概要",
    "口腔内科学": "口腔内科",
    "全口义齿工艺技术": "全口义齿",
    "口腔组织病理学": "组病理",
    "口腔医学美学": "医学美学",
    "口腔正畸学": "正畸学",
    "口腔颌面影像学": "影像学",
    "创业基础": "创业基础",
}
ROOM_SHORT = {
    "A-4-阶梯2": "A4阶2",
    "A-4-阶梯3": "A4阶3",
    "A-4-503": "A4-503",
    "A-1-302": "A1-302",
    "A-1-201": "A1-201",
    "A-1-202": "A1-202",
    "A-1-203": "A1-203",
    "A-1-205": "A1-205",
    "A-1-304/305": "A1-304/5",
    "SA-1-405": "SA1-405",
    "SA-1-407": "SA1-407",
    "SA-1-307": "SA1-307",
}

# ====== 课表 ======
WEEKLY_TIMETABLE: Dict[int, List[Dict[str, str]]] = {
    1: [  # 周一
        {"periods": "5-6", "name": "习近平新时代中国特色社会主义思想概论", "loc": "A-4-阶梯2", "weeks": "1-16"},
        {"periods": "7-8", "name": "口腔内科学", "loc": "A-1-302", "weeks": "2-14(双)"},
    ],
    2: [  # 周二
        {"periods": "1-2", "name": "口腔正畸学", "loc": "A-1-202", "weeks": "1-12（单）"},
        {"periods": "1-2", "name": "全口义齿工艺技术", "loc": "A-1-205", "weeks": "1-12（双）"},
        {"periods": "5-8", "name": "全口义齿工艺技术", "loc": "SA-1-407", "weeks": "1-15"},
        {"periods": "9-10", "name": "临床医学概要", "loc": "A-1-203", "weeks": "1-14"},
    ],
    3: [  # 周三
        {"periods": "1-2", "name": "临床医学概要", "loc": "A-4-503", "weeks": "1-14"},
        {"periods": "3-4", "name": "全口义齿工艺技术", "loc": "A-1-205", "weeks": "2-12"},
        {"periods": "7-8", "name": "口腔内科学", "loc": "A-1-302", "weeks": "2-14"},
        {"periods": "9-10", "name": "口腔正畸学", "loc": "A-1-201", "weeks": "1-11"},
    ],
    4: [  # 周四
        {"periods": "1-2", "name": "口腔组织病理学", "loc": "A-1-304/305", "weeks": "1-12"},
        {"periods": "3-4", "name": "口腔医学美学", "loc": "A-1-302", "weeks": "1-16"},
        {"periods": "5-8", "name": "口腔内科学", "loc": "SA-1-405", "weeks": "1-13（单）"},
        {"periods": "5-8", "name": "口腔正畸学", "loc": "SA-1-307", "weeks": "2-16（双）"},
        {"periods": "9-10", "name": "创业基础", "loc": "A-4-阶梯3", "weeks": "1-16"},
    ],
    5: [], 6: [], 7: [],
}

# -------------------- 小工具 --------------------
def _single_line(s: str) -> str:
    return " ".join(s.replace("\r", " ").replace("\n", " ").split())

def _clip_cn(s: str, limit: int) -> str:
    return s if len(s) <= limit else (s[:max(0, limit-1)] + "…")

def short_name(name: str) -> str:
    return COURSE_NAME_SHORT.get(name, name)

def short_room(loc: str) -> str:
    return ROOM_SHORT.get(loc, loc)

def first_period_num(periods: str) -> int:
    try:
        return int(periods.split("-")[0])
    except:
        return 99

# ============ 天气 ============

def get_weather(my_city: str):
    urls = [
        "http://www.weather.com.cn/textFC/hb.shtml","http://www.weather.com.cn/textFC/db.shtml",
        "http://www.weather.com.cn/textFC/hd.shtml","http://www.weather.com.cn/textFC/hz.shtml",
        "http://www.weather.com.cn/textFC/hn.shtml","http://www.weather.com.cn/textFC/xb.shtml",
        "http://www.weather.com.cn/textFC/xn.shtml",
    ]
    for url in urls:
        try:
            resp = requests.get(url, headers=UA, timeout=10)
            resp.encoding = "utf-8"
        except Exception as e:
            print(f"[get_weather] 请求失败 {url}: {e}")
            continue
        soup = BeautifulSoup(resp.text, "html5lib")
        div = soup.find("div", class_="conMidtab")
        if not div: continue
        for table in div.find_all("table"):
            trs = table.find_all("tr")
            if len(trs) <= 2: continue
            for tr in trs[2:]:
                tds = tr.find_all("td")
                if len(tds) < 8: continue
                try:
                    this_city = next(tds[-8].stripped_strings)
                except Exception:
                    continue
                if this_city == my_city:
                    try:
                        high = next(tds[-5].stripped_strings, "-")
                        low  = next(tds[-2].stripped_strings, "-")
                        dayw = next(tds[-7].stripped_strings, "-")
                        ngtw = next(tds[-4].stripped_strings, "-")
                        wind_day = "".join(list(tds[-6].stripped_strings)[:2]) or "--"
                        wind_ngt = "".join(list(tds[-3].stripped_strings)[:2]) or "--"
                        temp = f"{low}——{high}摄氏度" if high != "-" else f"{low}摄氏度"
                        wtyp = dayw if dayw != "-" else ngtw
                        wind = wind_day if wind_day != "--" else wind_ngt
                        return this_city, temp, wtyp, wind
                    except Exception as e:
                        print(f"[get_weather] 解析 {my_city} 行失败: {e}")
                        return None
    return None

def get_access_token() -> Optional[str]:
    url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={appID.strip()}&secret={appSecret.strip()}"
    try:
        response = requests.get(url, timeout=10).json()
    except Exception as e:
        print(f"[get_access_token] 请求失败: {e}")
        return None
    print("[get_access_token]", response)
    token = response.get("access_token")
    if not token:
        print("[get_access_token] 获取失败，请检查 appID/appSecret/权限。")
    return token

import random

def http_get_json(url: str, timeout: int = 6, retries: int = 2):
    """简单重试的 GET JSON。返回 dict/列表 或 None。"""
    last_err = None
    for _ in range(max(1, retries)):
        try:
            r = requests.get(url, headers=UA, timeout=timeout)
            if r.ok:
                # 有些接口实际返回纯文本，也尝试 json 解析失败时忽略
                try:
                    return r.json()
                except Exception:
                    return None
        except Exception as e:
            last_err = e
            time.sleep(0.3)
    if last_err:
        print(f"[http_get_json] {url} 失败: {last_err}")
    return None


def get_daily_love():
    """
    返回一行的“情话”：多源兜底 + 单行化 + 裁剪，避免模板字段截断。
    源序：lovelive → 一言 → uomg土味情话 → 本地备选。
    """
    # 1) lovelive
    try:
        data = http_get_json("https://api.lovelive.tools/api/SweetNothings/Serialization/Json", timeout=6, retries=2)
        if isinstance(data, dict):
            arr = data.get("returnObj") or data.get("data")
            if arr:
                text = str(arr[0]).strip()
                text = " ".join(text.replace("\r", " ").replace("\n", " ").split())
                text = text.replace("\u3000", " ")  # 全角空格
                text = text.replace("——", "-")
                result = text
                print("[get_daily_love] 使用 lovelive")
                return result if len(result) <= LOVE_FIELD_CHAR_LIMIT else (result[:LOVE_FIELD_CHAR_LIMIT - 1] + "…")
    except Exception as e:
        print(f"[get_daily_love] lovelive 异常: {e}")

    # 2) 一言
    try:
        data = http_get_json("https://v1.hitokoto.cn/?encode=json", timeout=6, retries=2)
        if isinstance(data, dict) and data.get("hitokoto"):
            text = str(data["hitokoto"]).strip()
            text = " ".join(text.replace("\r", " ").replace("\n", " ").split())
            result = text
            print("[get_daily_love] 使用 hitokoto")
            return result if len(result) <= LOVE_FIELD_CHAR_LIMIT else (result[:LOVE_FIELD_CHAR_LIMIT - 1] + "…")
    except Exception as e:
        print(f"[get_daily_love] hitokoto 异常: {e}")

    # 3) UOMG 土味情话
    try:
        data = http_get_json("https://api.uomg.com/api/rand.qinghua?format=json", timeout=6, retries=2)
        if isinstance(data, dict):
            # 有的字段叫 'content' 或 'respond'
            text = data.get("content") or data.get("respond") or ""
            if text:
                text = str(text).strip()
                text = " ".join(text.replace("\r", " ").replace("\n", " ").split())
                result = text
                print("[get_daily_love] 使用 uomg")
                return result if len(result) <= LOVE_FIELD_CHAR_LIMIT else (result[:LOVE_FIELD_CHAR_LIMIT - 1] + "…")
    except Exception as e:
        print(f"[get_daily_love] uomg 异常: {e}")

    # 4) 最终本地兜底（随机挑一句）
    fallback_pool = [
        "愿你与世界温柔相拥。",
        "今天也要元气满满呀！",
        "把喜欢装进口袋，慢慢发光给你看。",
        "你一笑，山河都温柔了。",
        "愿每个清晨都被你温柔叫醒。",
        "遇见你，满天的星都亮了。",
    ]
    text = random.choice(fallback_pool)
    print("[get_daily_love] 使用本地兜底")
    return text if len(text) <= LOVE_FIELD_CHAR_LIMIT else (text[:LOVE_FIELD_CHAR_LIMIT - 1] + "…")

def send_weather(access_token: str, weather):
    if not access_token or not weather:
        print("[send_weather] 缺少 access_token 或天气数据")
        return
    today_str = datetime.date.today().strftime("%Y年%m月%d日")
    body = {
        "touser": openId.strip(),
        "template_id": weather_template_id.strip(),
        "url": "https://weixin.qq.com",
        "data": {
            "date": {"value": today_str},
            "region": {"value": weather[0]},
            "weather": {"value": weather[2]},
            "temp": {"value": weather[1]},
            "wind_dir": {"value": weather[3]},
            "today_note": {"value": get_daily_love()},
        },
    }
    url = f"https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={access_token}"
    try:
        resp = requests.post(url, headers=JSON_HEADERS, json=body, timeout=10)
        print("[send_weather]", resp.text)
    except Exception as e:
        print(f"[send_weather] 发送失败: {e}")

def weather_report(city: str):
    token = get_access_token()
    weather = get_weather(city)
    print(f"天气信息：{weather}")
    send_weather(token, weather)

# ============ 课程表（按课一条卡片，尽量短，不换行） ============

def parse_weeks_rule(rule: str):
    rule = rule.replace("周", "").strip().replace("（","(").replace("）",")")
    parity = None
    if "(单)" in rule or "单" in rule:
        parity = "odd"; rule = rule.replace("(单)","").replace("单","")
    if "(双)" in rule or "双" in rule:
        parity = "even"; rule = rule.replace("(双)","").replace("双","")
    if "-" in rule:
        a,b = rule.split("-",1)
        return {"type":"range","start":int(a),"end":int(b),"parity":parity,"list":set()}
    lst = {int(x) for x in rule.split(",") if x.strip().isdigit()}
    return {"type":"list","start":0,"end":0,"parity":parity,"list":lst}

def is_week_hit(current_week: int, rule: str) -> bool:
    r = parse_weeks_rule(rule)
    if r["type"]=="range":
        ok = r["start"] <= current_week <= r["end"]
    else:
        ok = current_week in r["list"]
    if r["parity"] == "odd":  ok = ok and (current_week % 2 == 1)
    if r["parity"] == "even": ok = ok and (current_week % 2 == 0)
    return ok

def get_current_week(today: Optional[datetime.date] = None) -> int:
    if not today: today = datetime.date.today()
    delta = (today - TERM_START_DATE).days
    return delta // 7 + 1 if delta >= 0 else 0

def build_today_items(today: Optional[datetime.date] = None):
    if not today: today = datetime.date.today()
    wd = today.isoweekday()
    week_no = get_current_week(today)
    items = WEEKLY_TIMETABLE.get(wd, [])
    hit = [it for it in items if is_week_hit(week_no, it["weeks"])]
    hit.sort(key=lambda x: first_period_num(x["periods"]))
    return wd, week_no, hit

def make_course_line(it: Dict[str,str]) -> str:
    """生成尽量短的一行：'5-6节 习思想 A4阶2 1-16周' 并裁剪到 CARD_CHAR_LIMIT"""
    name = short_name(it["name"])
    loc  = short_room(it["loc"])
    txt  = f"{it['periods']}节 {name} {loc} {it['weeks']}周"
    txt  = _single_line(txt)
    return _clip_cn(txt, CARD_CHAR_LIMIT)

def send_timetable_cards(access_token: str, title: str, lines: List[str]):
    """按课一条卡片发送；第1条发送标题，其余每条一门课"""
    if not access_token:
        print("[send_timetable] 无 access_token"); return
    url = f"https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={access_token}"

    cards = [title] + lines  # 第一条是标题
    total = len(cards)
    for idx, part in enumerate(cards, start=1):
        body = {
            "touser": openId.strip(),
            "template_id": timetable_template_id.strip(),
            "url": "https://weixin.qq.com",  # 可替换为你自己的全文链接
            "data": {"message": {"value": f"({idx}/{total}) {part}"}},
        }
        try:
            resp = requests.post(url, headers=JSON_HEADERS, json=body, timeout=10)
            print("[send_timetable]", f"{idx}/{total}", part, resp.text)
            time.sleep(0.35)  # 轻微间隔，避开频率限制
        except Exception as e:
            print(f"[send_timetable] 发送失败: {e}")

def timetable_daily_push():
    token = get_access_token()
    today = datetime.date.today()
    wd, week_no, hit = build_today_items(today)
    title = f"{today.strftime('%Y年%m月%d日')}（周{CN_WEEK[wd]}）第{week_no}周课程安排"
    if not hit:
        if SKIP_WHEN_EMPTY:
            print("[timetable] 今日无课，跳过推送。"); return
        send_timetable_cards(token, title, ["今日无课"])
        return

    # 逐课生成短行
    lines = [make_course_line(it) for it in hit]
    send_timetable_cards(token, title, lines)

# ============ 定时任务入口 ============

if __name__ == "__main__":
    # 立即各跑一次（便于验证）
    weather_report(WEATHER_CITY)
    timetable_daily_push()

    # # 如需定时，取消注释
    # schedule.every().day.at(WEATHER_PUSH_TIME).do(weather_report, WEATHER_CITY)
    # schedule.every().day.at(TIMETABLE_PUSH_TIME).do(timetable_daily_push)
    # while True:
    #     schedule.run_pending()
    #     time.sleep(1)
