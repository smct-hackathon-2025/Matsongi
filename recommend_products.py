import json
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# 파일 경로
USER_VECTOR_PATH = "data/user/user_taste_vector.json"
PRODUCT_VECTOR_PATH = "data/products_vector.json"

def load_vectors():
    with open(USER_VECTOR_PATH, "r", encoding="utf-8") as f:
        user_data = json.load(f)
    with open(PRODUCT_VECTOR_PATH, "r", encoding="utf-8") as f:
        products = json.load(f)

    # 리스트형 or 딕셔너리형 모두 지원
    if isinstance(user_data, list):
        user_data = user_data[0]

    # 키 이름 유연하게 대응
    user_vec = user_data.get("user_taste_vector")

    # numpy 1D array → 2D array로 reshape
    user_vec = np.array(user_vec).reshape(1, -1)

    return user_vec, products

def recommend_products(top_k=5):
    user_vec, products = load_vectors()

    similarities = []
    for product in products:
        product_vec = np.array(product["product_vector"]).reshape(1, -1)
        sim = cosine_similarity(user_vec, product_vec)[0][0]
        similarities.append((product["name"], sim, product.get("url", "")))

    similarities.sort(key=lambda x: x[1], reverse=True)

    print("🔎 개인 취향과 가장 유사한 제품 TOP", top_k)
    for name, sim, url in similarities[:top_k]:
        print(f"- {name} (유사도: {sim:.3f})")
        if url:
            print(f"  {url}")

if __name__ == "__main__":
    recommend_products(top_k=5)