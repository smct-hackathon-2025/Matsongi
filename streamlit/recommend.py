import streamlit as st
import json

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
    
    # 세션 상태 초기화
    if 'recommendations' not in st.session_state:
        # 더미 추천 데이터 (실제로는 AI API에서 받아올 데이터)
        st.session_state.recommendations = [
            {
                "rank": 1,
                "name": "[오뚜기] 마얼라면 4입",
                "similarity": 0.909,
                "url": "https://www.kurly.com/goods/1000358330"
            },
            {
                "rank": 2,
                "name": "[농심] 신라면 멀티 5입",
                "similarity": 0.898,
                "url": "https://www.kurly.com/goods/5069267"
            },
            {
                "rank": 3,
                "name": "[삼양] 4가지 치즈 불닭볶음면 4입",
                "similarity": 0.890,
                "url": "https://www.kurly.com/goods/1000165845"
            },
            {
                "rank": 4,
                "name": "[농심] 안성탕면 5입",
                "similarity": 0.889,
                "url": "https://www.kurly.com/goods/5061317"
            },
            {
                "rank": 5,
                "name": "[삼양] 까르보불닭볶음면 140g*4입",
                "similarity": 0.887,
                "url": "https://www.kurly.com/goods/1000587032"
            }
        ]
    
    # 제목
    st.markdown('<div class="recommend-title">🎯 AI 맞춤 라면 추천</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="recommend-subtitle">{st.session_state.get("user_name", "회원")}님의 입맛을 분석하여 최적의 라면을 찾았습니다!</div>', unsafe_allow_html=True)
    
    # 추천 제품 목록
    st.markdown(
    """
    <div style='text-align: center;'>
        <h2>🏆 개인 취향과 가장 유사한 제품 TOP 5</h2>
    </div>
    """,
    unsafe_allow_html=True
    )

    st.markdown("")
    
    for product in st.session_state.recommendations:
        st.markdown(f"""
            <div style="text-align: center;">
                <div class="product-card" style="display: inline-block; width: 500px; text-align: left;">
                    <div>
                        <span class="product-rank">TOP {product['rank']}</span>
                        <span class="similarity-score">유사도: {product['similarity']:.1%}</span>
                    </div>
                    <div class="product-name">{product['name']}</div>
                    <a href="{product['url']}" target="_blank" class="buy-button">
                        🛒 구매하러 가기
                    </a>
                </div>
            </div>
        """, unsafe_allow_html=True)


    
    # 하단 버튼
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔄 다시 추천받기", use_container_width=True):
            st.session_state.recommendations = []
            st.rerun()
        
        if st.button("🏠 홈으로 돌아가기", use_container_width=True, type="primary"):
            st.success("홈 화면으로 이동하려면 왼쪽 메뉴에서 'HOME'을 선택해주세요!")