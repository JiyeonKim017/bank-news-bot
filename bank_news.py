import os
import requests
import yfinance as yf
from datetime import datetime
from collections import Counter
import re

# 1. 환경 변수
CLIENT_ID = os.getenv("NAVER_CLIENT_ID")
CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")

# 2. 지정된 경제지 및 주요 언론사 도메인
MEDIA_MAP = {
    "mk.co.kr": "매일경제", "hankyung.com": "한국경제", "sedaily.com": "서울경제",
    "mt.co.kr": "머니투데이", "edaily.co.kr": "이데일리", "fnnews.com": "파이낸셜뉴스",
    "bizwatch.co.kr": "비즈워치", "chosunbiz.com": "조선비즈", "asiae.co.kr": "아시아경제",
    "heraldcorp.com": "헤럴드경제", "dnews.co.kr": "대한경제", "joseilbo.com": "조세일보",
    "yna.co.kr": "연합뉴스", "news1.kr": "뉴스1", "newsis.com": "뉴시스"
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

def get_integrated_news():
    """'금융' 키워드로 최신 뉴스 100개를 가져옵니다."""
    url = f"https://openapi.naver.com/v1/search/news.json?query=금융&display=100&sort=date"
    headers = {"X-Naver-Client-Id": CLIENT_ID, "X-Naver-Client-Secret": CLIENT_SECRET}
    res = requests.get(url, headers=headers)
    return res.json().get('items', []) if res.status_code == 200 else []

def main():
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # 1. 실시간 지표 수집
    rate, kospi = get_financial_indicators()
    
    # 2. 통합 뉴스 수집 및 필터링
    raw_items = get_integrated_news()
    filtered_news = []
    all_titles = []
    unique_titles = set()

    for item in raw_items:
        link = item['link']
        media_name = next((name for domain, name in MEDIA_MAP.items() if domain in link), None)
        
        if media_name:
            title = re.sub(r'<[^>]*>', '', item['title']).replace('&quot;', '"').replace('&apos;', "'")
            if title not in unique_titles:
                filtered_news.append({"date": item['pubDate'][5:16], "media": media_name, "title": title, "link": link})
                all_titles.append(title)
                unique_titles.add(title)

    # 3. 자동 키워드 트렌드 추출 (빈도수 분석)
    words = []
    stopwords = ['금융', '은행', '뉴스', '오늘', '게시판', '기자', '출시', '개최']
    for t in all_titles:
        clean = re.sub(r'[^가-힣\s]', '', t)
        words.extend([w for w in clean.split() if len(w) >= 2 and w not in stopwords])
    trends = [f"`#{tag}`" for tag, _ in Counter(words).most_common(8)]

    # 4. README 작성
    news_table = "| 날짜 | 언론사 | 뉴스 헤드라인 |\n| :--- | :--- | :--- |\n"
    for n in filtered_news[:12]: # 최신 뉴스 12개 노출
        news_table += f"| {n['date']} | {n['media']} | [{n['title']}]({n['link']}) |\n"

    readme_content = f"""# 🏦 실시간 금융/경제 종합 브리핑

> **마지막 업데이트:** `{now}` (KST)  
> **자동 스케줄:** 09:00, 14:00, 17:00 (KST)

---

### 🔥 오늘의 AI 선정 핵심 키워드
{" ".join(trends)}
> *주요 경제지 100개 기사의 제목을 분석한 결과입니다.*

---

### 📈 실시간 주요 지표
| 지표명 | 현재가 |
| :--- | :---: |
| **USD/KRW 환율** | {rate}원 |
| **코스피 지수** | {kospi} |

---

### 📰 주요 경제지 실시간 헤드라인 (TOP 12)
{news_table}

---
*제작: JiyeonKim017 / 데이터 분석 기반 자동 뉴스 리포트*
"""
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(readme_content)

if __name__ == "__main__":
    main()
