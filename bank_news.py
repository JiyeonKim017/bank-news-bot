import os
import requests
import yfinance as yf
from datetime import datetime
from collections import Counter
import re
import random

# 1. 환경 변수 및 설정
CLIENT_ID = os.getenv("NAVER_CLIENT_ID")
CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")

# 지연님이 지정한 11개 경제지 + 3개 통신사
MEDIA_MAP = {
    "mk.co.kr": "매일경제", "mt.co.kr": "머니투데이", "bizwatch.co.kr": "비즈워치",
    "sedaily.com": "서울경제", "asiae.co.kr": "아시아경제", "edaily.co.kr": "이데일리",
    "chosunbiz.com": "조선비즈", "joseilbo.com": "조세일보", "fnnews.com": "파이낸셜뉴스",
    "hankyung.com": "한국경제", "heraldcorp.com": "헤럴드경제",
    "yna.co.kr": "연합뉴스", "news1.kr": "뉴스1", "newsis.com": "뉴시스"
}

def get_financial_indicators():
    try:
        usd_krw = yf.Ticker("USDKRW=X")
        rate = usd_krw.history(period="1d")['Close'].iloc[-1]
        kospi = yf.Ticker("^KS11")
        k_val = kospi.history(period="1d")['Close'].iloc[-1]
        return f"{rate:,.2f}", f"{k_val:,.2f}"
    except:
        return "데이터 확인 중", "데이터 확인 중"

def get_news_by_press():
    all_items = []
    headers = {"X-Naver-Client-Id": CLIENT_ID, "X-Naver-Client-Secret": CLIENT_SECRET}
    
    # [핵심] 언론사 이름을 직접 검색어로 사용하여 해당 매체의 최신 뉴스를 유도합니다.
    search_queries = ["매일경제", "한국경제", "머니투데이", "연합뉴스", "금융", "증권"]
    
    for q in search_queries:
        url = f"https://openapi.naver.com/v1/search/news.json?query={q}&display=100&sort=date"
        res = requests.get(url, headers=headers)
        if res.status_code == 200:
            all_items.extend(res.json().get('items', []))
    return all_items

def main():
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    rate, kospi = get_financial_indicators()
    
    # 1. 기사 수집 및 필터링
    raw_items = get_news_by_press()
    filtered_news = []
    unique_titles = set()

    for item in raw_items:
        full_link = item.get('originallink', '') + item.get('link', '')
        media_name = next((name for domain, name in MEDIA_MAP.items() if domain in full_link), None)
        
        if media_name:
            title = re.sub(r'<[^>]*>', '', item['title']).replace('&quot;', '"').replace('&apos;', "'")
            if title not in unique_titles:
                filtered_news.append({
                    "date": item['pubDate'][5:16],
                    "media": media_name,
                    "title": title,
                    "link": item['link']
                })
                unique_titles.add(title)

    # 2. 키워드 분석 (전체 수집된 기사 제목 기준)
    words = []
    stopwords = ['뉴스', '오늘', '기자', '오전', '오후', '분석', '경제', '금융']
    for n in filtered_news:
        clean = re.sub(r'[^가-힣\s]', '', n['title'])
        words.extend([w for w in clean.split() if len(w) >= 2 and w not in stopwords])
    
    # 빈도수가 높은 상위 6개 키워드 추출
    trends = [f"`#{tag}`" for tag, _ in Counter(words).most_common(6)]

    # 3. 뉴스 테이블 구성 (최신 12개만)
    news_table = "| 날짜 | 언론사 | 뉴스 헤드라인 |\n| :--- | :--- | :--- |\n"
    for n in filtered_news[:12]:
        news_table += f"| {n['date']} | {n['media']} | [{n['title']}]({n['link']}) |\n"

    # 4. README 작성
    readme = f"""# 🏦 실시간 금융 뉴스 대시보드

> **업데이트:** `{now}` (KST)

---

### 🔥 뉴스 기반 핫 키워드
{" ".join(trends)}  
*언론사별 최신 기사를 분석하여 추출한 키워드입니다.*

---

### 📈 주요 지표
| 지표명 | 현재가 |
| :--- | :---: |
| **USD/KRW 환율** | {rate}원 |
| **코스피 지수** | {kospi} |

---

### 📰 실시간 주요 뉴스 (14개 매체 타겟팅)
{news_table}

---
*제작: JiyeonKim017 / 11개 경제지 및 3개 통신사 데이터 기반*
"""
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(readme)

if __name__ == "__main__":
    main()
