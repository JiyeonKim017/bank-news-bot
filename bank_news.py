import os
import requests
import yfinance as yf
from datetime import datetime
from collections import Counter
import re

# 1. 환경 변수
CLIENT_ID = os.getenv("NAVER_CLIENT_ID")
CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")

# 2. 언론사 도메인 매칭 사전 (보내주신 경제지 중심)
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
        hist = usd_krw.history(period="2d")
        curr = hist['Close'].iloc[-1]
        diff = curr - hist['Close'].iloc[0]
        diff_str = f"▲ {diff:.2f}" if diff > 0 else f"▼ {abs(diff):.2f}"
        kospi = yf.Ticker("^KS11")
        k_val = kospi.history(period="1d")['Close'].iloc[-1]
        return f"{curr:,.2f}", diff_str, f"{k_val:,.2f}"
    except:
        return "데이터 확인 불가", "-", "데이터 확인 불가"

def get_news(query):
    # 최신순 정렬
    url = f"https://openapi.naver.com/v1/search/news.json?query={query}&display=50&sort=date"
    headers = {"X-Naver-Client-Id": CLIENT_ID, "X-Naver-Client-Secret": CLIENT_SECRET}
    res = requests.get(url, headers=headers)
    return res.json().get('items', []) if res.status_code == 200 else []

def get_media_name(link):
    """링크 주소에서 언론사 이름을 추출합니다."""
    for domain, name in MEDIA_MAP.items():
        if domain in link:
            return name
    return "기타"

def main():
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    queries = ["시중은행 금리", "은행 DX", "가계대출 규제"]
    
    rate, diff, kospi = get_financial_indicators()
    all_titles, news_section = [], ""

    for q in queries:
        items = get_news(q)
        news_section += f"#### 🔍 '{q}' 섹션\n| 날짜 | 언론사 | 뉴스 제목 |\n| :--- | :--- | :--- |\n"
        
        unique_titles = set()
        count = 0
        for item in items:
            title = re.sub(r'<[^>]*>', '', item['title']).replace('&quot;', '"').replace('&apos;', "'")
            media = get_media_name(item['link'])
            
            # 지정한 경제지 위주로 가져오고 싶다면 '기타'를 제외하도록 필터링 가능
            # 여기서는 '기타'도 포함하되 상위 5개만 노출
            if title not in unique_titles and count < 5:
                date = item['pubDate'][5:16]
                news_section += f"| {date} | {media} | [{title}]({item['link']}) |\n"
                all_titles.append(title)
                unique_titles.add(title)
                count += 1
        news_section += "\n"

    # 트렌드 및 감성 분석 로직 (생략 없이 포함)
    words = []
    for t in all_titles:
        clean = re.sub(r'[^가-힣a-zA-Z\s]', '', t)
        words.extend([w for w in clean.split() if len(w) >= 2])
    trends = [f"`#{tag}`" for tag, _ in Counter(words).most_common(5)]

    readme = f"""# 🏦 금융 뉴스 트렌드 대시보드

> **업데이트:** `{now}` (KST)

---

### 🔥 오늘의 핵심 키워드
{" ".join(trends)}

---

### 📈 주요 경제 지표
| 지표명 | 현재가 | 변동 |
| :--- | :---: | :---: |
| **USD/KRW 환율** | {rate}원 | {diff} |
| **코스피 지수** | {kospi} | - |

---

### 📰 섹션별 실시간 뉴스 (최신순)
{news_section}

---
*제작: JiyeonKim017 / 매일 자동 업데이트 중*
"""
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(readme)

if __name__ == "__main__":
    main()
