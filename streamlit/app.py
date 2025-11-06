import streamlit as st
from streamlit_option_menu import option_menu
import home
import survey
import json
import os, sys
from sentence_transformers import SentenceTransformer
from utils.flavorgraph_loader import load_flavorgraph
from utils.llm_utils import load_api_client

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(BASE_DIR)
from user_vector_generator import generate_user_vector_from_resources

# ==============================
# ✅ 최초 1회만 로드 (session_state 방식)
# ==============================
if "init_done" not in st.session_state:
    with st.spinner("🔄 모델 및 데이터 초기 로드 중... 잠시만 기다려주세요."):
        PRODUCTS_PATH = os.path.join(BASE_DIR, "data", "products_vector.json")
        NODE_PATH = os.path.join(BASE_DIR, "data", "nodes_191120.csv")
        EMBED_PATH = os.path.join(BASE_DIR, "data", "FlavorGraph Node Embedding.pickle")
        CONFIG_PATH = os.path.join(BASE_DIR, "api_keys.json")

        # ✅ 모델 로드 (한 번만)
        model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

        # ✅ FlavorGraph, 제품, 클라이언트 로드
        ingredient_name_to_vec = load_flavorgraph(NODE_PATH, EMBED_PATH)
        with open(PRODUCTS_PATH, "r", encoding="utf-8") as f:
            products = json.load(f)
        client = load_api_client(CONFIG_PATH)

        # ✅ 노드 이름과 임베딩 계산
        node_names = list(ingredient_name_to_vec.keys())
        node_embeds = model.encode(node_names, normalize_embeddings=True)

        # ✅ 세션 상태에 저장
        st.session_state.update({
            "init_done": True,
            "model": model,
            "ingredient_name_to_vec": ingredient_name_to_vec,
            "products": products,
            "client": client,
            "node_names": node_names,
            "node_embeds": node_embeds,
        })

    st.success("✅ 초기 로드 완료!")

# 이후 실행에서는 그대로 재사용
model = st.session_state.model
ingredient_name_to_vec = st.session_state.ingredient_name_to_vec
products = st.session_state.products
client = st.session_state.client
node_names = st.session_state.node_names
node_embeds = st.session_state.node_embeds


# ==============================
# ✅ 사이드바 메뉴
# ==============================
with st.sidebar:
    choice = option_menu(
        "YOUME",
        ["시작", "내 입맛 찾기", "내 레시피 만들기", "설정"],
        icons=['bi bi-house-fill', 'bi bi-clipboard2-x-fill', 'bi bi-gear-fill', 'bi bi-graph-up'],
        menu_icon="bi bi-pin-angle-fill",
        default_index=0,
        styles={
            "container": {"padding": "5!important", "background-color": "#FFFFFF"},
            "icon": {"color": "black", "font-size": "15px"},
            "nav-link": {
                "font-size": "15px",
                "text-align": "left",
                "margin": "0px",
                "--hover-color": "#eee",
            },
            "nav-link-selected": {"background-color": "#8DBBD3"},
            "menu-title": {"font-size": "15px"},
            "menu-icon": {"font-size": "15px"},
        },
    )

# ==============================
# ✅ 페이지 라우팅
# ==============================
if choice == "시작":
    home.run_home()

elif choice == "내 입맛 찾기":
    survey.run_survey(
        model=model,
        flavorgraph=ingredient_name_to_vec,
        products=products,
        client=client,
        node_names=node_names,
        node_embeds=node_embeds,
    )
