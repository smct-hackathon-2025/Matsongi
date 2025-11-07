import json
import numpy as np
from utils.llm_utils import (
    solar_translate_kor_to_eng,
    solar_match_candidate,
)
from utils.user_vector_utils import (
    clean_name,
    get_top_candidates,
    combine_user_vector,
)
from typing import Optional

def generate_user_vector_from_resources(
    user_id: str,
    survey_data: dict,
    products: list,
    model,
    flavorgraph: dict,
    client,
    node_names: list,
    node_embeds,
    output_path: Optional[str] = None,
):
    """
    이미 Streamlit(app.py)에서 로드해둔 자원들을 받아서
    사용자 미각 벡터만 생성하는 함수.
    """
    # 1) 상품명 -> 벡터 맵
    product_name_to_vec = {
        p["name"]: np.array(p["product_vector"]) for p in products if "product_vector" in p
    }

    # 2) 경험 기반 벡터 (설문에서 평가한 라면들)
    user_vecs = []
    for name, rating in survey_data["product_ratings"].items():
        for pname, pvec in product_name_to_vec.items():
            if clean_name(name) in clean_name(pname):
                weight = (rating["spicy"] + rating["salty"]) / 10.0
                user_vecs.append(pvec * weight)
    base_vector = np.mean(user_vecs, axis=0) if user_vecs else None

    # 3) 선호도 기반 벡터
    pref_vecs = []
    for category, prefs in survey_data["taste_preferences"].items():
        for ing_kor, score in prefs.items():
            # 한글 → 영어
            eng = solar_translate_kor_to_eng(client, ing_kor)
            # 후보군 뽑기
            candidates = get_top_candidates(model, eng, node_names, node_embeds)
            # LLM으로 제일 비슷한 노드 하나 고르기
            best = solar_match_candidate(client, eng, candidates)
            if best in flavorgraph:
                vec = flavorgraph[best]
                pref_vecs.append(vec * (score / 5.0))
    pref_vector = np.mean(pref_vecs, axis=0) if pref_vecs else None

    # 4) 결합
    user_vector = combine_user_vector(base_vector, pref_vector)

    result = {
        "user_id": user_id,
        "user_taste_vector": user_vector.tolist(),
    }

    # 5) 저장 옵션
    if output_path:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"✅ user_taste_vector.json saved → {output_path}")

    return result