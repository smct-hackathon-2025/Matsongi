import json
import numpy as np
from transformers import pipeline
import streamlit as st

BASE_USER_PATH = "data/user/"
PRODUCT_VECTOR_PATH = "data/products_vector.json"

def load_user_vector(user_id):
    path = f"{BASE_USER_PATH}{user_id}_taste_vector.json"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return np.array(data["user_taste_vector"], dtype=float)

def save_user_vector(user_id, new_vec):
    path = f"{BASE_USER_PATH}{user_id}_taste_vector.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"user_taste_vector": new_vec.tolist()}, f, ensure_ascii=False, indent=2)

def get_product_vector(product_name):
    with open(PRODUCT_VECTOR_PATH, "r", encoding="utf-8") as f:
        products = json.load(f)
    for p in products:
        if p["name"] == product_name:
            return np.array(p["product_vector"], dtype=float)
    raise ValueError(f"Product '{product_name}' not found")

# 1️⃣ 좋아요 이벤트
def update_on_like(user_id, product_name, alpha=0.3):
    user_vec = load_user_vector(user_id)
    product_vec = get_product_vector(product_name)
    new_vec = (1 - alpha) * user_vec + alpha * product_vec
    msg = f"✅ [{user_id}] '{product_name}' 좋아요 반영 완료"
    print(msg)
    return msg  

# 2️⃣ 챗봇 대화 기반 업데이트
keyword_extractor = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

def extract_preference(chat_text):
    labels = ["sweet", "spicy", "salty", "bitter", "sour", "umami"]
    result = keyword_extractor(chat_text, labels)
    return result["labels"][0]

def update_from_chat(user_id, chat_text, alpha=0.2):
    user_vec = load_user_vector(user_id)
    pref = extract_preference(chat_text)

    # ⚡ 여기서 session_state 사용
    flavor_vec_map = st.session_state.get("ingredient_name_to_vec", {})

    if pref not in flavor_vec_map:
        print(f"⚠️ '{pref}'에 해당하는 FlavorGraph 노드 없음")
        return

    pref_vec = np.array(flavor_vec_map[pref])
    new_vec = (1 - alpha) * user_vec + alpha * pref_vec
    save_user_vector(user_id, new_vec)
    print(f"🧠 [{user_id}] 채팅 '{chat_text}' 반영 → '{pref}' 취향 강화")
    
def get_sentiment(response_text: str) -> str:
    """
    Bedrock/Lambda 응답 문자열에서 sentiment ('positive', 'negative', 'neutral') 추출
    """
    response_text = response_text.lower()
    if "positive" in response_text:
        return "positive"
    elif "negative" in response_text:
        return "negative"
    else:
        return "neutral"


def run_update(user_vector, product_vector, sentiment, alpha=0.3):
    """
    후기 기반 사용자 벡터 업데이트 로직
    - user_vector: 기존 사용자 입맛 벡터 (list or np.ndarray)
    - product_vector: 후기 대상 제품 벡터
    - sentiment: 'positive' | 'negative' | 'neutral'
    """

    user_vec = np.array(user_vector, dtype=float)
    prod_vec = np.array(product_vector, dtype=float)

    if sentiment == "positive":
        # 긍정 후기는 제품 벡터 쪽으로 조금 이동
        new_vec = user_vec + alpha * (prod_vec - user_vec)
    elif sentiment == "negative":
        # 부정 후기는 반대 방향으로 이동
        new_vec = user_vec - alpha * (prod_vec - user_vec)
    else:  # neutral
        new_vec = user_vec  # 변화 없음

    print(f"🎯 후기 반영 완료: {sentiment} → Δ={alpha}")
    return new_vec.tolist()

# ---------------------------------------------------------
# 4️⃣ 통합 엔트리포인트
# ---------------------------------------------------------
def update_user_vector(event_type, user_id, data):
    if event_type == "like":
        update_on_like(user_id, data["product_name"])
    elif event_type == "chat":
        update_from_chat(user_id, data["message"])