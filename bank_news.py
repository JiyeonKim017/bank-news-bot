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

# 2. 11개 경제지 + 3개 주요 통신사 (지연님 맞춤 리스트)
MEDIA_MAP = {
    # 경제지
    "mk.co.kr": "매일경제", "mt.co.kr": "머니투데이", "bizwatch.co.kr": "비즈워치",
    "sedaily.com": "서울경제", "asiae.co.kr": "아시아경제", "edaily.co.kr": "이데일리",
    "chosunbiz.com": "조선비즈", "joseilbo.com": "조세일보", "fnnews.com": "파이낸셜뉴스",
    "hankyung.com": "한국경제", "heraldcorp.com": "헤럴드경제",
    # 통신사 추가
    "yna.co.kr": "연합뉴스", "news1.kr": "뉴스1", "newsis.com": "뉴시스"
}

# 3. 경제 용어 사전 (배워가는 단계를 위해)
ECON_TERMS = [
    {"term": "기준금리", "desc": "한 나라의 금리를 결정하는 뿌리예요. 한국은행이 정하며 대출 이자에 영향을 줘요."},
    {"term": "LTV", "desc": "집값 대비 대출 가능 금액의 비율이에요. 내 집 마련 시 대출 한도를 결정하죠."},
    {"term": "인플레이션", "desc": "물가가 계속 오르는 현상이에요. 돈의 가치가 예전보다 낮아졌다는 뜻이에요."},
    {"term": "코스피 (KOSPI)", "desc": "한국 종합주가지수예요. 우리나라 대표 기업들의 성적표라고 보면 돼요."},
    {"term": "환율", "desc": "우리 돈과 외국 돈의 교환 비율이에요. 경제의 기초 체력을 보여주는 지표입니다."},
    {"term": "경상수지", "desc": "국가 간 거래에서 번 돈과 쓴 돈의 차이예요. 플러스면 흑자, 마이너스면 적자예요."},
    {"term": "양적완화", "desc": "중앙은행이 시장에 돈을 직접 풀어 경기를 부양하는 정책이에요."}
]

def get_financial_indicators():
    try:
        usd_krw = yf.Ticker("USDKRW=X")
        rate = usd_krw.history(period="1d")['Close'].iloc[-1]
        kospi = yf.Ticker("^KS11")
        k_val = kospi.history(period="1d")['Close'].iloc[-1]
        return f"{rate:,.2f}", f"{k_val:,.2f}"
    except:
        return "확인 중", "확인 중"

def get_raw_data():
    url = "https://openapi.naver.com/v1/search/news.json?query=금융&display=100&sort=date"
    headers = {"X-Naver-Client-Id": CLIENT_ID, "X-Naver-Client-Secret": CLIENT_SECRET}
    res = requests.get(url, headers=headers)
    return res.json().get('items', []) if res.status_code == 200 else []

def main():
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    rate, kospi = get_financial_indicators()
    
    raw_items = get_raw_data()
    filtered_news = []
    unique_titles = set()

    for item in raw_items:
        link = item['link']
        media_name = next((name for domain, name in MEDIA_MAP.items() if domain in link), None)
        
        if media_name:
            title = re.sub(r'<[^>]*>', '', item['title']).replace('&quot;', '"').replace('&apos;', "'")
            if title not in unique_titles:
                filtered_news.append({"date": item['pubDate'][5:16], "media": media_name, "title": title, "link": link})
                unique_titles.add(title)

    # 키워드 분석
    words = []
    stopwords = ['금융', '은행', '뉴스', '오늘', '출시', '개최', '제공', '연속']
    for n in filtered_news:
        clean = re.sub(r'[^가-힣\s]', '', n['title'])
        words.extend([w for w in clean.split() if len(w) >= 2 and w not in stopwords])
    trends = [f"`#{tag}`" for tag, _ in Counter(words).most_common(6)]

    today_term = random.choice(ECON_TERMS)

    news_table = "| 날짜 | 언론사 | 뉴스 헤드라인 |\n| :--- | :--- | :--- |\n"
    for n in filtered_news[:12]: # 상위 12개 뉴스
        news_table += f"| {n['date']} | {n['media']} | [{n['title']}]({n['link']}) |\n"

    readme_content = f"""# 🏦 실시간 금융/경제 종합 브리핑

> **마지막 업데이트:** `{now}` (KST)  
> **자동 스케줄:** 09:00, 14:00, 17:00 (KST)

---

### 📖 오늘의 경제 한마디
> **{today_term['term']}**: {today_term['desc']}

---

### 🔥 오늘의 주요 키워드 (분석 대상: 경제지 11곳 + 통신사 3곳)
{" ".join(trends)}

---

### 📈 실시간 주요 지표
| 지표명 | 현재가 |
| :--- | :---: |
| **USD/KRW 환율** | {rate}원 |
| **코스피 지수** | {kospi} |

---

### 📰 실시간 주요 뉴스 (14개 매체 필터링)
{news_table}

---
*제작: JiyeonKim017 / 11개 경제지 및 3개 통신사 기반*
"""
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(readme_content)

if __name__ == "__main__":
    main()
