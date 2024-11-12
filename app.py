from flask import make_response, redirect, render_template, request, url_for
from flask import Flask
import psycopg2

app = Flask(__name__)
app.config['DEBUG'] = True

class DB:
    def __init__(self, database_url):
        self.conn = psycopg2.connect(database_url)
        self.cur = self.conn.cursor()

    def execute_query(self, query, params):
        self.cur.execute(query, params)
        self.conn.commit()
        return self.cur
    
    def select_user(self, userID):
        try:
            self.cur.execute("SELECT user_id, name FROM public.users WHERE user_id = %s;", (userID,))
            return self.cur.fetchone()  # 사용자 정보를 가져옴
        except Exception as e:
            print(f"Error during select_user execution: {e}")
            return None

    def select_user_password(self, userID, password):
        try:
            self.cur.execute("SELECT * FROM public.users WHERE user_id = %s AND password = %s;", (userID, password))
            result = self.cur.fetchone()
            print(f"Query executed successfully: {userID}, {password} -> {result}")  # 디버깅 정보 출력
            return result
        except Exception as e:
            print(f"Error during query execution: {e}")
            return None



# ElephantSQL 연결 URL 설정
database_url = "postgres://jgtlgycb:vTi1ir-ZNfoYi8xaS07Bqxthjm53eedD@salt.db.elephantsql.com/jgtlgycb"

# DB 인스턴스 생성
db = DB(database_url)

# 로그인 되어 있을 때의 유저 정보
def get_user_info():
    ID = request.cookies.get('ID')
    name = request.cookies.get('name')
    return ID, name

# 메인 화면
@app.route("/", methods=['GET', 'POST'])
def home():
    ID, name = get_user_info()
    if ID:
        return render_template("index.html", ID=ID, name=name)
    else:
        return render_template("index.html")


####### 개발 1주차 #######

# 로그인 화면
@app.route("/login", methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        userID = request.form.get("userID")
        password = request.form.get("password")
        
        user = db.select_user_password(userID, password)
        if user:
            user_info = db.select_user(userID)
            resp = make_response(redirect(url_for('home')))  # 메인 화면으로 리다이렉트
            resp.set_cookie('ID', user_info[0])  # ID 저장
            resp.set_cookie('name', user_info[1])  # 이름 저장
            return resp
        else:
            print("Invalid credentials")  # 로그인 실패 메시지 출력
            return render_template('login.html', message='아이디 또는 비밀번호가 일치하지 않습니다.')
    
    return render_template("login.html")

@app.route("/logout")
def logout():
    resp = make_response(redirect(url_for('home')))
    resp.delete_cookie('ID')
    return resp

# 회원가입 화면
@app.route("/join")
def join():
    return render_template("join.html")


####### 개발 2주차 #######

# 식당 리스트 화면
@app.route("/res_list")
def res_list():
    ID, name = get_user_info()
    return render_template("restaurant_list.html", ID=ID, name=name)

# 식당 상세 화면
@app.route("/res_detail")
def res_detail():
    ID, name = get_user_info()
    return render_template("restaurant_detail.html", ID=ID, name=name)

# 레시피 리스트 화면
@app.route("/rec_list")
def rec_list():
    ID, name = get_user_info()
    return render_template("recipe_list.html", ID=ID, name=name)

# 레시피 상세 화면
@app.route("/rec_detail")
def rec_detail():
    ID, name = get_user_info()
    return render_template("recipe_detail.html", ID=ID, name=name)