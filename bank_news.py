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

# 2. 지정된 경제지 및 주요 언론사 도메인
MEDIA_MAP = {
    "mk.co.kr": "매일경제", "hankyung.com": "한국경제", "sedaily.com": "서울경제",
    "mt.co.kr": "머니투데이", "edaily.co.kr": "이데일리", "fnnews.com": "파이낸셜뉴스",
    "bizwatch.co.kr": "비즈워치", "chosunbiz.com": "조선비즈", "asiae.co.kr": "아시아경제",
    "heraldcorp.com": "헤럴드경제", "dnews.co.kr": "대한경제", "joseilbo.com": "조세일보",
    "yna.co.kr": "연합뉴스", "news1.kr": "뉴스1", "newsis.com": "뉴시스"
}

# 3. 입문자를 위한 풍성한 경제 용어 리스트
ECON_TERMS = [
    {"term": "기준금리", "desc": "한 나라의 금리를 결정하는 '뿌리'가 되는 금리예요. 한국은행이 정하며, 대출 및 예금 금리에 직접적인 영향을 줘요."},
    {"term": "LTV (주택담보대출비율)", "desc": "집값 대비 대출 가능 금액의 비율이에요. LTV 60%라면 10억 집 담보로 최대 6억까지 빌릴 수 있다는 뜻이죠."},
    {"term": "인플레이션", "desc": "물가가 계속 오르고 돈의 가치가 떨어지는 현상이에요. 똑같은 돈으로 살 수 있는 물건이 줄어드는 상황을 말해요."},
    {"term": "코스피 (KOSPI)", "desc": "국내 대기업들의 주가 흐름을 종합한 지수예요. 한국 경제의 체온계라고도 불려요."},
    {"term": "코스닥 (KOSDAQ)", "desc": "코스피보다 규모는 작지만 유망한 IT, 바이오 기업들이 모여 있는 시장이에요."},
    {"term": "환율", "desc": "우리나라 돈과 외국 돈의 교환 비율이에요. 환율이 오르면 외국 돈을 살 때 더 많은 우리 돈이 필요해져요."},
    {"term": "공매도", "desc": "주식을 빌려서 먼저 팔고, 나중에 주가가 떨어지면 싸게 사서 갚아 차익을 남기는 투자 기법이에요."},
    {"term": "GDP (국내총생산)", "desc": "우리나라 안에서 일정 기간 동안 만들어낸 모든 물건과 서비스의 가치를 합친 경제 규모 지표예요."},
    {"term": "디폴트", "desc": "빌린 돈을 제때 갚지 못하는 채무불이행 상태를 말해요."},
    {"term": "베이비스텝 / 빅스텝", "desc": "금리를 0.25%p 올리면 베이비스텝, 0.5%p 한꺼번에 올리면 빅스텝이라고 해요."},
    {"term": "스테그플레이션", "desc": "경기는 안 좋은데 물가만 계속 오르는 아주 힘든 경제 상황을 뜻해요."},
    {"term": "양적완화", "desc": "국가가 시장에 돈을 직접 풀어 경기를 부양하는 정책이에요."}
]

def get_financial_indicators():
    try:
        usd_krw = yf.Ticker("USDKRW=X")
        curr_rate = usd_krw.history(period="1d")['Close'].iloc[-1]
        kospi = yf.Ticker("^KS11")
        k_val = kospi.history(period="1d")['Close'].iloc[-1]
        return f"{curr_rate:,.2f}", f"{k_val:,.2f}"
    except:
        return "확인 중", "확인 중"

def get_integrated_news():
    # 검색 범위를 넓히기 위해 '금융'으로 검색 후 최신순 100개 수집
    url = "https://openapi.naver.com/v1/search/news.json?query=금융&display=100&sort=date"
    headers = {"X-Naver-Client-Id": CLIENT_ID, "X-Naver-Client-Secret": CLIENT_SECRET}
    res = requests.get(url, headers=headers)
    return res.json().get('items', []) if res.status_code == 200 else []

def main():
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # 1. 지표 및 뉴스 수집
    rate, kospi = get_financial_indicators()
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

    # 2. 오늘의 단어 무작위 선정
    today_term = random.choice(ECON_TERMS)

    # 3. AI 트렌드 키워드 분석
    words = []
    stopwords = ['금융', '은행', '뉴스', '오늘', '출시', '개최', '제공']
    for t in all_titles:
        clean = re.sub(r'[^가-힣\s]', '', t)
        words.extend([w for w in clean.split() if len(w) >= 2 and w not in stopwords])
    trends = [f"`#{tag}`" for tag, _ in Counter(words).most_common(6)]

    # 4. 뉴스 테이블 구성
    news_table = "| 날짜 | 언론사 | 뉴스 헤드라인 |\n| :--- | :--- | :--- |\n"
    for n in filtered_news[:12]:
        news_table += f"| {n['date']} | {n['media']} | [{n['title']}]({n['link']}) |\n"

    # 5. README 조립
    readme_content = f"""# 🏦 실시간 금융/경제 종합 브리핑

> **마지막 업데이트:** `{now}` (KST)  
> **자동 스케줄:** 매일 09:00, 14:00, 17:00 (KST)

---

### 📖 오늘의 경제 한마디
> **{today_term['term']}**: {today_term['desc']}
> *지연님의 경제 공부를 위해 매 업데이트마다 새로운 단어를 선정합니다.*

---

### 🔥 지금 시장 핫 키워드 (AI 분석)
{" ".join(trends)}

---

### 📈 주요 실시간 지표
| 지표명 | 현재가 |
| :--- | :---: |
| **USD/KRW 환율** | {rate}원 |
| **코스피 지수** | {kospi} |

---

### 📰 주요 경제지 실시간 헤드라인 (TOP 12)
{news_section if 'news_section' in locals() else news_table}

---
*제작: JiyeonKim017 / 2026 금융 프로젝트*
"""
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(readme_content)

if __name__ == "__main__":
    main()
