# VeganWeb

### 실행 방법
vscode의 터미널에서 프로젝트 디렉토리로 이동한 후, 가상환경을 생성합니다:

```bash
python -m venv venv
```

가상환경 실행 : 
```bash
## 맥/리눅스 버전
source venv/bin/activate
## 윈도우 버전
.\venv\Scripts\activate
```

클론한 프로젝트의 requirements.txt 파일을 사용하여 필요한 패키지를 설치합니다:
```bash : 
pip install -r requirements.txt
```

웹 실행 : 
```bash
flask run
```

http://127.0.0.1:5000 이동

<hr>

## 개발 1주차

### 사용 기술
- **웹 프레임워크**: Flask 웹 기본 프레임 구현 완료
- **데이터베이스**: ElephantSQL 연동 완료

### 구현 기능
1. **메인 페이지**
2. **로그인 페이지**
3. **회원가입 페이지**

### 회원가입 기능
참고 : https://velog.io/@hp657/Flask%EB%9E%91-PostgreSQL%EB%A1%9C-%EB%A1%9C%EA%B7%B8%EC%9D%B8-%ED%9A%8C%EC%9B%90%EA%B0%80%EC%9E%85-%EA%B8%B0%EB%8A%A5-%EB%A7%8C%EB%93%A4%EA%B8%B0 
- 회원가입 화면은 `templates/join.html` 파일에서 구현되었습니다.
- 회원가입 기능을 구현하기 위해서는 `app.py` 파일 중 다음 코드에 추가해야 합니다:

```python
# 회원가입 화면
@app.route("/join")
def join():
    return render_template("join.html")
```

### 개발 2주차
4. **식당/레시피 리스트 페이지**
5. **식당/레시피 상세 페이지**