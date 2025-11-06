import json
import numpy as np
from sentence_transformers import SentenceTransformer
from utils.flavorgraph_loader import load_flavorgraph
from utils.llm_utils import load_api_client, solar_translate_kor_to_eng, solar_match_candidate
from utils.user_vector_utils import clean_name, get_top_candidates, combine_user_vector

BASE_DIR = "./"  # 현재 디렉토리 기준
CONFIG_PATH = f"{BASE_DIR}api_keys.json"
PRODUCTS_PATH = f"{BASE_DIR}data/products_vector.json"
SURVEY_PATH = f"{BASE_DIR}data/user/user_survey.json"
NODE_PATH = f"{BASE_DIR}data/nodes_191120.csv"
EMBED_PATH = f"{BASE_DIR}data/FlavorGraph Node Embedding.pickle"
OUTPUT_PATH = f"{BASE_DIR}data/user/user_taste_vector.json"

# === 데이터 로드 ===
client = load_api_client(CONFIG_PATH)
ingredient_name_to_vec = load_flavorgraph(NODE_PATH, EMBED_PATH)

# 모델 준비
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
node_names = list(ingredient_name_to_vec.keys())
node_embeds = model.encode(node_names, normalize_embeddings=True)

# 입력 데이터 로드
with open(PRODUCTS_PATH, "r", encoding="utf-8") as f:
    products = json.load(f)
with open(SURVEY_PATH, "r", encoding="utf-8") as f:
    survey = json.load(f)

# === 경험 기반 base vector ===
product_name_to_vec = {p["name"]: np.array(p["product_vector"]) for p in products}
user_vecs = []
for name, rating in survey["product_ratings"].items():
    for pname, pvec in product_name_to_vec.items():
        if clean_name(name) in clean_name(pname):
            weight = (rating["spicy"] + rating["salty"]) / 10.0
            user_vecs.append(pvec * weight)
base_vector = np.mean(user_vecs, axis=0) if user_vecs else None

# === 선호도 기반 pref vector ===
pref_vecs = []
for category, prefs in survey["taste_preferences"].items():
    for ing_kor, score in prefs.items():
        eng = solar_translate_kor_to_eng(client, ing_kor)
        candidates = get_top_candidates(model, eng, node_names, node_embeds)
        best = solar_match_candidate(client, eng, candidates)
        if best in ingredient_name_to_vec:
            vec = ingredient_name_to_vec[best]
            pref_vecs.append(vec * (score / 5.0))
pref_vector = np.mean(pref_vecs, axis=0) if pref_vecs else None

# === 결합 및 저장 ===
user_vector = combine_user_vector(base_vector, pref_vector)
output = {"user_id": survey["user_id"], "user_taste_vector": user_vector.tolist()}
with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"user_taste_vector.json saved → {OUTPUT_PATH}")
