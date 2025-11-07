import json
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import os

# 기본 경로 설정
USER_DIR = "data/user"
PRODUCT_VECTOR_PATH = "data/products_vector.json"

def get_latest_user_vector_path():
    """user 디렉토리 내 최신 taste_vector 파일 경로 반환"""
    if not os.path.exists(USER_DIR):
        return None

    files = [f for f in os.listdir(USER_DIR) if f.endswith("_taste_vector.json")]
    if not files:
        return None

    # 최신 수정일 기준으로 정렬
    files.sort(key=lambda x: os.path.getmtime(os.path.join(USER_DIR, x)), reverse=True)
    return os.path.join(USER_DIR, files[0])


def load_vectors():
    """유저 벡터와 상품 벡터 로드"""
    user_vec_path = get_latest_user_vector_path()

    if not user_vec_path:
        raise FileNotFoundError("❌ user_taste_vector 파일이 없습니다. Streamlit 설문 후 다시 시도해주세요.")

    with open(user_vec_path, "r", encoding="utf-8") as f:
        user_data = json.load(f)
    with open(PRODUCT_VECTOR_PATH, "r", encoding="utf-8") as f:
        products = json.load(f)

    if isinstance(user_data, list):
        user_data = user_data[0]

    # 키 이름 유연하게 대응
    user_vec = user_data.get("user_taste_vector") or user_data.get("vector")
    if user_vec is None:
        raise KeyError("❌ user_taste_vector 키를 찾을 수 없습니다.")

    # numpy 1D array → 2D array로 reshape
    user_vec = np.array(user_vec).reshape(1, -1)

    return user_vec, products


def recommend_products(top_k=5):
    """유저 벡터와 상품 벡터 간 코사인 유사도 계산"""
    user_vec, products = load_vectors()

    similarities = []
    for product in products:
        try:
            product_vec = np.array(product["product_vector"]).reshape(1, -1)
            sim = cosine_similarity(user_vec, product_vec)[0][0]
            similarities.append({
                "name": product["name"],
                "similarity": float(sim),
                "url": product.get("url", "")
            })
        except Exception as e:
            print(f"⚠️ {product.get('name', 'Unknown')} 처리 중 오류: {e}")

    similarities.sort(key=lambda x: x["similarity"], reverse=True)
    return similarities[:top_k]


if __name__ == "__main__":
    top_items = recommend_products(top_k=5)
    print("🔎 개인 취향과 가장 유사한 제품 TOP 5")
    for i, p in enumerate(top_items, start=1):
        print(f"{i}. {p['name']} ({p['similarity']:.3f})")
        if p["url"]:
            print(f"   {p['url']}")
