from dotenv import load_dotenv
load_dotenv()

import os
import urllib.request
import xml.etree.ElementTree as ET
import google.generativeai as genai
from supabase import create_client

# 環境変数から設定を取得
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

genai.configure(api_key=GEMINI_API_KEY)
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# 1. RSSニュース取得
def get_latest_news():
    url = "https://news.yahoo.co.jp/rss/topics/top-picks.xml"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    html = urllib.request.urlopen(req).read()
    root = ET.fromstring(html)
    
    articles = []
    for item in root.findall('.//item')[:5]:
        title = item.find('title').text
        description = item.find('description').text if item.find('description') is not None else ""
        articles.append(f"・{title}: {description}")
    return "\n".join(articles)

# 2. AI要約生成
def generate_summary(news_text, target_minutes):
    model = genai.GenerativeModel('gemini-3.6-flash')
    char_count = 300 if target_minutes == 3 else 600
    prompt = f"""
以下のニュースを、朝の移動時間（{target_minutes}分、約{char_count}文字程度）で読めるように分かりやすく要約してください。
箇条書きを活用し、主要なポイントを簡潔にまとめてください。

【ニュース一覧】
{news_text}
"""
    response = model.generate_content(prompt)
    return response.text

# 3. 実行メイン処理
def main():
    print("ニュースを取得中...")
    news_text = get_latest_news()
    
    # ユーザー一覧を取得
    profiles = supabase.table("profiles").select("*").execute().data
    
    for user in profiles:
        print(f"[{user['user_name']}さん用] 3分用・5分用の要約を生成中...")
        summary_3min = generate_summary(news_text, 3)
        summary_5min = generate_summary(news_text, 5)
        
        # 3分用・5分用の両方を保存
        supabase.table("daily_news").insert({
            "user_id": user["id"],
            "summary_text": summary_3min,
            "summary_text_5min": summary_5min  # 5分用カラム（テキストに含むかJSON保存）
        }).execute()
        
    print("完了しました！")

if __name__ == "__main__":
    main()