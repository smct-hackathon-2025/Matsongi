# 📄 streamlit/recommend.py
import streamlit as st
from recommend_products import recommend_products, get_latest_user_vector_path
from update_user_vector import update_on_like
import os
import requests
from io import BytesIO
from urllib.parse import unquote
from recommend_products import (
    recommend_products,
    get_latest_user_vector_path,
    get_active_product_vector_path,
)
import slackbot


user_id = st.session_state.get('user_id', 'user_1')
USER_ID = user_id


def run_recommend():

    # 스타일링
    st.markdown("""
        <style>
        .recommend-title {
            font-size: 36px;
            font-weight: bold;
            color: #20314e;
            text-align: center;
            margin-bottom: 10px;
        }
        .recommend-subtitle {
            font-size: 18px;
            color: #5D6D7E;
            text-align: center;
            margin-bottom: 30px;
        }
        .product-card {
            background-color: #FFFFFF;
            border: 2px solid #E0E0E0;
            border-radius: 15px;
            padding: 20px;
            margin: 15px auto;
            max-width: 400px;
            transition: all 0.3s;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        .product-card:hover {
            border-color: #fe9600;
            box-shadow: 0 6px 12px rgba(254, 150, 0, 0.3);
            transform: translateY(-3px);
        }
        .product-rank {
            display: inline-block;
            background: #20314e;
            color: white;
            font-size: 18px;
            font-weight: bold;
            padding: 8px 16px;
            border-radius: 20px;
            margin-right: 10px;
        }
        .product-name {
            font-size: 22px;
            font-weight: bold;
            color: #20314e;
            margin: 10px 0;
        }
        .similarity-score {
            display: inline-block;
            background-color: #fff5e6;
            color: #fe9600;
            padding: 5px 12px;
            border-radius: 15px;
            font-size: 14px;
            font-weight: bold;
            margin: 5px 0;
        }
        .buy-button {
            background: #fe9600;
            color: white;
            padding: 12px 24px;
            border-radius: 25px;
            text-decoration: none;
            display: inline-block;
            font-weight: bold;
            margin-top: 10px;
            transition: all 0.3s;
            border: none;
        }
        .buy-button:hover {
            background: #e58700;
            transform: scale(1.05);
            box-shadow: 0 4px 8px rgba(254, 150, 0, 0.4);
        }
        .stButton > button[kind="primary"] {
            background-color: #20314e !important;
            color: white !important;
            border: none !important;
        }
        .stButton > button[kind="primary"]:hover {
            background-color: #162338 !important;
            border: none !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown("<h1 style='text-align:center;'>🎯 AI 맞춤 라면 추천</h1>", unsafe_allow_html=True)

    user_vec_path = get_latest_user_vector_path()
    if not user_vec_path:
        st.warning("⚠️ 아직 생성된 맛 벡터가 없습니다. 먼저 설문을 완료해주세요!")
        st.stop()

    st.info(f"✅ 현재 사용 중인 사용자 벡터 파일: `{os.path.basename(user_vec_path)}`")

    use_new = st.toggle(
        "도전 모드", 
        value=True,    
    )

    active_product_vec = get_active_product_vector_path(use_new=use_new)  # ✅ CHANGED(신규가 기본)
    st.caption(f"현재 선택된 상품 벡터: `{os.path.basename(active_product_vec)}`")

    # 추천 실행 버튼
    if st.button("✨ 추천 결과 불러오기", use_container_width=True):
        with st.spinner("개인 맞춤형 라면 추천을 생성 중입니다... 🍜"):
            try:
                recommendations = recommend_products(top_k=5)
                st.session_state.recommendations = [
                    {**p, "rank": i + 1} for i, p in enumerate(recommendations)
                ]
                st.success("✅ 추천이 완료되었습니다!")

            except FileNotFoundError as e:
                st.error(str(e))
                st.stop()
            except Exception as e:
                st.error(f"❌ 추천 생성 중 오류 발생: {e}")
                st.stop()

    # 추천 결과 표시
    if "recommendations" in st.session_state and st.session_state.recommendations:
        st.markdown("<h2 style='text-align:center; margin-bottom: 25px;'>🏆 개인 취향과 가장 유사한 제품 TOP 5</h2>", unsafe_allow_html=True)

        for product in st.session_state.recommendations:
            img_url = product.get("img", None)
            rank = product["rank"]
            name = product["name"]
            sim = product["similarity"]

            with st.container():
                # 상단: 카드 정보 + 이미지
                col_info, col_img = st.columns([1, 1], vertical_alignment="center")
                with col_info:
                    st.markdown(
                        f"""
                        <div style="
                            background-color: #FFFFFF;
                            border: 2px solid #E0E0E0;
                            border-radius: 20px;
                            padding: 20px;
                            margin: 20px auto;
                            box-shadow: 0 4px 8px rgba(0,0,0,0.08);
                            text-align: center;
                            width: 260px;
                        ">
                            <div style="margin-bottom:10px;">
                                <span style="background:#20314e;color:white;
                                    font-weight:bold;padding:6px 14px;
                                    border-radius:15px;">TOP {rank}</span>
                                <span style="background:#fff5e6;color:#fe9600;
                                    font-weight:bold;padding:6px 12px;
                                    border-radius:15px;margin-left:8px;">
                                    유사도 {sim:.1%}
                                </span>
                            </div>
                            <div style='font-size:20px;font-weight:bold;color:#20314e;margin-top:10px;'>{name}</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    st.markdown(
                        f"""
                        <div style="text-align:center;">
                            <a href="{product['url']}" target="_blank"
                            style="background:#fe9600;color:white;padding:10px 24px;
                                    border-radius:25px;text-decoration:none;font-weight:bold;
                                    display:inline-block;transition:all 0.3s;">
                                    🛒 구매하러 가기
                            </a>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                with col_img:
                    if img_url:
                        try:
                            decoded_url = unquote(img_url)
                            response = requests.get(decoded_url, timeout=5)
                            if response.status_code == 200:
                                st.image(BytesIO(response.content), width=250)
                        except Exception:
                            st.warning("⚠️ 이미지 불러오기 실패")

                # 구분선
                st.markdown("<hr style='margin:20px 0;border:1px solid #e0e0e0;'>", unsafe_allow_html=True)


        # ===== 최근 좋아요 표시 =====
        if "last_liked" in st.session_state:
            st.markdown(
                f"<p style='text-align:center;color:#fe9600;font-weight:bold;'>"
                f"💖 최근 좋아요한 상품: {st.session_state['last_liked']}</p>",
                unsafe_allow_html=True,
            )

        # ===== 하단 버튼 =====
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🔄 다시 추천받기", use_container_width=True):
                st.session_state.recommendations = []
                st.rerun()

            if st.button("🏠 홈으로 돌아가기", use_container_width=True, type="primary"):
                st.success("홈 화면으로 이동하려면 왼쪽 메뉴에서 'HOME'을 선택해주세요!")
