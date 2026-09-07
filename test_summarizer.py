import os
import feedparser
from google import genai

# 1. Google Gemini APIの初期化
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

# 2. RSSフィードから最新ニュースを取得
RSS_URL = "https://www.nhk.or.jp/rss/news/cat0.xml"
feed = feedparser.parse(RSS_URL)

raw_articles = []
for entry in feed.entries[:5]:
    raw_articles.append(f"【タイトル】{entry.title}\n【概要】{entry.summary}")

input_text = "\n\n".join(raw_articles)

# 3. ユーザー設定のシミュレーション
reading_time_minutes = 3

if reading_time_minutes <= 3:
    max_chars = 300
    article_count = 3
    detail_level = "要点のみを箇条書きで極めて簡潔に"
else:
    max_chars = 600
    article_count = 5
    detail_level = "背景や詳細を含めてわかりやすく"

# 4. プロンプト作成
prompt = f"""
以下のニュース記事一覧から、重要なものを{article_count}件厳選し、
朝の忙しい時間帯に【{reading_time_minutes}分（約{max_chars}文字以内）】で読み切れるように要約してください。

【条件】
- 全体の合計文字数を【{max_chars}文字以内】に収めてください。
- {detail_level}まとめてください。
- 読者が朝一番に素早く情報を把握できるように出力してください。

【ニュース一覧】
{input_text}
"""

# 5. Gemini APIで要約を生成（最新モデル gemini-3.6-flash に変更）
response = client.models.generate_content(
    model="gemini-3.6-flash",
    contents=prompt,
)

print(f"=== 朝の{reading_time_minutes}分要約ニュース（上限{max_chars}文字） ===")
print(response.text)