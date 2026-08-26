import os
import time
import glob
from datetime import datetime
from google import genai

# ==========================================
# 網頁模板設定區（集中管理，現代金融科技風格）
# ==========================================

PAGE_TEMPLATE = """\
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>美股市場情報 - {today_str}</title>
    <style>
        :root {{
            --bg-color: #0f172a;
            --card-bg: #1e293b;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --accent: #38bdf8;
            --border: #334155;
            --up: #10b981;
            --down: #ef4444;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "PingFang TC", sans-serif;
            background-color: var(--bg-color);
            color: var(--text-main);
            margin: 0;
            padding: 30px 15px;
            line-height: 1.6;
        }}
        .container {{
            max-width: 900px;
            margin: 0 auto;
            background: var(--card-bg);
            padding: 35px;
            border-radius: 16px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            border: 1px solid var(--border);
        }}
        .back-btn {{
            display: inline-flex;
            align-items: center;
            margin-bottom: 25px;
            color: var(--accent);
            text-decoration: none;
            font-weight: 600;
            font-size: 0.95em;
            transition: transform 0.2s ease;
        }}
        .back-btn:hover {{
            transform: translateX(-4px);
        }}
        h1 {{
            color: var(--text-main);
            font-size: 1.8em;
            margin-top: 0;
            padding-bottom: 15px;
            border-bottom: 1px solid var(--border);
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        /* AI 產出內容的金融卡片樣式 */
        .market-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
            margin: 25px 0;
        }}
        .stock-card {{
            background: #0f172a;
            border-radius: 12px;
            padding: 20px;
            border: 1px solid var(--border);
        }}
        .stock-card h3 {{
            margin: 0 0 15px 0;
            font-size: 1.1em;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .stock-list {{
            list-style: none;
            padding: 0;
            margin: 0;
        }}
        .stock-item {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px 0;
            border-bottom: 1px solid #1e293b;
        }}
        .stock-item:last-child {{
            border-bottom: none;
        }}
        .badge-up {{ color: var(--up); font-weight: bold; }}
        .badge-down {{ color: var(--down); font-weight: bold; }}
        .news-section {{
            background: #0f172a;
            border-radius: 12px;
            padding: 25px;
            border: 1px solid var(--border);
            margin-top: 25px;
        }}
        .news-section h3 {{
            margin-top: 0;
            color: var(--accent);
        }}
        .news-item {{
            margin-bottom: 15px;
            padding-bottom: 15px;
            border-bottom: 1px solid var(--border);
        }}
        .news-item:last-child {{
            margin-bottom: 0;
            padding-bottom: 0;
            border-bottom: none;
        }}
    </style>
</head>
<body>
    <div class="container">
        <a href="index.html" class="back-btn">⬅ 回到市場日報列表</a>
        <h1>📈 美股市場情報：{today_str}</h1>
        <div class="content">{ai_content}</div>
    </div>
</body>
</html>"""

HOMEPAGE_TEMPLATE = """\
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>美股每日動態情報站</title>
    <style>
        :root {{
            --bg-color: #0f172a;
            --card-bg: #1e293b;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --accent: #38bdf8;
            --border: #334155;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "PingFang TC", sans-serif;
            background-color: var(--bg-color);
            color: var(--text-main);
            margin: 0;
            padding: 40px 15px;
        }}
        .container {{
            max-width: 800px;
            margin: 0 auto;
            background: var(--card-bg);
            padding: 35px;
            border-radius: 16px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            border: 1px solid var(--border);
        }}
        h1 {{
            color: var(--text-main);
            font-size: 1.8em;
            margin-top: 0;
            border-bottom: 1px solid var(--border);
            padding-bottom: 15px;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        p.subtitle {{
            color: var(--text-muted);
            font-size: 0.95em;
            margin-bottom: 25px;
        }}
        ul {{
            list-style: none;
            padding: 0;
            margin: 0;
        }}
        li {{
            margin-bottom: 12px;
        }}
        .date-link {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 16px 20px;
            background: #0f172a;
            color: var(--text-main);
            text-decoration: none;
            border-radius: 10px;
            font-weight: 500;
            border: 1px solid var(--border);
            transition: all 0.2s ease;
        }}
        .date-link:hover {{
            background: #1e293b;
            border-color: var(--accent);
            transform: translateX(6px);
            color: var(--accent);
        }}
        .footer {{
            margin-top: 40px;
            font-size: 0.85em;
            color: var(--text-muted);
            text-align: center;
            border-top: 1px solid var(--border);
            padding-top: 20px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 美股每日動態情報站</h1>
        <p class="subtitle">追蹤美股強弱勢股走勢與市場關鍵大事（僅保留最近 5 日紀錄）：</p>
        <ul>
{links_html}
        </ul>
        <div class="footer">
            本站由 Python + GitHub Actions + Google Gemini API 自動化生成
        </div>
    </div>
</body>
</html>"""

# ==========================================
# 邏輯處理區
# ==========================================

def get_ai_content(max_retries=4, base_delay=10):
    """調用 Google GenAI API 生成美股強弱勢股與當日財經大事"""
    client = genai.Client()
    prompt = """你是一位資深美股量化分析師與財經編輯，請用繁體中文整理最近一個美股交易日的市場焦點。
請直接以乾淨的 HTML 標籤結構輸出（僅需 <div> 區塊，不要包含 <html>、<head> 或 <body> 宣告，不要 Markdown 程式碼區塊標記）。

請嚴格按照以下 HTML 結構生成內容：

<div class="market-grid">
    <div class="stock-card">
        <h3 style="color: #10b981;">🚀 漲幅最高 Top 5 焦點股</h3>
        <ul class="stock-list">
            <li class="stock-item"><span><strong>代號</strong> 公司簡稱</span><span class="badge-up">+00.00%</span></li>
            <!-- 列出 5 檔，並附帶 1 句簡短暴漲原因 -->
        </ul>
    </div>
    <div class="stock-card">
        <h3 style="color: #ef4444;">🔻 跌幅最深 Top 5 焦點股</h3>
        <ul class="stock-list">
            <li class="stock-item"><span><strong>代號</strong> 公司簡稱</span><span class="badge-down">-00.00%</span></li>
            <!-- 列出 5 檔，並附帶 1 句簡短重挫原因 -->
        </ul>
    </div>
</div>

<div class="news-section">
    <h3>📌 當日美股核心大事與總經觀點</h3>
    <div class="news-item">
        <strong>1. 重大市場事件 / 總經數據（如 CPI、利率政策、科技巨頭財報等）：</strong>
        <p>重點摘要解析...</p>
    </div>
    <div class="news-item">
        <strong>2. 板塊資金輪動與盤勢結論：</strong>
        <p>重點摘要解析...</p>
    </div>
</div>
"""

    last_error = None
    for attempt in range(1, max_retries + 1):
        try:
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
            )
            # 清理可能夾帶的 markdown 標籤
            content = response.text.replace('```html', '').replace('```', '').strip()
            return content
        except Exception as e:
            last_error = e
            print(f"第 {attempt} 次呼叫失敗: {e}")
            if attempt < max_retries:
                delay = base_delay * (2 ** (attempt - 1))
                print(f"等待 {delay} 秒後重試...")
                time.sleep(delay)
    raise last_error

def process_daily_content():
    today_str = datetime.now().strftime("%Y-%m-%d")
    
    # 1. 生成今天的獨立美股情報文章
    try:
        ai_content = get_ai_content()
    except Exception as e:
        print(f"AI 內容產生失敗, 跳過今日更新: {e}")
        return
        
    page_html = PAGE_TEMPLATE.format(today_str=today_str, ai_content=ai_content)

    # 寫入當天檔案 (例如: 2026-08-26.html)
    with open(f"{today_str}.html", "w", encoding="utf-8") as f:
        f.write(page_html)

    # 2. 抓取所有日期 HTML 檔案（排除 index.html）
    all_files = [f for f in glob.glob("*.html") if f != "index.html"]
    all_files.sort(reverse=True)
    
    # 3. 超過 5 天的歷史檔案進行清理
    if len(all_files) > 5:
        files_to_delete = all_files[5:]
        for old_file in files_to_delete:
            if os.path.exists(old_file):
                os.remove(old_file)
                print(f"清理過期歷史檔案: {old_file}")
        all_files = all_files[:5]

    # 4. 重新建構 index.html 首頁選單
    links_html = ""
    for file_name in all_files:
        date_display = file_name.replace(".html", "")
        links_html += f'            <li><a class="date-link" href="{file_name}"><span>📈 美股盤後動態彙整</span> <span>{date_display} ➔</span></a></li>\n'

    # 填入連結並寫入 index.html
    homepage_html = HOMEPAGE_TEMPLATE.format(links_html=links_html.rstrip())
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(homepage_html)

if __name__ == "__main__":
    process_daily_content()
