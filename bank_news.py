import os
import requests
from datetime import datetime

# 1. GitHub Secrets에서 환경 변수 읽기
# 로컬 테스트 시에는 .env 파일이 작동하고, GitHub Actions에서는 Secrets 값이 들어옵니다.
CLIENT_ID = os.getenv("NAVER_CLIENT_ID")
CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")

# 검색 키워드 설정
KEYWORDS = ["시중은행", "금리 변동", "은행 DX"]

def get_bank_news(query):
    """네이버 뉴스 API를 통해 뉴스 수집"""
    url = f"https://openapi.naver.com/v1/search/news.json?query={query}&display=3&sort=sim"
    headers = {
        "X-Naver-Client-Id": CLIENT_ID,
        "X-Naver-Client-Secret": CLIENT_SECRET
    }
    
    try:
        res = requests.get(url, headers=headers)
        if res.status_code == 200:
            return res.json().get('items', [])
        else:
            print(f"Error: {res.status_code} for keyword {query}")
            return []
    except Exception as e:
        print(f"Exception occurred: {e}")
        return []

def update_readme():
    """뉴스 데이터를 바탕으로 README.md 파일 생성/수정"""
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # 마크다운 내용 구성
    content = "# 🏦 실시간 은행권 뉴스 큐레이션\n\n"
    content += f"> **마지막 업데이트:** {now} (KST)\n\n"
    content += "이 페이지는 GitHub Actions를 통해 정기적으로 업데이트됩니다.\n\n"
    
    for kw in KEYWORDS:
        content += f"## 🔍 '{kw}' 관련 뉴스\n"
        news_items = get_bank_news(kw)
        
        if not news_items:
            content += "최근 뉴스가 없습니다.\n"
        else:
            for item in news_items:
                # 제목에 포함된 HTML 태그(<b> 등) 제거
                title = item['title'].replace('<b>', '').replace('</b>', '').replace('&quot;', '"').replace('&apos;', "'")
                content += f"* [{title}]({item['link']})\n"
        content += "\n---\n"

    # README.md 파일 쓰기 (현재 실행 경로에 생성)
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(content)
    print("README.md 파일이 성공적으로 생성되었습니다.")

if __name__ == "__main__":
    # API 키 존재 여부 확인
    if not CLIENT_ID or not CLIENT_SECRET:
        print("Error: API 키(ID 또는 Secret)가 설정되지 않았습니다.")
    else:
        update_readme()