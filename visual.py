import json
import numpy as np
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import re
import warnings
import os

warnings.filterwarnings(action='ignore')
font_path = '/usr/share/fonts/truetype/nanum/NanumGothic.ttf'
bold_font_path = '/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf'

try:
    if not os.path.exists(font_path):
        !sudo apt-get -qq -y install fonts-nanum
    font_prop = fm.FontProperties(fname=font_path)

    if os.path.exists(bold_font_path):
        bold_font_prop = fm.FontProperties(fname=bold_font_path)
    else:
        bold_font_prop = fm.FontProperties(fname=font_path, weight='bold')

    plt.rcParams['font.family'] = font_prop.get_name()
    plt.rcParams['axes.unicode_minus'] = False

    print(f"✅ 한글 폰트 '{font_prop.get_name()}' 로드 완료")

except Exception as e:
    print(f"⚠️ 폰트 로드 실패: {e}.")
    font_prop = fm.FontProperties()
    bold_font_prop = fm.FontProperties(weight='bold')

# ====== 경로 설정 ======
BASE_DIR = "/content/drive/MyDrive/Colab Notebooks/숙명AI해커톤"
USER_VECTOR_PATH = f"{BASE_DIR}/user_taste_vector.json"
PRODUCTS_VECTOR_PATH = f"{BASE_DIR}/products_vector.json"
USER_SURVEY_PATH = f"{BASE_DIR}/user_survey.json"
MAP_OUTPUT_PATH = f"{BASE_DIR}/user_taste_map_styled.png" # 파일 이름 변경

# ====== 1. 사용자 벡터 로드 ======
with open(USER_VECTOR_PATH, "r", encoding="utf-8") as f:
    user_data = json.load(f)
user_vector = np.array(user_data["user_taste_vector"])
user_id = user_data["user_id"]

target_dim = user_vector.shape[0]
print(f"INFO: 기준 벡터 차원(Dimension) = {target_dim}")

# ====== 2. 상품 벡터 DB 로드 (유효성 검사) ======
with open(PRODUCTS_VECTOR_PATH, "r", encoding="utf-8") as f:
    products = json.load(f)

product_vectors = []
product_names = []

print("\n--- 🔄 상품 벡터 로드 ---")
for p in products:
    vec = p.get("product_vector")
    if (vec is not None) and isinstance(vec, (list, tuple, np.ndarray)) and (len(vec) == target_dim):
        product_vectors.append(vec)
        product_names.append(p["name"])
    else:
        vec_len = len(vec) if hasattr(vec, '__len__') else 0
        print(f"  (Warning) 상품 스킵: '{p['name']}' (유효하지 않은 벡터: {type(vec)}, len: {vec_len})")

product_matrix = np.array(product_vectors)
print(f"✅ 유효한 상품 {len(product_names)}개 벡터 로드 완료 (Matrix shape: {product_matrix.shape})")

# ====== 3. 사용자가 평가한 상품 목록 로드 ======
with open(USER_SURVEY_PATH, "r", encoding="utf-8") as f:
    survey = json.load(f)

def clean_name(name):
    return re.sub(r'[\[\]\(\)\{\}\s]', '', name).lower()

rated_cleaned_names = {clean_name(name) for name in survey["product_ratings"].keys()}

# ====== 4. PCA 차원 축소 ======
print(f"\n--- 🔄 PCA 차원 축소 시작 ({target_dim}D -> 2D) ---")
all_vectors = np.vstack([product_matrix, user_vector])
pca = PCA(n_components=2)
all_vectors_2d = pca.fit_transform(all_vectors)

product_vectors_2d = all_vectors_2d[:-1]
user_vector_2d = all_vectors_2d[-1]
print("✅ PCA 차원 축소 완료")

# ====== 5. Matplotlib 시각화 (스타일 개선) ======
print("--- 🎨 '미각 지도' 시각화 생성 중 (스타일 적용) ---")

plt.style.use('seaborn-v0_8-darkgrid')

fig, ax = plt.subplots(figsize=(16, 12))
fig.set_facecolor('white')

# 5-1. 모든 상품(•) 플롯
ax.scatter(product_vectors_2d[:, 0], product_vectors_2d[:, 1],
           c='#666666',
           alpha=0.4,
           s=50,
           label=f'전체 상품 ({len(product_names)}개)')

# 5-2. 사용자가 평가한 상품(O) 플롯
rated_indices = []
for i, name in enumerate(product_names):
    cleaned_db_name = clean_name(name)
    for rated_name in rated_cleaned_names:
        if rated_name in cleaned_db_name:
            rated_indices.append(i)
            break

if rated_indices:
    ax.scatter(product_vectors_2d[rated_indices, 0], product_vectors_2d[rated_indices, 1],
               c='#6b9dfa',
               marker='o',
               s=100,
               alpha=0.9,
               label='내가 평가한 상품',
               edgecolors='#FFFFFF',
               linewidth=1.5)

# 5-3. 사용자 벡터 플롯
ax.scatter(user_vector_2d[0], user_vector_2d[1],
           c='#2b6ae0',
           marker='s',
           s=150,
           label=f'나: {user_id}',
           edgecolors='#1c2445',
           linewidth=1)

# 5-4. (선택) 일부 상품명 텍스트 라벨링
if rated_indices:
    for i in rated_indices:
        simple_name = product_names[i].split(']')[-1].split(' (')[0].strip()
        ax.text(product_vectors_2d[i, 0] + 0.01, product_vectors_2d[i, 1] + 0.01,
                simple_name,
                fontsize=12,
                color='#333333', # [스타일 11] 더 부드러운 검은색
                fontproperties=font_prop)

# 5-5. 그래프 설정 (ax 사용)
ax.set_title(f"'{user_id}'의 미각 지도 ({target_dim}D -> 2D PCA)",
             fontsize=20, pad=20, fontproperties=bold_font_prop)
ax.set_xlabel("",
              fontsize=14, fontproperties=font_prop)
ax.set_ylabel("",
              fontsize=14, fontproperties=font_prop)

# [스타일 12] 범례 스타일링
legend = ax.legend(fontsize=12, loc='best')
legend.get_frame().set_facecolor('white') # 범례 배경 흰색
legend.get_frame().set_alpha(0.8) # 범례 배경 반투명
for text in legend.get_texts():
    text.set_fontproperties(font_prop)

# 5-6. 파일로 저장
plt.savefig(MAP_OUTPUT_PATH, dpi=150, bbox_inches='tight')
print(f"\n💾 '미각 지도' 저장 완료 → {MAP_OUTPUT_PATH}")
# plt.show()