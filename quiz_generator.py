# -*- coding: utf-8 -*-

import os
import streamlit as st

if "OPENAI_API_KEY" in st.secrets:
    api_key = st.secrets["OPENAI_API_KEY"]
else:
    api_key = os.getenv("OPENAI_API_KEY")

# 그리고 이후에 api_key를 사용하면 됨


from openai import OpenAI
client = OpenAI(api_key=api_key)



def generate_quiz_batch(book_title):
    file_map = {
        "오즈의 마법사": "oz.txt",
        "이상한 나라의 앨리스": "alice.txt",
        "셜록 홈즈": "sherlock.txt"
        # 여기에 책이 늘어나면 계속 추가하면 돼
    }

    file_path = file_map.get(book_title)
    if not file_path or not os.path.exists(file_path):
        return [f"❌ '{book_title}'에 해당하는 텍스트 파일이 없습니다."]

    with open(file_path, "r", encoding="utf-8") as f:
        full_text = f.read()

    chunk_size = 3000
    chunks = [full_text[i:i+chunk_size] for i in range(0, len(full_text), chunk_size)][:4]

    all_quizzes = []
    for chunk in chunks:
        prompt = f"""
        다음은 한국어 고전문학 『{book_title}』의 본문 중 일부입니다. 이 내용을 바탕으로 독해 문제 10개를 만들어 주세요.

        문제는 다음 조건을 정확히 지켜 주세요:

        - 총 10개의 문제를 생성해 주세요.
        - 각 문제는 줄마다 구성해 주세요: 질문 1줄, 보기 4줄.
        - 질문은 보기와 같은 줄에 쓰지 말고, 한 줄 띄어 따로 작성해 주세요.
        - 보기는 반드시 ①, ②, ③, ④로 시작하고 정확히 4개만 작성해 주세요.
        - 보기 중 오직 1개에만 "정답"이라는 단어를 보기 끝에 써 주세요. 예: ③ 양철 나무꾼 정답
        - 보기 중 정답을 반드시 하나만 표시해야 합니다. 여러 개 표시하거나 빠지면 안 됩니다.
        - 각 문제는 문제 사이에 줄바꿈 1줄로 구분해 주세요.
        - 출력은 문제 형식만 주세요. 해설이나 다른 설명은 쓰지 마세요.

        예시:
        도로시는 누구와 함께 길을 떠났나요?  
        ① 허수아비  
        ② 사자  
        ③ 양철 나무꾼 정답  
        ④ 도로시의 고모  

        본문:
        {chunk}
        """





        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        all_quizzes.append(response.choices[0].message.content)

    return all_quizzes
