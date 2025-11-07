# 📄 streamlit/recommend.py
import streamlit as st
from recommend_products import recommend_products, get_latest_user_vector_path
from update_user_vector import update_on_like
import os

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

    # vector_visual.py 돌린 후 결과 이미지 삽입
    st.markdown("### 📊 나의 맛 취향 벡터 시각화")

    # vector_visual.py 실행
    vector_script_path = "vector_visual.py"
    vector_image_path = "./data/user/user_taste_map.png"

    # 이전 이미지가 있다면 삭제
    if os.path.exists(vector_image_path):
        os.remove(vector_image_path)

    try:
        # vector_visual.py 실행
        import subprocess
        result = subprocess.run(
            ["python", vector_script_path],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            # 이미지 생성 성공
            if os.path.exists(vector_image_path):
                st.success("✅ 벡터 시각화 생성이 완료되었습니다!")
                st.image(vector_image_path, use_container_width=True)
            else:
                st.error("❌ 스크립트는 실행되었으나 이미지 파일이 생성되지 않았습니다.")
        else:
            st.error(f"❌ 스크립트 실행 실패:\n{result.stderr}")
            
    except subprocess.TimeoutExpired:
        st.error("❌ 스크립트 실행 시간 초과 (30초)")
    except FileNotFoundError:
        st.error(f"❌ {vector_script_path} 파일을 찾을 수 없습니다.")
    except Exception as e:
        st.error(f"❌ 오류 발생: {str(e)}")
        # 에러 발생 시에도 기존 이미지가 있다면 표시
        if os.path.exists(vector_image_path):
            st.warning("⚠️ 최신 이미지를 생성하지 못했지만, 이전 이미지를 표시합니다.")
            st.image(vector_image_path, caption="나의 맛 취향 벡터 시각화 (이전 버전)", use_container_width=True)

    st.markdown("---")

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

     # ✅ 좋아요 반영 강도 슬라이더
    st.markdown("### 💡 좋아요 반영 강도 설정")
    alpha = st.slider(
        "좋아요를 누를 때, 해당 제품의 취향이 얼마나 반영될까요?",
        min_value=0.05,
        max_value=0.35,
        value=0.2,      # 기본값 (중간값 정도)
        step=0.05,
        help="값이 높을수록 새로 좋아한 제품의 맛이 강하게 반영됩니다."
    )

    # 추천 결과 표시
    if "recommendations" in st.session_state and st.session_state.recommendations:
        st.markdown("<h2 style='text-align:center;'>🏆 개인 취향과 가장 유사한 제품 TOP 5</h2>", unsafe_allow_html=True)

        for product in st.session_state.recommendations:
            like_btn_key = f"like_{product['name'].replace('[','').replace(']','').replace(' ','_')}"

            # 카드 영역
            st.markdown(f"""
                <div style="text-align: center;">
                    <div class="product-card" style="display: inline-block; width: 300px; text-align: center;">
                        <div>
                            <span class="product-rank">TOP {product['rank']}</span>
                            <span class="similarity-score">유사도: {product['similarity']:.1%}</span>
                        </div>
                        <div class="product-name">{product['name']}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)


            col_spacer1, col1, col2, col_spacer2 = st.columns([4, 3, 2, 3])

            with col1:
                st.markdown(f"""
                    <a href="{product['url']}" target="_blank" class="buy-button" style="
                        background:#fe9600;
                        color:white;
                        padding:10px 20px;
                        border-radius:25px;
                        text-decoration:none;
                        font-weight:bold;
                        display:inline-block;
                        transition:all 0.3s;
                        text-align:center;">
                        🛒 구매하러 가기
                    </a>
                """, unsafe_allow_html=True)

            with col2:
                if st.button("❤️", key=f"like_{product['name']}"):
                    msg = update_on_like(USER_ID, product["name"], alpha=0.3)
                    st.toast(msg)

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
