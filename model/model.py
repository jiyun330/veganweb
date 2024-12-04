import pickle
import re
import pandas as pd
import time  # 추가
from sklearn.metrics.pairwise import cosine_similarity

class Chatbot:
    def __init__(self, model_path, vectorizer_path, tfidf_vectorizer_path, tfidf_matrix_path, restaurant_data, recipe_data):
        try:
            with open(model_path, "rb") as model_file:
                self.model = pickle.load(model_file)

            with open(vectorizer_path, "rb") as vectorizer_file:
                self.vectorizer = pickle.load(vectorizer_file)

            with open(tfidf_vectorizer_path, "rb") as tfidf_file:
                self.tfidf_vectorizer = pickle.load(tfidf_file)
            
            with open(tfidf_matrix_path, "rb") as tfidf_matrix_file:
                self.tfidf_matrix = pickle.load(tfidf_matrix_file)

            self.restaurant_data = restaurant_data
            self.recipe_data = recipe_data

            # 고유 명사 데이터 로드
            self.unique_nouns_df = pd.read_csv('static/csv/unique_nouns.csv')
            self.unique_nouns = self.unique_nouns_df['nouns'].tolist()

        except Exception as e:
            print(f"Error loading model or data: {e}")

    def predict(self, user_input):
        user_vector = self.vectorizer.transform([user_input])
        return self.model.predict(user_vector)[0]

    def extract_location(self, user_input):
        location_match = re.search(r"(서울|경기|인천|대전|대구|부산|울산|광주|강원|충청북도|충북|충청남도|충남|"
                                r"경상북도|경북|경상남도|경남|전라북도|전북|전라남도|전남|제주도|제주)", user_input)
        return location_match.group(1) if location_match else None

    def extract_district(self, user_input):
        district_match = re.search(r"(강남|강남구|강동|강동구|강북|강북구|강서|강서구|관악|관악구|광진|광진구|구로|구로구|금천|금천구|노원|노원구|"
                                r"도봉|도봉구|동대문|동대문구|동작|동작구|마포|마포구|서대문|서대문구|서초|서초구|성동|성동구|성북|성북구|송파|송파구|"
                                r"양천|양천구|영등포|영등포구|용산|용산구|은평|은평구|종로|종로구|중구|중구구|중랑|중랑구|고양|고양시|과천|과천시|광명|광명시|"
                                r"광주|광주시|구리|구리시|군포|군포시|김포|김포시|남양주|남양주시|동두천|동두천시|부천|부천시|성남|성남시|수원|수원시|"
                                r"시흥|시흥시|안산|안산시|안성|안성시|안양|안양시|양주|양주시|오산|오산시|용인|용인시|의왕|의왕시|의정부|의정부시|이천|이천시|"
                                r"파주|파주시|평택|평택시|포천|포천시|하남|하남시|화성|화성시|가평|가평군|양평|양평군|여주|여주시|연천|연천군|강서|강서구|"
                                r"금정|금정구|남구|남구구|동구|동구구|동래|동래구|부산진|부산진구|북구|북구구|사상|사상구|사하|사하구|서구|서구구|수영|수영구|"
                                r"연제|연제구|영도|영도구|중구|중구구|해운대|해운대구|기장|기장군|유성|유성구|서구|서구구|동구|동구구|중구|중구구|대덕|대덕구|"
                                r"남구|남구구|달서|달서구|동구|동구구|북구|북구구|서구|서구구|수성|수성구|중구|중구구|달성|달성군|계양|계양구|미추홀|미추홀구|"
                                r"남동|남동구|동구|동구구|부평|부평구|서구|서구구|연수|연수구|중구|중구구|강화|강화군|옹진|옹진군|광산|광산구|남구|남구구|"
                                r"동구|동구구|북구|북구구|서구|서구구|남구|남구구|동구|동구구|북구|북구구|중구|중구구|울주|울주군|강릉|강릉시|동해|동해시|"
                                r"삼척|삼척시|속초|속초시|원주|원주시|춘천|춘천시|태백|태백시|고성|고성군|양구|양구군|양양|양양군|영월|영월군|인제|인제군|"
                                r"정선|정선군|철원|철원군|평창|평창군|홍천|홍천군|화천|화천군|횡성|횡성군|제천|제천시|청주|청주시|충주|충주시|괴산|괴산군|"
                                r"단양|단양군|보은|보은군|영동|영동군|옥천|옥천군|음성|음성군|증평|증평군|진천|진천군|청원|청원구|계룡|계룡시|공주|공주시|"
                                r"논산|논산시|보령|보령시|서산|서산시|아산|아산시|천안|천안시|금산|금산군|당진|당진시|부여|부여군|서천|서천군|연기|연기군|"
                                r"예산|예산군|청양|청양군|태안|태안군|홍성|홍성군|경산|경산시|경주|경주시|구미|구미시|김천|김천시|문경|문경시|상주|상주시|"
                                r"안동|안동시|영주|영주시|영천|영천시|포항|포항시|고령|고령군|군위|군위군|봉화|봉화군|성주|성주군|영덕|영덕군|영양|영양군|"
                                r"예천|예천군|울릉|울릉군|울진|울진군|의성|의성군|청도|청도군|청송|청송군|칠곡|칠곡군|거제|거제시|김해|김해시|마산|마산시|"
                                r"밀양|밀양시|양산|양산시|진주|진주시|진해|진해시|창원|창원시|통영|통영시|거창|거창군|고성|고성군|남해|남해군|산청|산청군|"
                                r"의령|의령군|창녕|창녕군|하동|하동군|함안|함안군|함양|함양군|합천|합천군|군산|군산시|김제|김제시|남원|남원시|익산|익산시|"
                                r"전주|전주시|정읍|정읍시|고창|고창군|무주|무주군|부안|부안군|순창|순창군|완주|완주군|임실|임실군|장수|장수군|진안|진안군|"
                                r"광양|광양시|나주|나주시|목포|목포시|순천|순천시|여수|여수시|강진|강진군|고흥|고흥군|곡성|곡성군|구례|구례군|담양|담양군|"
                                r"무안|무안군|보성|보성군|신안|신안군|영광|영광군|영암|영암군|완도|완도군|장성|장성군|장흥|장흥군|진도|진도군|함평|함평군|"
                                r"해남|해남군|화순|화순군|서귀포|서귀포시|제주|제주시)\b"
                                , user_input, re.IGNORECASE)
        return district_match.group(1) if district_match else None

    def extract_category(self, user_input):
        category_match = re.search(r"(한식|양식|중식|일식)", user_input)
        return category_match.group(1) if category_match else None
    
    def extract_ingredients(self, user_input):
        # 입력 재료의 TF-IDF 벡터 계산
        input_vector = self.tfidf_vectorizer.transform([user_input])
        
        # 유사도 계산
        ingredient_vector = self.tfidf_vectorizer.transform(self.unique_nouns)
        cosine_similarities = cosine_similarity(input_vector, ingredient_vector)

        # 유사도 순으로 정렬
        similar_indices = cosine_similarities.argsort()[0][::-1]

        # 유사도가 0.5 이상인 재료 추천
        recommended_nouns = []
        for i in similar_indices:
            if cosine_similarities[0][i] >= 0.5:
                recommended_nouns.append(self.unique_nouns[i])

        # 유사도 값 출력
        print("추천된 재료:", recommended_nouns)
        print("유사도 값:", cosine_similarities[0][similar_indices[:len(recommended_nouns)]])

        return recommended_nouns

    def get_recommendation(self, user_input):
        predicted_label = self.predict(user_input)
        print(f"예측: {predicted_label}")        

        # 식당 추천
        if predicted_label == "식당_추천":
            location = self.extract_location(user_input)
            district = self.extract_district(user_input)
            category = self.extract_category(user_input)

            print(f"입력된 위치: {location}, 구/군: {district}, 카테고리: {category}")

            df = self.restaurant_data
            
            filter_conditions = (df['city'].str.contains(location, case=False) if location else True)

            if district:
                filter_conditions &= df['district'].str.contains(district, case=False)
            if category:
                filter_conditions &= df['category'].str.contains(category, case=False)

            filtered_restaurants = df[filter_conditions]
            
            num_samples = min(3, len(filtered_restaurants))
            if num_samples > 0:
                filtered_restaurants = filtered_restaurants.sample(n=num_samples, random_state=None)

                # 결과를 보기 좋게 디자인
                response = ", ".join([
                    f"{row['name']} | {row['category']} | {row['address']}\n" 
                    for _, row in filtered_restaurants.iterrows()
                ])
            else:
                response = "해당 조건에 맞는 레스토랑을 찾을 수 없습니다."

        # 레시피 추천
        elif predicted_label == "레시피_추천":
            recommended_nouns = self.extract_ingredients(user_input)
            
            # 레시피 데이터 가져오기
            r_df = self.recipe_data
            
            # 추천된 재료를 기반으로 레시피 필터링
            recipe_conditions = r_df['ingredients'].str.contains(recommended_nouns[0]) if recommended_nouns else pd.Series([False] * len(r_df))
            
            for noun in recommended_nouns[1:]:
                recipe_conditions |= r_df['ingredients'].str.contains(noun)

            # 필터링된 레시피 가져오기
            filtered_recipes = r_df[recipe_conditions]

            if not filtered_recipes.empty:
                # 랜덤으로 3개 선택
                num_samples = min(3, len(filtered_recipes))
                selected_recipes = filtered_recipes.sample(n=num_samples, random_state=None)

                # 결과를 보기 좋게 디자인
                response = ", ".join([
                    f"{row['name']}" 
                    for _, row in selected_recipes.iterrows()
                ])
            else:
                response = "추천할 수 있는 요리가 없습니다."

        else:
            response = "요청을 이해하지 못했습니다. 다시 시도해주세요."

        # 1.5초 지연 후 응답 반환
        time.sleep(1.5)  # 1.5초 지연
        return response
