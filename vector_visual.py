import os
import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from sklearn.decomposition import PCA
import re
import streamlit as st


# 폰트 설정
def load_korean_font():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    font_dir = os.path.join(base_dir, "./font")

    font_path = os.path.join(font_dir, "NanumGothic.ttf")
    bold_font_path = os.path.join(font_dir, "NanumGothicBold.ttf")

    font_prop = fm.FontProperties(fname=font_path)
    bold_font_prop = fm.FontProperties(fname=bold_font_path)

    plt.rcParams["font.family"] = font_prop.get_name()
    plt.rcParams["axes.unicode_minus"] = False

    print(f" 한글 폰트 '{font_prop.get_name()}' 로드 완료")
    return font_prop, bold_font_prop


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# 상품명 정리 함수
def clean_name(name: str) -> str:
    return re.sub(r"[\[\]\(\)\{\}\s]", "", name).lower()


# PCA 시각화
def plot_user_taste_map(user_data, products, survey, font_prop, bold_font_prop, output_path):
    user_vector = np.array(user_data["user_taste_vector"])
    # user_id = user_data["user_id"]
    user_id = st.session_state.get('user_id', 'user_1')
    user_name = st.session_state.user_name if 'user_name' in st.session_state else user_id

    target_dim = user_vector.shape[0]

    product_vectors, product_names = [], []
    for p in products:
        vec = p.get("product_vector")
        if (vec is not None) and isinstance(vec, (list, np.ndarray)) and len(vec) == target_dim:
            product_vectors.append(vec)
            product_names.append(p["name"])

    product_matrix = np.array(product_vectors)
    print(f"유효한 상품 {len(product_names)}개 벡터 로드 완료")

    rated_cleaned_names = {clean_name(name) for name in survey["product_ratings"].keys()}

    # PCA 차원 축소
    print(f"--- PCA 차원 축소 시작 ({target_dim}D → 2D) ---")
    all_vectors = np.vstack([product_matrix, user_vector])
    pca = PCA(n_components=2)
    all_vectors_2d = pca.fit_transform(all_vectors)

    product_vectors_2d = all_vectors_2d[:-1]
    user_vector_2d = all_vectors_2d[-1]
    print("PCA 차원 축소 완료")

    print("--- 시각화 생성 중 ---")
    plt.style.use("seaborn-v0_8-darkgrid")
    fig, ax = plt.subplots(figsize=(16, 12))
    fig.set_facecolor("white")

    # 전체 상품
    ax.scatter(product_vectors_2d[:, 0], product_vectors_2d[:, 1],
               c="#666666", alpha=0.4, s=50, label=f"전체 상품 ({len(product_names)}개)")

    # 사용자가 평가한 상품
    rated_indices = []
    for i, name in enumerate(product_names):
        if any(r in clean_name(name) for r in rated_cleaned_names):
            rated_indices.append(i)

    if rated_indices:
        ax.scatter(product_vectors_2d[rated_indices, 0], product_vectors_2d[rated_indices, 1],
                   c="#6b9dfa", marker="o", s=100, alpha=0.9,
                   label="내가 평가한 상품", edgecolors="#FFFFFF", linewidth=1.5)

    # 사용자 벡터 표시
    ax.scatter(user_vector_2d[0], user_vector_2d[1],
               c="#2b6ae0", marker="s", s=150,
               label=f"나: {user_name}", edgecolors="#1c2445", linewidth=1)

    # 평가한 상품 라벨 표시
    if rated_indices:
        for i in rated_indices:
            simple_name = product_names[i].split("]")[-1].split(" (")[0].strip()
            ax.text(product_vectors_2d[i, 0] + 0.01, product_vectors_2d[i, 1] + 0.01,
                    simple_name, fontsize=12, color="#333333", fontproperties=font_prop)

    ax.set_title(f"'{user_name}'의 미각 지도 ({target_dim}D → 2D PCA)",
                 fontsize=20, pad=20, fontproperties=bold_font_prop)

    legend = ax.legend(fontsize=12, loc="best")
    legend.get_frame().set_facecolor("white")
    legend.get_frame().set_alpha(0.8)
    for text in legend.get_texts():
        text.set_fontproperties(font_prop)

    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    print(f" 저장 완료 → {output_path}")


# 실행
if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, "./data")
    output_dir = os.path.join(base_dir, "./data")

    USER_VECTOR_PATH = os.path.join(data_dir, "./user/user_1_taste_vector.json")
    PRODUCTS_VECTOR_PATH = os.path.join(data_dir, "products_vector.json")
    USER_SURVEY_PATH = os.path.join(data_dir, "./user/user_1_survey.json")
    MAP_OUTPUT_PATH = os.path.join(output_dir, "./user/user_taste_map.png")

    font_prop, bold_font_prop = load_korean_font()
    user_data = load_json(USER_VECTOR_PATH)
    products = load_json(PRODUCTS_VECTOR_PATH)
    survey = load_json(USER_SURVEY_PATH)

    plot_user_taste_map(user_data, products, survey, font_prop, bold_font_prop, MAP_OUTPUT_PATH)
