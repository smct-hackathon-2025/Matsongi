import streamlit as st

def run_home():
    # 페이지 스타일링
    st.markdown("""
        <style>
        .main-title {
            font-size: 48px;
            font-weight: bold;
            color: #2C3E50;
            text-align: center;
            margin-bottom: 20px;
        }
        .subtitle {
            font-size: 24px;
            color: #34495E;
            text-align: center;
            margin-bottom: 30px;
        }
        .description {
            font-size: 18px;
            color: #5D6D7E;
            text-align: center;
            line-height: 1.8;
            margin-bottom: 40px;
        }
        .highlight-box {
            background-color: #E8F4F8;
            border-left: 5px solid #8DBBD3;
            padding: 20px;
            border-radius: 10px;
            margin: 30px 0;
        }
        .feature-item {
            font-size: 16px;
            color: #2C3E50;
            margin: 10px 0;
            padding-left: 20px;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # 메인 컨텐츠
    col1, col2, col3 = st.columns([1, 4, 1])
    
    with col2:
        st.markdown('<div class="main-title">YOUME(味)에 오신 것을 환영합니다!</div>', unsafe_allow_html=True)
        
        # 사용자 이름 입력 (세션에 저장)
        if 'user_name' not in st.session_state:
            st.session_state.user_name = ""
        
        if st.session_state.user_name == "":
            st.markdown('<div class="subtitle">시작하기 전에 이름을 알려주세요</div>', unsafe_allow_html=True)
            name_input = st.text_input("이름", placeholder="이름을 입력해주세요", label_visibility="collapsed")
            
            if st.button("시작하기", use_container_width=True):
                if name_input.strip():
                    st.session_state.user_name = name_input.strip()
                    st.rerun()
                else:
                    st.warning("이름을 입력해주세요!")
        else:
            # 이름이 입력된 경우
            st.markdown(f'<div class="subtitle">{st.session_state.user_name}님, 환영합니다!</div>', unsafe_allow_html=True)
            
            st.markdown("""
                <div class="description">
                    <strong>{}</strong>님에게 딱 맞는 라면을 추천해 드리기 위해,<br>
                    <strong>{}</strong>님의 입맛을 알려주세요.
                </div>
            """.format(st.session_state.user_name, st.session_state.user_name), unsafe_allow_html=True)
            
            # 하이라이트 박스
            st.markdown("""
                <div class="highlight-box">
                    <div style="font-size: 20px; font-weight: bold; color: #2C3E50; margin-bottom: 15px;">
                        📋 설문 안내
                    </div>
                    <div class="feature-item">⏱️ 소요 시간: 약 1분</div>
                    <div class="feature-item">📊 생성 결과: 나만의 미각 벡터</div>
                    <div class="feature-item">🎯 추천 정확도: 입맛 기반 맞춤 추천</div>
                </div>
            """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # 설문 시작 버튼
            col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
            with col_btn2:
                if st.button("🚀 내 입맛 벡터 만들러 가기", use_container_width=True, type="primary"):
                    st.session_state.current_page = "SURVEY"
                    # survey 페이지로 이동하기 위한 플래그
                    st.session_state.start_survey = True
                    st.success("설문을 시작합니다! 왼쪽 메뉴에서 'SURVEY'를 선택해주세요.")
            
            st.markdown("<br><br>", unsafe_allow_html=True)
            
            # 추가 정보
            with st.expander("💡 YOUME는 어떤 서비스인가요?"):
                st.markdown("""
                    **YOUME**는 당신의 입맛을 수치화하여 맞춤형 음식을 추천하는 서비스입니다.
                    
                    **주요 기능:**
                    - 🎯 개인 맞춤 미각 벡터 생성
                    - 🍜 입맛 기반 라면 추천
                    - 📈 취향 분석 및 시각화
                    - 💬 AI 챗봇을 통한 상세 추천
                    
                    당신의 입맛을 정확하게 분석하여, 
                    가장 만족스러운 음식 경험을 제공합니다.
                """)