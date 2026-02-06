import os
import requests
from datetime import datetime

# GitHub Secrets에서 가져올 환경 변수
CLIENT_ID = os.getenv("NAVER_CLIENT_ID")
CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")

# 확장할 키워드 리스트 (여기에 원하는 키워드를 추가하세요)
KEYWORDS = ["시중은행 금리", "은행 DX", "금융 보안", "한국은행 기준금리"]

def get_news(query):
    # 각 키워드당 3개씩 가져오도록 설정
    url = f"https://openapi.naver.com/v1/search/news.json?query={query}&display=3&sort=sim"
    headers = {
        "X-Naver-Client-Id": CLIENT_ID,
        "X-Naver-Client-Secret": CLIENT_SECRET
    }
    try:
        res = requests.get(url, headers=headers)
        return res.json().get('items', []) if res.status_code == 200 else []
    except:
        return []

def main():
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # README 디자인 꾸미기
    content = f"# 🏦 실시간 금융/은행권 뉴스 큐레이션\n\n"
    content += f"> **최종 업데이트:** `{now}` (KST)  \n"
    content += f"> 본 페이지는 GitHub Actions를 통해 매일 자동으로 업데이트됩니다.\n\n"
    content += "--- \n\n"
    
    for kw in KEYWORDS:
        items = get_news(kw)
        content += f"### 🔍 '{kw}' 관련 뉴스\n"
        
        if not items:
            content += "최근 뉴스가 없습니다.\n"
        else:
            for item in items:
                # HTML 태그 제거 및 특수문자 처리
                title = item['title'].replace('<b>', '').replace('</b>', '').replace('&quot;', '"').replace('&apos;', "'")
                pub_date = item['pubDate'][:16] # 날짜 포맷 정리
                content += f"* **[{title}]({item['link']})** \n"
                content += f"  <small>📅 {pub_date}</small>\n"
        
        content += "\n"
    
    content += "---\n"
    content += "*제작: JiyeonKim017 / Powered by Naver Search API*"

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(content)
    print(f"{len(KEYWORDS)}개 키워드에 대한 README 생성 완료")

if __name__ == "__main__":
    main()
