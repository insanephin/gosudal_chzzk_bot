> **Warning**
> 상당히 맛없는 스파게티입니다.

# 🛡️ 포탑1 : 고수달 치지직 챗봇

> [치지직 개발자 센터](https://developers.chzzk.naver.com/) | [치지직 공식 문서](https://chzzk.gitbook.io/chzzk)

## 📦 설치 및 실행 방법

```bash
# 1. 저장소 클론
git clone https://github.com/insanephin/gosudal_chzzk_bot
cd gosudal_chzzk_bot

# 2. 가상환경 생성 (선택)
python -m virtualenv venv
source venv/bin/activate  # Windows는 venv\Scripts\activate

# 3. 의존성 설치
pip install -r requirements.txt

# 4. 실행
python main.py
# or 
python -m uvicorn --host 0.0.0.0 --port 8081
```

## 🤖 명령어

| 명령어 | 설명 | 사용 예시 | 권한 |
|--------|------|-----------|------|
| `!멤버` | 합방 멤버 조회 | `!멤버` | 모두 |
| `!멤버 <스트리머 목록>` | 합방 멤버 설정 | `!멤버 엠비션,빅헤드` | 구독자,관리자 |

---

## ⚠️ 주의사항

- 본인 계정이 아닌 봇 계정은 따로 생성 필요
- 현재 사욛하는 scope는 다음과 같음
    - 채팅 메시지 조회, 채팅 메시지 쓰기, 채팅 공지 쓰기, 채팅 설정 조회, 채팅 설정 변경, 유저 조회
