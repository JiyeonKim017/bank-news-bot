import os
import requests
import yfinance as yf
from datetime import datetime
from collections import Counter
import re

# 1. 환경 변수
CLIENT_ID = os.getenv("NAVER_CLIENT_ID")
CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")

# 2. 감성 분석용 사전 (기존 유지)
POS_WORDS = ['상승', '돌파', '호재', '급등', '최고', '성장', '확대', '기대', '강세', '흑자']
NEG_WORDS = ['하락', '위기', '우려', '급락', '최저', '침체', '축소', '감소', '약세', '적자']

def get_financial_indicators():
    """실시간 금융 지표 수집 (기존 유지)"""
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

def extract_trends(titles):
    """트렌드 키워드 분석 (기존 유지)"""
    words = []
    for title in titles:
        clean = re.sub(r'[^가-힣a-zA-Z\s]', '', title)
        words.extend([w for w in clean.split() if len(w) >= 2])
    common = Counter(words).most_common(5)
    return [f"`#{tag}`" for tag, count in common]

def analyze_sentiment(titles):
    """감성 분석 (기존 유지)"""
    score = sum(1 for t in titles for p in POS_WORDS if p in t) - \
            sum(1 for t in titles for n in NEG_WORDS if n in t)
    if score > 2: return "긍정 😊", "현재 시장 분위기는 밝은 편입니다."
    if score < -2: return "주의 ⚠️", "리스크 관리에 유의해야 할 시점입니다."
    return "보합 ➖", "평이한 흐름을 유지하고 있습니다."

def get_news(query):
    # sort=date로 변경하여 오늘 올라온 뉴스를 가장 위로!
    url = f"https://openapi.naver.com/v1/search/news.json?query={query}&display=20&sort=date"
    headers = {"X-Naver-Client-Id": CLIENT_ID, "X-Naver-Client-Secret": CLIENT_SECRET}
    res = requests.get(url, headers=headers)
    return res.json().get('items', []) if res.status_code == 200 else []

def clean_html(text):
    return re.sub(r'<[^>]*>', '', text).replace('&quot;', '"').replace('&apos;', "'")

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
            title = clean_html(item['title'])
            # 언론사 정보가 따로 없어서 링크에서 도메인을 추출하거나 간단히 표기
            if title not in unique_titles and count < 5:
                date = item['pubDate'][5:16]
                # 언론사명을 수집하기 위해 link를 활용하거나 '금융뉴스'로 대체
                news_section += f"| {date} | 뉴스원 | [{title}]({item['link']}) |\n"
                all_titles.append(title)
                unique_titles.add(title)
                count += 1
        news_section += "\n"

    trends = extract_trends(all_titles)
    s_label, s_desc = analyze_sentiment(all_titles)

    readme = f"""# 🏦 금융 뉴스 트렌드 대시보드

> **업데이트:** `{now}` (KST)  
> 본 리포트는 실시간 금융 데이터를 분석하여 자동으로 생성됩니다.

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

### 💡 오늘의 시장 분위기
> **종합 의견:** `{s_label}`  
> {s_desc}

---

### 📰 섹션별 실시간 뉴스 (최신순)
{news_section}

---
*제작: JiyeonKim017 / 이 리포트는 매일 자동으로 업데이트됩니다.*
"""
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(readme)

if __name__ == "__main__":
    main()
