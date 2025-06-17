# -*- coding: utf-8 -*-

import streamlit as st

from send_email import send_email  # 네가 만든 이메일 함수

st.set_page_config(page_title="BookBuddy", page_icon="📚", layout="centered")

# 세션 상태 초기화
if "page" not in st.session_state:
    st.session_state.page = "welcome"

# 함수로 각 페이지 정의
def show_welcome():
    st.title("📚 BookBuddy에 오신 걸 환영합니다!")
    st.markdown("책을 읽고, AI가 만든 퀴즈를 풀며 캐릭터를 키워보세요!")
    
    # 이미지 넣고 싶으면 나중에 교체
    # st.image("your_image.png", width=200)

    if st.button("👉 시작하기"):
        st.session_state.page = "select_book"

def show_select_book():
    st.title("📖 책을 선택하세요!")

    # 카테고리 필터 및 검색창
    st.subheader("🔍 필터")
    category = st.selectbox("카테고리", ["전체", "동화", "추리", "고전"])
    search = st.text_input("제목 검색")

    # 예시용 책 목록
    books = {
        "오즈의 마법사": "동화",
        "이상한 나라의 앨리스": "동화",
        "셜록 홈즈": "추리"
    }

    # 필터링
    filtered_books = [
        title for title, cat in books.items()
        if (category == "전체" or cat == category) and (search.lower() in title.lower())
    ]

    for book in filtered_books:
        st.markdown(f"### 📘 {book}")
        if st.button(f"📖 '{book}' 퀴즈 시작하기", key=book):
            st.session_state.selected_book = book  # 선택된 책 저장
            st.session_state.page = "quiz"         # 페이지 상태를 quiz로 바꿈
            st.rerun()                # 페이지 다시 실행해서 퀴즈 화면으로 이동  # 추후 연결

    st.markdown("---")

    with st.expander("📩 찾는 책이 없나요? 퀴즈 추가 요청하기"):
        name = st.text_input("이름")
        email = st.text_input("이메일 주소")
        requested_book = st.text_input("추가 요청하고 싶은 책 제목")
        message = st.text_area("전하고 싶은 말")

        if st.button("📨 요청 보내기"):
            if name and email and requested_book:
                success = send_email(name, email, requested_book, message)
                if success:
                    st.success("요청이 성공적으로 전송되었습니다! 감사합니다 😊")
                else:
                    st.error("요청 전송에 실패했습니다. 다시 시도해 주세요.")
            else:
                st.warning("모든 필수 항목을 입력해 주세요.")

from quiz_generator import generate_quiz_batch
import re

def show_quiz():
    st.title(f"🧠 '{st.session_state.selected_book}' 퀴즈")

    # 퀴즈 제출 여부 확인
    if "quiz_submitted" not in st.session_state:
        with st.spinner("GPT가 문제를 생성 중입니다..."):
            raw_quizzes = generate_quiz_batch(st.session_state.selected_book)
            full_text = "\n".join(raw_quizzes)

        # 줄 단위로 자르기
        lines = [line.strip() for line in full_text.strip().split("\n") if line.strip()]
        question_blocks = []
        current_block = []

        for line in lines:
            if re.match(r"^[①②③④]", line):
                current_block.append(line)
            else:
                if current_block:
                    # 직전 블록이 완성된 문제(질문+보기 4개)면 저장
                    if len(current_block) == 5:
                        question_blocks.append(current_block)
                    current_block = []
                current_block = [line]

        # 마지막 블록 확인
        if current_block and len(current_block) == 5:
            question_blocks.append(current_block)

        # 딱 10문제만 사용
        question_blocks = question_blocks[:10]

        # 세션에 저장
        st.session_state.question_blocks = question_blocks
        st.session_state.answers = {}
        st.session_state.quiz_submitted = False

    # 문제 출력
    from quiz_generator import generate_quiz_batch
import re

def show_quiz():
    import re
    from quiz_generator import generate_quiz_batch

    st.title(f"🧠 '{st.session_state.selected_book}' 퀴즈")

    # 퀴즈 제출 여부 확인
    if "quiz_submitted" not in st.session_state:
        with st.spinner("GPT가 문제를 생성 중입니다..."):
            raw_quizzes = generate_quiz_batch(st.session_state.selected_book)
            full_text = "\n".join(raw_quizzes)

        # 줄 단위로 나누기
        lines = [line.strip() for line in full_text.strip().split("\n") if line.strip()]
        question_blocks = []
        current_block = []

        for line in lines:
            if re.match(r"^[①②③④]", line):
                current_block.append(line)
            else:
                if current_block:
                    if len(current_block) == 5:
                        question_blocks.append(current_block)
                    current_block = []
                current_block = [line]

        if current_block and len(current_block) == 5:
            question_blocks.append(current_block)

        # 딱 10문제만 사용
        question_blocks = question_blocks[:10]

        # 세션 저장
        st.session_state.question_blocks = question_blocks
        st.session_state.answers = {}
        st.session_state.quiz_submitted = False

    # 문제 출력
    for i, block in enumerate(st.session_state.question_blocks):
        raw_question = block[0]
        question = re.sub(r"^\d+\.\s*", "", raw_question)

        raw_choices = block[1:]  # 원본 보기 (정답 포함됨)
        display_choices = [c.replace("(정답)", "").strip() for c in raw_choices]  # 사용자에게 보여줄 보기

        st.markdown(f"**{i + 1}. {question}**")

        selected_display = st.radio(
            "정답 선택:",
            options=display_choices,
            key=f"quiz_{i}",
            index=None,
            horizontal=True
        )

        # 사용자가 고른 보기의 인덱스를 기반으로 원본 정답 포함 보기 저장
        selected_index = display_choices.index(selected_display) if selected_display else None
        if selected_index is not None:
            st.session_state.answers[i] = raw_choices[selected_index]

        st.markdown("---")

    # 채점 버튼
    if st.button("✅ 채점하기"):
        st.session_state.page = "result"
        st.session_state.quiz_submitted = True
        st.rerun()


def show_result():
    st.title("📝 채점 결과")

    correct = 0
    total = len(st.session_state.question_blocks)

    for i, block in enumerate(st.session_state.question_blocks):
        raw_question = block[0]
        # GPT가 붙인 숫자 제거
        question = re.sub(r"^\d+\.\s*", "", raw_question)
        choices = block[1:]

        user_answer = st.session_state.answers.get(i, "")
        correct_choice = next((c for c in choices if "(정답)" in c), None)

        is_correct = user_answer == correct_choice
        if is_correct:
            correct += 1

        st.markdown(f"**{i + 1}. {question}**")

        for choice in choices:
            clean_choice = choice.replace("(정답)", "").strip()

            if choice == correct_choice:
                st.markdown(f"✅ **{clean_choice}**")
            elif choice == user_answer:
                st.markdown(f"❌ ~~{clean_choice}~~")
            else:
                st.markdown(clean_choice)

        st.markdown("---")

    # 점수 및 코인 표시
    coins = correct * 400
    st.success(f"정답 수: {correct} / {total}")
    st.markdown(f"💰 획득 코인: **{coins} 코인**")

    if "coin" not in st.session_state:
        st.session_state.coin = 0
    st.session_state.coin += coins

    # 다음 단계로 이동
    if st.button("🏪 상점으로 이동하기"):
        st.session_state.page = "shop"
        st.rerun()

import os
import streamlit as st

# 📁 이미지 경로 설정
IMAGE_FOLDER = "images/shop"
CHARACTER_IMAGE_PATH = os.path.join(IMAGE_FOLDER, "origin.png")

# 📦 카테고리 접두어 설정
CATEGORY_PREFIX = {
    "피부색": "skin",
    "헤어스타일": "h",
    "상의": "c",
    "하의": "t",
    "드레스": "d",
    "배경": "b"
}

# 💰 아이템 가격 설정
ITEM_PRICES = {
    # 피부색
    **{f"skin_{i}": 200 for i in range(1, 12)},
    # 헤어스타일 h1~h25
    **{f"h_{i}": price for i, price in zip(range(1, 26),
        [500, 600, 400, 500, 600, 400, 500, 600, 400, 500,
         600, 400, 500, 600, 400, 500, 600, 400, 500, 600,
         400, 500, 600, 400, 500])},
    # 상의 c1~c14
    **{f"c_{i}": price for i, price in zip(range(1, 15),
        [500, 400, 500, 400, 500, 400, 500, 400, 500, 400, 500, 400, 500, 400])},
    # 하의 t1~t11
    **{f"t_{i}": price for i, price in zip(range(1, 12),
        [450, 550, 350, 450, 550, 350, 450, 550, 350, 450, 550])},
    # 드레스 d1~d9
    **{f"d_{i}": price for i, price in zip(range(1, 11),
        [700, 600, 700, 600, 700, 600, 700, 600, 700,700,700])},
    # 배경 b1~b5
    **{f"b_{i}": 300 for i in range(1, 6)}
}


def show_shop():
    st.title("아이템 상점")

    # 세션 초기화
    if "coin" not in st.session_state:
        st.session_state.coin = 0
    if "purchased_items" not in st.session_state:
        st.session_state.purchased_items = {}

    # 실시간 구매 내역 (사이드바)
    # ▶ 왼쪽 사이드바: 실시간 구매 내역 (사진 가로 나열)
    with st.sidebar:
       st.markdown("### 🎒 구매한 아이템")
       for cat, items in st.session_state.purchased_items.items():
         if items:
              st.markdown(f"**{cat}**")
              item_images = [os.path.join(IMAGE_FOLDER, f"{name}.png") for name in items]
              img_cols = st.columns(len(item_images))
              for idx, img_path in enumerate(item_images):
                  with img_cols[idx]:
                      if os.path.exists(img_path):
                          st.image(img_path, use_container_width=True)
                      else:
                          st.caption("이미지 없음")



    # 화면 분할
    col1, col2 = st.columns([4, 1])

    # ▶ 오른쪽: 캐릭터 + 선택 아이템
    with col2:
        if os.path.exists(CHARACTER_IMAGE_PATH):
            st.image(CHARACTER_IMAGE_PATH, width=120, caption="내 캐릭터")
        else:
            st.warning("⚠️ 'images/shop/origin.png' 파일이 없습니다!")

        if "selected_item" in st.session_state:
            item = st.session_state.selected_item
            st.image(item["image_path"], width=120)
            st.markdown(f"**{item['name']}**")
            st.markdown(f"💰 가격: **{item['price']} 코인**")
            st.caption("🙅‍♀️ 피팅은 불가능합니다. 고객님~ 착용은 다음 단계에서!")

            if st.button("🛍️ 구매하기", key="buy_selected"):
                coin = st.session_state.coin
                name = item["name"]
                cat = item["category"]
                purchased = st.session_state.purchased_items

                # 제한 조건 체크
                if cat == "드레스" and ("상의" in purchased or "하의" in purchased):
                    st.error("⚠️ 드레스는 상의/하의와 함께 구매할 수 없습니다.")
                elif cat in ("상의", "하의") and "드레스" in purchased:
                    st.error("⚠️ 상의/하의는 드레스와 함께 구매할 수 없습니다.")
                elif cat in ("피부색", "헤어스타일", "상의", "하의", "드레스") and cat in purchased:
                    st.error(f"⚠️ {cat} 아이템은 하나만 구매할 수 있어요.")
                elif coin >= item["price"]:
                    st.session_state.coin -= item["price"]
                    if cat not in purchased:
                        purchased[cat] = []
                    purchased[cat].append(name)
                    st.success(f"{name} 구매 완료! 🎉")
                    del st.session_state.selected_item
                    st.rerun()
                else:
                    st.error("💸 코인이 부족해요!")

    # ▶ 왼쪽: 아이템 목록
    with col1:
        st.markdown(f"💰 현재 코인: **{st.session_state.coin} 코인**")
        selected_category = st.radio("카테고리 선택:", list(CATEGORY_PREFIX.keys()), horizontal=True)
        prefix = CATEGORY_PREFIX[selected_category]

        all_files = sorted(os.listdir(IMAGE_FOLDER)) if os.path.exists(IMAGE_FOLDER) else []
        item_files = [f for f in all_files if f.startswith(prefix)]

        st.markdown(f"### {selected_category} 아이템")
        cols = st.columns(5)
        for idx, filename in enumerate(item_files):
            item_name = os.path.splitext(filename)[0]
            img_path = os.path.join(IMAGE_FOLDER, filename)
            price = ITEM_PRICES.get(item_name, 999)

            with cols[idx % 5]:
                st.image(img_path, width=100)
                if st.button("　", key=f"{selected_category}_{item_name}"):
                    st.session_state.selected_item = {
                        "category": selected_category,
                        "name": item_name,
                        "price": price,
                        "image_path": img_path
                    }

    st.markdown("---")
    if st.button("🧪 쇼핑 종료하고 감정포션 만들기"):
       st.session_state.page = "emotion_potion"
       st.rerun()


import math
import streamlit as st

# 감정 키워드 정의 및 점수 벡터
EMOTION_KEYWORDS = {
    "기쁨": [5, 0, 0],
    "즐거움": [5, 0, 1],
    "신기함": [4, 0, 2],
    "새로움": [4, 0, 1],
    "행복": [5, 0, 0],
    "평온": [4, 0, -1],
    "자신감": [4, 0, 0],
    "놀람": [0, 0, 5],
    "충격": [-1, 0, 5],
    "의아": [-1, 0, 4],
    "혼란": [-2, 0, 4],
    "슬픔": [-5, 0, 0],
    "조금 속상함": [-3, 0, 0],
    "불만족스러움": [-2, 0, 1],
    "화남": [-4, 1, 0],
    "좌절": [-4, 1, -1],
    "두려움": [-3, 1, 2],
}

# 표정 벡터 정의 (총 7개)
EXPRESSION_VECTORS = {
    "아주기쁨": [5, 0, 0],
    "평온": [4, 0, -1],
    "신남": [4, 0, 2],
    "조금 속상함": [-3, 0, 0],
    "슬픔": [-5, 0, 0],
    "화남": [-4, 1, 0],
    "놀람": [0, 0, 5],
}

# 유클리드 거리 계산 함수
def euclidean_distance(vec1, vec2):
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(vec1, vec2)))

# 가장 적절한 표정 결정 함수
def get_best_expression(selected_keywords):
    if not selected_keywords:
        return None
    score = [0, 0, 0]
    for keyword in selected_keywords:
        vec = EMOTION_KEYWORDS.get(keyword)
        if vec:
            score = [s + v for s, v in zip(score, vec)]
    best_expr = min(EXPRESSION_VECTORS.items(), key=lambda item: euclidean_distance(score, item[1]))
    return best_expr[0]

# 감정 포션 만들기 페이지
def show_emotion_potion():
    st.title("🧪 감정포션 만들기")
    st.markdown("이 책을 읽고 어떤 감정을 느꼈나요? 아래 감정 중 3~5개를 골라 포션을 만들어 보세요!")

    all_emotions = [
        "기쁨", "행복", "신남", "놀람", "평온",
        "슬픔", "화남", "조금 속상함", "두려움", "좌절"
    ]

    # 감정 키워드 선택 UI (체크박스 나열)
    selected = []
    cols = st.columns(5)
    for idx, emotion in enumerate(all_emotions):
        with cols[idx % 5]:
            if st.checkbox(emotion, key=f"emotion_{emotion}"):
                selected.append(emotion)

    # 감정 개수에 따라 버튼 제어
    if len(selected) < 3:
        st.warning("⚠️ 최소 3개 이상의 감정을 선택해주세요.")
    elif len(selected) > 5:
        st.warning("⚠️ 최대 5개까지만 선택할 수 있어요.")
    else:
        if st.button("🧪 감정 포션 만들기"):
            expression = get_best_expression(selected)
            if expression:
                st.session_state.selected_emotions = selected
                st.session_state.expression_label = expression  # 합성 단계에서 사용
                st.success("🧪 감정 포션이 완성되었어요! 다음 단계에서 캐릭터에게 적용할 수 있어요.")
                st.session_state.page = "magic"
                st.rerun()
            else:
                st.error("😢 표정을 결정할 수 없어요. 감정을 다시 선택해 주세요.")


from PIL import Image
import os

def generate_character_image(purchased_items, expression_label):
    # 레이어 순서: 아래 → 위
    layer_order = ["b", "sikn", "t", "c", "d", "expression","h"]
    base = None

    for layer in layer_order:
        path = None

        if layer == "sikn":
            item_name = purchased_items.get("피부색", ["sikn_default"])[0]
            path = os.path.join("images/shop", f"{item_name}.png")

        elif layer == "expression":
            if not expression_label:
                continue
            path = os.path.join("images/expression", f"{expression_label}.png")

        else:
            category = next((k for k, v in CATEGORY_PREFIX.items() if v == layer), None)
            if category and category in purchased_items:
                item_name = purchased_items[category][0]
                path = os.path.join("images/shop", f"{item_name}.png")

        if path and os.path.exists(path):
            img = Image.open(path).convert("RGBA")
            if base is None:
                base = Image.new("RGBA", img.size, (0, 0, 0, 0))
            base = Image.alpha_composite(base, img)

    output_path = "images/final_character.png"
    if base:
        base.save(output_path)
        return output_path
    else:
        return None



def show_magic_page():
    st.title("✨ 내 캐릭터 완성!")

    purchased_items = st.session_state.get("purchased_items", {})
    expression_label = st.session_state.get("expression_label", "default")

    image_path = generate_character_image(purchased_items, expression_label)

    if image_path and os.path.exists(image_path):
        st.image(image_path, caption="최종 캐릭터", use_container_width=True)
    else:
        st.error("⚠️ 캐릭터 이미지를 생성할 수 없어요.")



import os
from PIL import Image
import streamlit as st

def show_magic_page():
    st.title("✨ 내 캐릭터 완성!")

    purchased_items = st.session_state.get("purchased_items", {})
    expression_label = st.session_state.get("expression_label", "default")
    book_title = st.session_state.get("selected_book", "unknown_book")

    # 🧍 사용자 이름 입력
    user_name = st.text_input("👤 사용자 이름을 입력해주세요", key="user_name")

    image_path = generate_character_image(purchased_items, expression_label)

    if image_path and os.path.exists(image_path):
        st.image(image_path, caption="최종 캐릭터", use_container_width=True)
    else:
        st.error("⚠️ 캐릭터 이미지를 생성할 수 없어요.")

    if st.button("🎀 컬렉션에 저장하고 다음으로!"):
        if not user_name:
            st.warning("⚠️ 이름을 입력해주세요!")
            return

        collection_dir = "images/collection"
        os.makedirs(collection_dir, exist_ok=True)

        # 📸 저장 경로
        save_path = os.path.join(collection_dir, f"{user_name}_{book_title}.png")

        if os.path.exists(image_path):
            img = Image.open(image_path)
            img.save(save_path)

        st.success("✅ 저장이 완료되었어요!")
        st.session_state.page = "collection"
        st.rerun()



    


    # 컬렉션 저장 버튼 등 추가 가능

from collections import defaultdict

def show_collection():
    st.title("📚 나의 BookBuddy 컬렉션")
    st.markdown("지금까지 저장된 캐릭터들을 책 제목별로 모아봤어요!")

    collection_dir = "images/collection"
    if not os.path.exists(collection_dir):
        st.warning("아직 저장된 캐릭터가 없어요.")
        return

    files = sorted([f for f in os.listdir(collection_dir) if f.endswith(".png")])
    if not files:
        st.info("📁 컬렉션이 비어있어요.")
        return

    # 책 제목별로 분류
    grouped = defaultdict(list)
    for file in files:
        if "_" in file:
            name, book = file.rsplit("_", 1)
            book = book.replace(".png", "")
            grouped[book].append((name, os.path.join(collection_dir, file)))

    # 출력
    for book_title in grouped:
        st.subheader(f"📘 {book_title}")
        cols = st.columns(3)
        for idx, (user, img_path) in enumerate(grouped[book_title]):
            with cols[idx % 3]:
                st.image(img_path, caption=f"{user}", use_container_width=True)

    st.markdown("---")
    if st.button("📖 다른 책 퀴즈 풀러가기"):
        st.session_state.page = "select_book"
        st.rerun()


























# 라우팅
if st.session_state.page == "welcome":
    show_welcome()
elif st.session_state.page == "select_book":
    show_select_book()
elif st.session_state.page == "quiz":
    show_quiz()
elif st.session_state.page == "result":
    show_result()
elif st.session_state.page == "shop":
    show_shop()
elif st.session_state.page == "emotion_potion":
    show_emotion_potion()
elif st.session_state.page == "magic":
    show_magic_page()

elif st.session_state.page == "collection":
    show_collection()






