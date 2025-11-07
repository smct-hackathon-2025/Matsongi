import json
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import os

# 기본 경로 설정
USER_DIR = "data/user"
PRODUCT_VECTOR_PATH = "data/products_vector.json"
NEW_PRODUCT_VECTOR = "data/explore_products.json"

def get_active_product_vector_path(use_new: bool = False) -> str:
    return NEW_PRODUCT_VECTOR if use_new else PRODUCT_VECTOR_PATH

def _is_explore_path(path: str) -> bool:
    """✅ ADDED: 경로가 explore_products.json 인지 확인"""
    return os.path.abspath(path) == os.path.abspath(NEW_PRODUCT_VECTOR)


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


def load_vectors(product_vector_path: str = None):
    """유저 벡터와 상품 벡터 로드"""
    user_vec_path = get_latest_user_vector_path()

    if not user_vec_path:
        raise FileNotFoundError("❌ user_taste_vector 파일이 없습니다. Streamlit 설문 후 다시 시도해주세요.")
    
    if product_vector_path is None:
        product_vector_path = NEW_PRODUCT_VECTOR
    
    if not os.path.exists(product_vector_path):
        raise FileNotFoundError(f"❌ 상품 벡터 파일을 찾을 수 없습니다: {product_vector_path}")

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


def recommend_products(top_k=5, use_new: bool = False, product_vector_path: str = None):
    if product_vector_path is None:
        product_vector_path = get_active_product_vector_path(use_new=use_new)

    if _is_explore_path(product_vector_path) or use_new:
        if not os.path.exists(product_vector_path):
            raise FileNotFoundError(f"❌ 상품 벡터 파일을 찾을 수 없습니다: {product_vector_path}")
        with open(product_vector_path, "r", encoding="utf-8") as f:
            products = json.load(f)

        results = []
        for p in products[:top_k]:
            sim_raw = p.get("similarity", None)
            if sim_raw is None:
                print(f"⚠️ explore 항목에 similarity 없음: {p.get('name', 'Unknown')}, 0.0으로 대체")
                sim_val = 0.0
            else:
                sim_val = float(sim_raw)
            results.append({
                "name": p.get("name", ""),
                "similarity": sim_val, 
                "url": p.get("url", ""),
                "img": p.get("img"),
            })
        return results

    user_vec, products = load_vectors(product_vector_path=product_vector_path)

    similarities = []
    for product in products:
        try:
            product_vec = np.array(product["product_vector"]).reshape(1, -1)
            sim = cosine_similarity(user_vec, product_vec)[0][0]
            similarities.append({
                "name": product["name"],
                "similarity": float(sim),
                "url": product.get("url", ""),
                "img": product.get("img", None)
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
            print("img:", p.get("img"))

