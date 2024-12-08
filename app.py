from flask import redirect, render_template, request, url_for, session, jsonify
from flask import Flask
import pandas as pd
import psycopg2
from model.model import Chatbot

app = Flask(__name__)
app.config['DEBUG'] = True
app.secret_key = 'your_secret_key' # 세션용 비밀키

class DB:
    def __init__(self, database_url):
        self.conn = self.conn = psycopg2.connect(database_url)
        self.cur = self.conn.cursor()

    def execute_query(self, query, params):
        try:
            self.cur.execute(query, params)
            self.conn.commit()
            return self.cur
        except Exception as e:
            self.conn.rollback()  # 예외 발생 시 트랜잭션 롤백
            print(f"Query Execution Error: {e}")
            raise

    def __del__(self):
        try:
            if self.cur:
                self.cur.close()
            if self.conn:
                self.conn.close()
        except Exception as e:
            print(f"Error during connection cleanup: {e}")


    
    def select_user(self, userID):
        try:
            self.cur.execute("SELECT user_id, name FROM public.users WHERE user_id = %s;", (userID, ))
            return self.cur.fetchone()
        except Exception as e:
            print(f"Error during select_user execution: {e}")
            return None

    def select_user_password(self, userID, password):
        try:
            self.cur.execute("SELECT * FROM public.users WHERE user_id = %s AND password = %s;", (userID, password))
            result = self.cur.fetchone()
            return result
        except Exception as e:
            print(f"Error during query execution: {e}")
            return None
    
    def change_pwd(self, userID, new_password):
        try:
            self.cur.execute("UPDATE public.users SET password = %s WHERE user_id = %s;", (new_password, userID))
            self.conn.commit()
        except Exception as e:
            print(f"Error during change_pwd execution: {e}")
        
    def select_restaurants_by_category(self, category):
        try:
            if category == '전체보기':
                self.cur.execute("SELECT r.* FROM public.restaurant r;")
            elif category == '베이커리/카페':
                self.cur.execute("""
                            SELECT r.* FROM public.restaurant r 
                            WHERE r.category IN ('베이커리', '카페');""")
            else: 
                self.cur.execute("""
                    SELECT r.*
                    FROM public.restaurant r
                    WHERE r.category = %s;
                """, (category,))
            return self.cur.fetchall()
        except Exception as e:
            self.conn.rollback()
            print(f"Error during select_restaurants_by_category execution: {e}")
            return None
        
    def select_recipes_by_category(self):
        try:
            self.cur.execute("""
                    SELECT r.*
                    FROM public.recipe r;
                """)
            return self.cur.fetchall()
        except Exception as e:
            self.conn.rollback()
            print(f"Error during select_recipes_by_category execution: {e}")
            return None
   
    def select_review_by_id(self, id):
        try:
            self.cur.execute("""
                SELECT r.*, u.name
                FROM public.review r
                JOIN public.users u ON r.user_num = u.user_num
                WHERE r.restaurant_num = %s or r.recipe_num = %s;
            """, (id, id, ))
            return self.cur.fetchall()  # 여러 리뷰와 사용자 이름을 반환
        except Exception as e:
            print(f"Error during select_review_by_id execution: {e}")
            return []

    def select_restaurant_by_id(self, restaurant_id):
        try:
            self.cur.execute("""
                SELECT 
                    r.*,
                    AVG(rv.rating) AS average_rating, 
                    COUNT(rv.rating) AS review_count
                FROM 
                    public.restaurant r
                LEFT JOIN 
                    public.review rv ON r.restaurant_num = rv.restaurant_num
                WHERE 
                    r.restaurant_num = %s
                GROUP BY 
                    r.restaurant_num;
            """, (restaurant_id,))
            result = self.cur.fetchone()
            return result
        except Exception as e:
            print(f"Error during select_average_rating_and_count execution: {e}")
            return None
        
    def select_recipe_by_id(self, recipe_id):
        try:
            self.cur.execute("""
                SELECT 
                    r.*,
                    AVG(rv.rating) AS average_rating, 
                    COUNT(rv.rating) AS review_count
                FROM 
                    public.recipe r
                LEFT JOIN 
                    public.review rv ON r.recipe_num = rv.recipe_num
                WHERE 
                    r.recipe_num = %s
                GROUP BY 
                    r.recipe_num;
            """, (recipe_id,))
            result = self.cur.fetchone()
            return result
        except Exception as e:
            print(f"Error during select_average_rating_and_count execution: {e}")
            return None

    def count_reviews_by_restaurant_id(self, id):
        try:
            self.cur.execute("""
                SELECT COUNT(*) FROM public.review 
                WHERE restaurant_num = %s or recipe_num = %s;
            """, (id, id, ))
            return self.cur.fetchone()[0]  # 총 리뷰 수 반환
        except Exception as e:
            print(f"Error during count_reviews_by_restaurant_id execution: {e}")
            return 0

    
    #  챗봇 sql
    def select_restaurant(self):
        try:
            self.cur.execute("SELECT * FROM public.restaurant;")
            columns = [desc[0] for desc in self.cur.description]  # 컬럼 이름 가져오기
            return pd.DataFrame(self.cur.fetchall(), columns=columns)
        except Exception as e:
            print(f"Error during select_restaurant execution: {e}")
            return pd.DataFrame()
        
    def select_recipe(self):
        try:
            self.cur.execute("SELECT * FROM public.recipe;")
            columns = [desc[0] for desc in self.cur.description]
            return pd.DataFrame(self.cur.fetchall(), columns=columns)
        except Exception as e:
            print(f"Error during select_recipe execution: {e}")
            return pd.DataFrame()

# ElephantSQL 연결 URL 설정
database_url = "postgres://jgtlgycb:vTi1ir-ZNfoYi8xaS07Bqxthjm53eedD@salt.db.elephantsql.com/jgtlgycb"

# DB 인스턴스 생성
db = DB(database_url)

model_path = "./model/naive_bayes_model.pkl"
vectorizer_path = "./model/vectorizer.pkl"
tfidf_vectorizer_path = "./model/tfidf_vectorizer.pkl"
tfidf_matrix_path = "./model/tfidf_matrix.pkl"

restaurant_data = db.select_restaurant() 
recipe_data = db.select_recipe()

# 챗봇 객체 생성
chatbot = Chatbot(model_path, vectorizer_path, tfidf_vectorizer_path, tfidf_matrix_path, restaurant_data, recipe_data)

# 로그인 되어 있을 때의 유저 정보
def get_user_info():
    ID = session.get('ID')
    name = session.get('name')
    return ID, name

# 메인 화면
@app.route("/", methods=['GET', 'POST'])
def home():
    ID, name = get_user_info()
    return render_template("index.html", ID=ID, name=name)


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
            session['ID'] = user_info[0]  # 세션에 ID 저장
            session['name'] = user_info[1]  # 세션에 이름 저장
            return redirect(url_for('home'))
        else:
            print("Invalid credentials")  # 로그인 실패 메시지 출력
            return render_template('login.html', message='아이디 또는 비밀번호가 일치하지 않습니다.')
    
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop('ID', None)
    session.pop('name', None)
    return redirect(url_for('home'))

# 아이디 비밀번호 찾기
@app.route("/find_id", methods=['GET', 'POST'])
def find_id():
    userID = None
    message = ''
    
    if request.method == 'POST':
        userID = request.form.get("userID")
        
        if userID:
            user = db.select_user(userID) 
            
            if user: 
                message = '해당 계정은 존재합니다'
            else: 
                message = '해당 계정은 없습니다'
        else:
            message = '아이디를 입력하세요'
    
    return render_template("find1.html", message=message, userID=userID)

@app.route("/find_pw/<userID>", methods=['GET', 'POST'])
def find_pw(userID):
    if request.method == 'POST':
        new_password = request.form.get('pwd2')

        if new_password:
            # 비밀번호 업데이트
            db.change_pwd(userID, new_password)
            return redirect(url_for('login'))
        else:
            return render_template("find2.html", userID=userID, message="해당 사용자 ID가 존재하지 않습니다.")

    return render_template("find2.html", userID=userID)

# 회원가입 화면
@app.route("/join", methods=['POST', 'GET'])
def join():
    if request.method=='POST':
        
        userID = request.form.get("userID")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        nickname = request.form.get("nickname")
        birthdate = request.form.get("birthdate")
        full_email = f"{request.form.get('email')}@{request.form.get('email_domain')}"
       
        receive_ads = 'receive_ads' in request.form
        
        if password != confirm_password:
            return render_template('join.html', message='비밀번호가 일치하지 않습니다. 다시 입력해주세요.')
        elif len(password)<8:
            return render_template('join.html', message='8자리 이상의 비밀번호를 입력해주세요.')

        # 사용자 ID 중복 체크
        user_check = db.select_user(userID)
        if user_check:
            return render_template('join.html', message='이미 존재하는 아이디입니다.')

        # 이메일 중복 체크
        cur = db.execute_query("SELECT * FROM public.users WHERE email = %s;", (full_email,))
        if cur.fetchone():
            return render_template('join.html', message='이미 존재하는 이메일입니다.')

        db.execute_query("""
		    INSERT INTO public.users (name, user_id, password, email, birthdate, e_checkbox, registration_date) 
		    VALUES (%s, %s, %s, %s, %s, %s, now());""", (nickname, userID, password, full_email, birthdate, receive_ads))
        return redirect(url_for('login'))
    
    return render_template("join.html")



####### 개발 2주차 #######

# 식당 리스트 화면
@app.route("/res_list", methods=['GET', 'POST'])
def res_list():
    ID, name = get_user_info()
    
    # 페이지 번호 가져오기 및 처리
    page = request.args.get('page', '1')  # 기본값을 문자열로 설정
    try:
        page = int(page)  # 문자열을 정수로 변환
    except ValueError:
        page = 1  # 변환 실패 시 기본값으로 설정

    category = request.args.get('category', '전체보기')
    
    # POST 요청에서 검색 조건 가져오기
    search_term = request.form.get('search')
    city = request.form.get('city')
    district = request.form.get('district')

    # 카테고리에 따라 식당 목록 가져오기
    restaurants = db.select_restaurants_by_category(category)

    # 지역 필터링
    if search_term:
        restaurants = [res for res in restaurants if search_term in res[2]]
    if city:
        restaurants = [res for res in restaurants if res[9] == city]
    if district:
        restaurants = [res for res in restaurants if res[10] == district] 

    # 페이지당 표시할 식당 수
    items_per_page = request.args.get('per_page', '15')
    print(items_per_page)
    try:
        items_per_page = int(items_per_page)  # 문자열을 정수로 변환
    except ValueError:
        items_per_page = 15  # 변환 실패 시 기본값 설정

    # 페이징 처리
    start_index = (page - 1) * items_per_page
    end_index = start_index + items_per_page

    # 페이지네이션 처리
    paginated_restaurants = restaurants[start_index:end_index] if restaurants else []
    total_restaurants = len(restaurants) if restaurants else 0  # 전체 식당 수
    total_pages = (total_restaurants + items_per_page - 1) // items_per_page if total_restaurants > 0 else 1  # 총 페이지 수

    # 페이지 번호를 10개씩 묶어서 보여주기
    page_group_size = 10
    start_page_group = (page - 1) // page_group_size * page_group_size + 1
    end_page_group = min(start_page_group + page_group_size - 1, total_pages)

    return render_template(
        "restaurant_list.html",
        ID=ID,
        name=name,
        restaurants=restaurants,  # 전체 식당 목록
        paginated_restaurants=paginated_restaurants,
        category=category,
        page=page,
        total_pages=total_pages,
        start_page_group=start_page_group,
        end_page_group=end_page_group
    )


# 식당 상세 화면
@app.route("/res_detail", methods=['GET', 'POST'])
def res_detail():
    ID, name = get_user_info()
    restaurant_id = request.args.get('restaurant_id')
    page = int(request.args.get('page', 1))

    # user_num 가져오기
    user_num = db.execute_query("""
                SELECT user_num FROM public.users WHERE user_id = %s;
            """, (ID,)).fetchone()
    
    search = request.form.get("search")
    password = request.form.get("password")

    # user_num이 None이 아닐 경우에만 가져옴
    user_num = user_num[0] if user_num else None

    if request.method == 'POST':
        # 리뷰 제출 처리
        review_text = request.form.get('reviewText')
        rating = request.form.get('rating')

        if ID and restaurant_id and review_text and rating and user_num:
            # 데이터베이스에 리뷰 저장
            db.execute_query("""
                INSERT INTO public.review (user_num, content, registration_date, restaurant_num, rating)
                VALUES (%s, %s, now(),  %s, %s);
            """, (user_num, review_text, restaurant_id, rating))
            return redirect(url_for('res_detail', restaurant_id=restaurant_id, page=page)) 

    restaurant = db.select_restaurant_by_id(restaurant_id)
    reviews = db.select_review_by_id(restaurant_id)

    return render_template("restaurant_detail.html", ID=ID, name=name, restaurant=restaurant, reviews=reviews, page=page)



@app.route('/chatbot')
def chat():
    return render_template("chatbot.html")

@app.route("/chatbot_model", methods=['POST'])
def predict():
    user_input = request.json.get('message')
    print(f"사용자 입력: {user_input}")
    
    try: 
        response = chatbot.get_recommendation(user_input)
        return jsonify({"response": response})
    except Exception as e:
        print(f"오류 발생: {e}")  # 오류 로그 출력
        response = "죄송합니다. 요청을 이해하지 못했습니다."
        return jsonify({"response": response})

    

# 레시피 리스트 화면
@app.route("/rec_list")
def rec_list():
    ID, name = get_user_info()
    
    # 페이지 번호 가져오기 및 처리
    page = request.args.get('page', '1') 
    try:
        page = int(page)
    except ValueError:
        page = 1 

    category = request.args.get('category', '전체보기')
    
    # POST 요청에서 검색 조건 가져오기
    search_term = request.form.get('search')

    # 카테고리에 따라 식당 목록 가져오기
    recipes = db.select_recipes_by_category()

    # 지역 필터링
    if search_term:
        recipes = [res for res in recipes if search_term in res[2]]
    
    # 페이지당 표시할 식당 수
    items_per_page = request.args.get('per_page', '15')
    print(items_per_page)
    try:
        items_per_page = int(items_per_page)
    except ValueError:
        items_per_page = 15 

    # 페이징 처리
    start_index = (page - 1) * items_per_page
    end_index = start_index + items_per_page

    # 페이지네이션 처리
    paginated_recipes = recipes[start_index:end_index] if recipes else []
    total_recipes = len(recipes) if recipes else 0  # 전체 식당 수
    total_pages = (total_recipes + items_per_page - 1) // items_per_page if total_recipes > 0 else 1  # 총 페이지 수

    # 페이지 번호를 10개씩 묶어서 보여주기
    page_group_size = 10
    start_page_group = (page - 1) // page_group_size * page_group_size + 1
    end_page_group = min(start_page_group + page_group_size - 1, total_pages)

    return render_template(
        "recipe_list.html",
        ID=ID,
        name=name,
        recipes=recipes,  # 전체 식당 목록
        paginated_recipes=paginated_recipes,
        category=category,
        page=page,
        total_pages=total_pages,
        start_page_group=start_page_group,
        end_page_group=end_page_group
    )

# 레시피 상세 화면
@app.route("/rec_detail", methods=['GET', 'POST'])
def rec_detail():
    ID, name = get_user_info()
    recipe_id = request.args.get('recipe_id')
    page = int(request.args.get('page', 1))

    # user_num 가져오기
    user_num = db.execute_query("""
                SELECT user_num FROM public.users WHERE user_id = %s;
            """, (ID,)).fetchone()

    # user_num이 None이 아닐 경우에만 가져옴
    user_num = user_num[0] if user_num else None

    if request.method == 'POST':
        # 리뷰 제출 처리
        review_text = request.form.get('reviewText')
        rating = request.form.get('rating')

        if ID and recipe_id and review_text and rating and user_num:
            # 데이터베이스에 리뷰 저장
            db.execute_query("""
                INSERT INTO public.review (user_num, content, registration_date, recipe_num, rating)
                VALUES (%s, %s, now(),  %s, %s);
            """, (user_num, review_text, recipe_id, rating))
            return redirect(url_for('rec_detail', recipe_id=recipe_id, page=page))

    recipe = db.select_recipe_by_id(recipe_id)
    reviews = db.select_review_by_id(recipe_id)

    return render_template("recipe_detail.html", ID=ID, name=name, recipe=recipe, reviews=reviews, page=page)

if __name__ == "__main__":
    app.run()