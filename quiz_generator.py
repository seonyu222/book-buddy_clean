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
        다음은 영어 고전문학 『{book_title}』의 한 부분입니다. 이 내용을 바탕으로, 한국인 독자를 위한 **독해 문제 5개**를 만들어 주세요.

        조건:
        - 질문과 보기, 모두 반드시 **한국어**로 작성해 주세요.
        - 꼭 보기 4개 중 하나에만 (정답) 이라는 단어를 붙여 주세요. 하나도 빠지면 안 됩니다.
        - (정답)이 빠진 문제가 생기면 전체 퀴즈는 무효가 됩니다.
        - 반드시 하나의 정답이 있어야함
        - 정답은 꼭 반드시 무조건 표기해주세요
        - 각 문제는 **질문 1줄 + 보기 4줄** 형식으로 작성해주세요.
        - 각 문제에는 반드시 보기를 제시하기 전에 첫번째 줄에 질문을 포함해주세요. - 보기 중 정확한 정답 하나에만 반드시 **(정답)**이라고 표시해 주세요. 
        - 질문은 보기와 같은 줄에 쓰지 말고, **질문은 한 줄**, 보기는 **①~④**로 각각 줄을 나눠 주세요.
        - 질문과 보기, 모두 반드시 **한국어**로 작성해 주세요.
        - 보기는 반드시 4지선다형(①~④)이며, 보기 중 하나에만 정답 이라고 적어 주세요.
        - 줄과 줄은 모두 줄바꿈으로 구분해 주세요.
        - 각 문제는 줄바꿈 1번으로 구분해주세요.
        - 형식을 지키지 않은 문제는 만들지 마세요. 보기 4개가 정확히 존재하지 않으면 해당 문제는 출력하지 마세요.
        - 문제는 줄거리, 인물, 상황에 대한 독해력을 평가하도록 해 주세요.
        - 질문과 보기는 반드시 **줄을 나누어** 작성해 주세요.
        - 예시 형식:
    
          도로시의 집에 대한 설명 중 틀린 것은 무엇인가요?

         ① 단층 건물이다. 정답
         ② 오두막에는 총 4벽이 있다.  
         ③ 지하실이라는 공간이 있다.  
         ④ 낮은 지붕이 있다.

     


        📘 다음은 원문 텍스트입니다:
        {chunk}
        """




        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        all_quizzes.append(response.choices[0].message.content)

    return all_quizzes
