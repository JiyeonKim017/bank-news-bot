import os
import requests
import yfinance as yf
from datetime import datetime
from collections import Counter
import re

# 1. 환경 변수
CLIENT_ID = os.getenv("NAVER_CLIENT_ID")
CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")

# 2. 지정된 경제지 도메인 (이미지 기반 12곳 + 주요 통신사)
MEDIA_MAP = {
    "mk.co.kr": "매일경제",
    "hankyung.com": "한국경제",
    "sedaily.com": "서울경제",
    "mt.co.kr": "머니투데이",
    "edaily.co.kr": "이데일리",
    "fnnews.com": "파이낸셜뉴스",
    "bizwatch.co.kr": "비즈워치",
    "chosunbiz.com": "조선비즈",
    "asiae.co.kr": "아시아경제",
    "heraldcorp.com": "헤럴드경제",
    "dnews.co.kr": "대한경제",
    "joseilbo.com": "조세일보",
    "yna.co.kr": "연합뉴스",
    "news1.kr": "뉴스1",
    "newsis.com": "뉴시스"
}

def get_financial_indicators():
    try:
        usd_krw = yf.Ticker("USDKRW=X")
        curr = usd_krw.history(period="1d")['Close'].iloc[-1]
        kospi = yf.Ticker("^KS11")
        k_val = kospi.history(period="1d")['Close'].iloc[-1]
        return f"{curr:,.2f}", f"{k_val:,.2f}"
    except:
        return "데이터 확인 중", "데이터 확인 중"

def get_news(query):
    # 최신순 정렬로 100개를 가져와서 필터링 준비
    url = f"https://openapi.naver.com/v1/search/news.json?query={query}&display=100&sort=date"
    headers = {"X-Naver-Client-Id": CLIENT_ID, "X-Naver-Client-Secret": CLIENT_SECRET}
    res = requests.get(url, headers=headers)
    return res.json().get('items', []) if res.status_code == 200 else []

def main():
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    queries = ["시중은행 금리", "은행 DX", "가계대출 규제"]
    
    rate, kospi = get_financial_indicators()
    all_titles, news_section = [], ""

    for q in queries:
        items = get_news(q)
        news_section += f"#### 🔍 '{q}' 섹션\n| 날짜 | 언론사 | 뉴스 제목 |\n| :--- | :--- | :--- |\n"
        
        unique_titles = set()
        count = 0
        for item in items:
            link = item['link']
            media_name = None
            for domain, name in MEDIA_MAP.items():
                if domain in link:
                    media_name = name
                    break
            
            if not media_name: continue

            title = re.sub(r'<[^>]*>', '', item['title']).replace('&quot;', '"').replace('&apos;', "'")
            if title not in unique_titles and count < 5:
                date = item['pubDate'][5:16]
                news_section += f"| {date} | {media_name} | [{title}]({link}) |\n"
                all_titles.append(title)
                unique_titles.add(title)
                count += 1
        
        if count == 0:
            news_section += "| - | - | 최근 100개 기사 중 지정 경제지 뉴스가 없습니다. |\n"
        news_section += "\n"

    # 트렌드 분석
    words = []
    for t in all_titles:
        clean = re.sub(r'[^가-힣a-zA-Z\s]', '', t)
        words.extend([w for w in clean.split() if len(w) >= 2])
    trends = [f"`#{tag}`" for tag, _ in Counter(words).most_common(5)]

    readme = f"""# 🏦 금융 뉴스 트렌드 대시보드

> **업데이트:** `{now}` (KST)  
> **자동 스케줄:** 매일 09:00, 14:00, 17:00 (KST)

---

### 🔥 오늘의 핵심 키워드 (분석)
{" ".join(trends)}

---

### 📈 주요 경제 지표
| 지표명 | 현재가 |
| :--- | :---: |
| **USD/KRW 환율** | {rate}원 |
| **코스피 지수** | {kospi} |

---

### 📰 실시간 뉴스 (경제지 필터링)
{news_section}

---
*제작: JiyeonKim017 / GitHub Actions 자동화*
"""
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(readme)

if __name__ == "__main__":
    main()
