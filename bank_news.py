import os
import requests
from datetime import datetime
from collections import Counter
import re

CLIENT_ID = os.getenv("NAVER_CLIENT_ID")
CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")

# 트렌드 파악을 위한 키워드 리스트
KEYWORDS = ["은행 금리", "디지털 금융", "가상화폐", "부동산 대출", "증시"]

def get_news(query):
    url = f"https://openapi.naver.com/v1/search/news.json?query={query}&display=10&sort=sim"
    headers = {"X-Naver-Client-Id": CLIENT_ID, "X-Naver-Client-Secret": CLIENT_SECRET}
    try:
        res = requests.get(url, headers=headers)
        return res.json().get('items', []) if res.status_code == 200 else []
    except:
        return []

def extract_trend(all_titles):
    """제목들에서 2글자 이상 단어를 추출해 가장 많이 나온 단어 5개 반환"""
    words = []
    for title in all_titles:
        # 한글, 영문만 남기고 제거
        clean_title = re.sub(r'[^가-힣a-zA-Z\s]', '', title)
        words.extend([word for word in clean_title.split() if len(word) >= 2])
    
    # 빈도수 계산
    most_common = Counter(words).most_common(5)
    return [f"`#{tag}`" for tag, count in most_common]

def main():
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    all_titles = []
    news_data = {}

    for kw in KEYWORDS:
        items = get_news(kw)
        news_data[kw] = items
        for item in items:
            all_titles.append(item['title'].replace('<b>', '').replace('</b>', ''))

    # 트렌드 태그 추출
    trend_tags = extract_trend(all_titles)

    # README 작성
    content = f"# 📊 경제/금융 뉴스 트렌드 리포트\n\n"
    content += f"> **업데이트:** `{now}` (KST)  \n\n"
    content += f"### 🔥 오늘의 핵심 키워드\n"
    content += f"{' '.join(trend_tags)}\n\n"
    content += "--- \n\n"

    for kw, items in news_data.items():
        content += f"### 🔍 '{kw}' 섹션\n"
        for item in items[:3]: # 섹션별 3개만 표시
            title = item['title'].replace('<b>', '').replace('</b>', '').replace('&quot;', '"')
            content += f"* [{title}]({item['link']})\n"
        content += "\n"

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    main()
