import os
import requests
import yfinance as yf
from datetime import datetime
from collections import Counter
import re
import random

# 1. 환경 변수
CLIENT_ID = os.getenv("NAVER_CLIENT_ID")
CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")

# 2. 지연님의 14개 타겟 매체
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

def get_balanced_news():
    headers = {"X-Naver-Client-Id": CLIENT_ID, "X-Naver-Client-Secret": CLIENT_SECRET}
    # 검색어를 '경제'로 통합해서 100개를 가져옵니다.
    url = "https://openapi.naver.com/v1/search/news.json?query=경제&display=100&sort=date"
    res = requests.get(url, headers=headers)
    
    if res.status_code != 200:
        return []
    
    items = res.json().get('items', [])
    filtered_news = []
    unique_titles = set()
    # [핵심] 언론사별 카운팅을 위한 딕셔너리
    media_count = {name: 0 for name in MEDIA_MAP.values()}

    for item in items:
        full_link = item.get('originallink', '') + item.get('link', '')
        media_name = next((name for domain, name in MEDIA_MAP.items() if domain in full_link), None)
        
        if media_name:
            # 언론사당 최대 2개까지만 허용 (골고루 보여주기 위해)
            if media_count[media_name] >= 2:
                continue
                
            title = re.sub(r'<[^>]*>', '', item['title']).replace('&quot;', '"').replace('&apos;', "'")
            if title not in unique_titles:
                filtered_news.append({
                    "date": item['pubDate'][5:16],
                    "media": media_name,
                    "title": title,
                    "link": item['link']
                })
                unique_titles.add(title)
                media_count[media_name] += 1
                
        if len(filtered_news) >= 12: # 12개 차면 종료
            break
            
    return filtered_news

def main():
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    rate, kospi = get_financial_indicators()
    news_list = get_balanced_news()

    # 키워드 분석 (필터링된 뉴스 제목 기준)
    words = []
    for n in news_list:
        clean = re.sub(r'[^가-힣\s]', '', n['title'])
        words.extend([w for w in clean.split() if len(w) >= 2 and w not in ['경제', '뉴스', '오늘']])
    trends = [f"`#{tag}`" for tag, _ in Counter(words).most_common(6)]

    # 뉴스 테이블 작성
    news_table = "| 날짜 | 언론사 | 뉴스 헤드라인 |\n| :--- | :--- | :--- |\n"
    for n in news_list:
        news_table += f"| {n['date']} | {n['media']} | [{n['title']}]({n['link']}) |\n"

    readme_content = f"""# 🏦 실시간 경제 종합 브리핑 (14개 매체 균형)

> **업데이트:** `{now}` (KST)

---

### 🔥 오늘의 키워드
{" ".join(trends)}

---

### 📈 주요 지표
| 지표명 | 현재가 |
| :--- | :---: |
| **USD/KRW 환율** | {rate}원 |
| **코스피 지수** | {kospi} |

---

### 📰 실시간 주요 뉴스 (매체별 균형 선별)
{news_table}

---
*제작: JiyeonKim017 / 11개 경제지 + 3개 통신사 기반*
"""
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(readme_content)

if __name__ == "__main__":
    main()
