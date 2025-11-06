import streamlit as st
import pandas as pd
import json
import os 
import subprocess
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from user_vector_generator import   generate_user_vector_from_resources

SAVE_DIR = "data/user"

def run_survey(model, flavorgraph, products, client, node_names, node_embeds):
    # 스타일링
    st.markdown("""
        <style>
        .survey-title {
            font-size: 36px;
            font-weight: bold;
            color: #2C3E50;
            text-align: center;
            margin-bottom: 10px;
        }
        .survey-subtitle {
            font-size: 18px;
            color: #5D6D7E;
            text-align: center;
            margin-bottom: 30px;
        }
        .step-indicator {
            background-color: #E8F4F8;
            padding: 15px;
            border-radius: 10px;
            text-align: center;
            margin-bottom: 30px;
            font-size: 16px;
            font-weight: bold;
            color: #2C3E50;
        }
        .ramen-card {
            background-color: #FFFFFF;
            border: 2px solid #E0E0E0;
            border-radius: 10px;
            padding: 15px;
            margin: 10px 0;
            transition: all 0.3s;
        }
        .ramen-card:hover {
            border-color: #8DBBD3;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        </style>
    """, unsafe_allow_html=True)
    
    # 세션 상태 초기화
    if 'survey_step' not in st.session_state:
        st.session_state.survey_step = 1
    if 'selected_ramens' not in st.session_state:
        st.session_state.selected_ramens = []
    if 'ramen_ratings' not in st.session_state:
        st.session_state.ramen_ratings = {}
    if 'preference_ratings' not in st.session_state:
        st.session_state.preference_ratings = {}
    
    # 라면 목록
    ramen_list = [
        "신라면", "진라면 (매운맛)", "진라면 (순한맛)", 
        "불닭볶음면 (오리지널)", "너구리 (얼큰한맛)", "삼양라면",
        "안성탕면", "짜파게티", "짜왕", "참깨라면",
        "육개장", "비빔면", "열라면", "진짬뽕"
    ]
    
    # 단계별 진행 표시
    progress = st.session_state.survey_step / 7
    st.progress(progress)
    st.markdown(f'<div class="step-indicator">🔄 진행 단계: {st.session_state.survey_step}/7</div>', unsafe_allow_html=True)
    
    # ==================== 화면 1: 기준 라면 선택 ====================
    if st.session_state.survey_step == 1:
        st.markdown('<div class="survey-title">📋 기준 라면 선택</div>', unsafe_allow_html=True)
        st.markdown('<div class="survey-subtitle">평소 드셔보셨고, 맛이 기억나는 라면을 3가지 이상 선택해주세요.</div>', unsafe_allow_html=True)
        
        st.info("💡 이 라면들을 기준으로 {}님의 입맛을 분석합니다.".format(st.session_state.get('user_name', '회원')))
        
        # 라면 선택 (체크박스)
        cols = st.columns(3)
        for idx, ramen in enumerate(ramen_list):
            with cols[idx % 3]:
                if st.checkbox(ramen, key=f"select_{ramen}", value=ramen in st.session_state.selected_ramens):
                    if ramen not in st.session_state.selected_ramens:
                        st.session_state.selected_ramens.append(ramen)
                else:
                    if ramen in st.session_state.selected_ramens:
                        st.session_state.selected_ramens.remove(ramen)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # 선택 개수 표시 및 다음 버튼
        col1, col2, col3 = st.columns([2, 1, 2])
        with col2:
            selected_count = len(st.session_state.selected_ramens)
            st.metric("선택한 라면", f"{selected_count}개")
            
            if selected_count >= 1:
                if st.button("✅ 선택 완료", use_container_width=True, type="primary"):
                    st.session_state.survey_step = 2
                    st.session_state.current_rating_index = 0
                    st.rerun()
            else:
                st.button("✅ 선택 완료", use_container_width=True, disabled=True)
                st.caption(f"⚠️ {selected_count}개 선택")
    
    # ==================== 화면 2-n: 선택한 라면 평가 ====================
    elif st.session_state.survey_step >= 2 and st.session_state.survey_step < 2 + len(st.session_state.selected_ramens):
        rating_index = st.session_state.survey_step - 2
        current_ramen = st.session_state.selected_ramens[rating_index]
        
        st.markdown(f'<div class="survey-title">🍜 {current_ramen} 평가</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="survey-subtitle">{st.session_state.get("user_name", "회원")}님이 느끼기에 [{current_ramen}]의 맛은 어떠셨나요?</div>', unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # 평가 항목
        st.subheader("🌶️ 1. 매운맛")
        spicy = st.select_slider(
            "매운 정도",
            options=[1, 2, 3, 4, 5],
            format_func=lambda x: ["전혀 안 매웠다", "살짝 매웠다", "적당히 매웠다", "꽤 매웠다", "아주 매웠다"][x-1],
            key=f"spicy_{current_ramen}",
            value=st.session_state.ramen_ratings.get(current_ramen, {}).get('spicy', 3)
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.subheader("🧂 2. 짠맛")
        salty = st.select_slider(
            "짠 정도",
            options=[1, 2, 3, 4, 5],
            format_func=lambda x: ["싱거웠다", "살짝 싱거웠다", "간이 적당했다", "살짝 짰다", "아주 짰다"][x-1],
            key=f"salty_{current_ramen}",
            value=st.session_state.ramen_ratings.get(current_ramen, {}).get('salty', 3)
        )
        
        st.markdown("<br><br>", unsafe_allow_html=True)
        
        # 버튼 영역
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            # 이전 버튼
            if rating_index > 0:
                if st.button("⬅️ 이전", use_container_width=True):
                    st.session_state.survey_step -= 1
                    st.rerun()
            
            # 다음/완료 버튼
            if st.button("➡️ 다음" if rating_index < len(st.session_state.selected_ramens) - 1 else "✅ 평가 완료", 
                        use_container_width=True, type="primary"):
                # 현재 평가 저장
                st.session_state.ramen_ratings[current_ramen] = {
                    'spicy': spicy,
                    'salty': salty
                }
                st.session_state.survey_step += 1
                st.rerun()
    
    # ==================== 화면 마지막: 선호 맛 입력 ====================
    elif st.session_state.survey_step == 2 + len(st.session_state.selected_ramens):
        st.markdown('<div class="survey-title">🎯 선호하는 맛 설정</div>', unsafe_allow_html=True)
        st.markdown('<div class="survey-subtitle">마지막입니다! {}님께서 가장 선호하는 맛의 종류와 강도를 알려주세요.</div>'.format(
            st.session_state.get('user_name', '회원')), unsafe_allow_html=True)
        
        st.info("💡 평소 가장 즐겨 드시는 '이상적인 맛'을 선택해주세요.")
        
        # 섹션 1: 매운맛
        st.markdown("---")
        st.markdown("### 🌶️ 섹션 1: 매운맛")
        
        st.markdown("**1-1. 고추/캡사이신 (칼칼함)**")
        st.caption("혀를 직접 때리는 듯한 매운맛 (예: 불닭볶음면, 틈새라면)")
        capsaicin = st.select_slider(
            "칼칼함 선호도",
            options=[1, 2, 3, 4, 5],
            format_func=lambda x: ["전혀 선호 안함", "살짝 들어간 정도", "적당히 칼칼한 정도", "칼칼한 맛을 즐김", "아주 강한 칼칼함을 선호"][x-1],
            key="pref_capsaicin",
            value=st.session_state.preference_ratings.get('capsaicin', 3)
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown("**1-2. 후추/화자오 (알싸함)**")
        st.caption("입안이 얼얼하고 향이 남는 매운맛 (예: 진짬뽕, 후추가 많은 곰탕)")
        piperine = st.select_slider(
            "알싸함 선호도",
            options=[1, 2, 3, 4, 5],
            format_func=lambda x: ["전혀 선호 안함", "향이 느껴지는 정도", "적당히 알싸한 정도", "알싸한 맛을 즐김", "아주 강한 알싸함을 선호"][x-1],
            key="pref_piperine",
            value=st.session_state.preference_ratings.get('piperine', 3)
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown("**1-3. 마늘/양파 (달큰한 매움)**")
        st.caption("한국적인 감칠맛과 함께 오는 매운맛 (예: 너구리, 안성탕면)")
        garlic = st.select_slider(
            "마늘/양파 선호도",
            options=[1, 2, 3, 4, 5],
            format_func=lambda x: ["전혀 선호 안함", "베이스로 깔린 정도", "적당히 어우러진 정도", "마늘/양파 맛을 즐김", "아주 강한 마늘/양파 맛을 선호"][x-1],
            key="pref_garlic",
            value=st.session_state.preference_ratings.get('garlic', 3)
        )
        
        # 섹션 2: 단맛
        st.markdown("---")
        st.markdown("### 🍭 섹션 2: 단맛")
        
        st.markdown("**2-1. 설탕/시럽 (직관적인 단맛)**")
        st.caption("떡볶이, 짜장라면 등에서 느껴지는 달콤함")
        sugar = st.select_slider(
            "단맛 선호도",
            options=[1, 2, 3, 4, 5],
            format_func=lambda x: ["전혀 선호 안함", "감칠맛을 돋우는 정도", "적당히 달콤한 정도", "달콤한 맛을 즐김", "아주 강한 단맛을 선호"][x-1],
            key="pref_sugar",
            value=st.session_state.preference_ratings.get('sugar', 3)
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown("**2-2. 인공 감미료 (깔끔한 단맛)**")
        st.caption("제로 칼로리 음료 등에서 느껴지는 가벼운 단맛")
        sweetener = st.select_slider(
            "감미료 선호도",
            options=[1, 2, 3, 4, 5],
            format_func=lambda x: ["전혀 선호 안함", "살짝 들어간 정도", "적당한 정도", "감미료의 단맛을 즐김", "아주 강한 감미료 단맛을 선호"][x-1],
            key="pref_sweetener",
            value=st.session_state.preference_ratings.get('sweetener', 3)
        )
        
        # 섹션 3: 짠맛
        st.markdown("---")
        st.markdown("### 🧂 섹션 3: 짠맛")
        
        st.markdown("**3-1. 전반적인 염도**")
        st.caption("국물의 간, 면의 간 등 전반적인 짠 정도")
        saltiness = st.select_slider(
            "염도 선호도",
            options=[1, 2, 3, 4, 5],
            format_func=lambda x: ["싱겁게 먹는 편", "간이 약한 편", "보통 간", "짭짤하게 먹는 편", "간이 센 편"][x-1],
            key="pref_saltiness",
            value=st.session_state.preference_ratings.get('saltiness', 3)
        )
        
        st.markdown("<br><br>", unsafe_allow_html=True)
        
        # 완료 버튼
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("⬅️ 이전", use_container_width=True):
                st.session_state.survey_step -= 1
                st.rerun()
            
            if st.button("🎉 내 입맛 벡터 생성하기", use_container_width=True, type="primary"):
                # 선호도 저장
                st.session_state.preference_ratings = {
                    'capsaicin': capsaicin,
                    'piperine': piperine,
                    'garlic': garlic,
                    'sugar': sugar,
                    'sweetener': sweetener,
                    'saltiness': saltiness
                }
                st.session_state.survey_step += 1
                st.rerun()
    
    # ==================== 완료 화면 ====================
    else:
        st.markdown('<div class="survey-title">🎊 완료!</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="survey-subtitle">{st.session_state.get("user_name", "회원")}님만의 미각 벡터 생성이 완료되었습니다!</div>', unsafe_allow_html=True)
        
        st.balloons()
        
        st.success("✅ 설문이 완료되었습니다!")
        
        # ==================== Json 저장 ====================
        # JSON 데이터 생성 (추가된 부분)
        # user_id는 세션에서 가져오거나 기본값 사용
        user_id = st.session_state.get('user_id', 'user_1')
        
        # JSON 형식으로 데이터 구성
        survey_result = {
            "user_id": user_id,
            "selected_products": st.session_state.selected_ramens,
            "product_ratings": {
                ramen: {
                    "spicy": ratings["spicy"],
                    "salty": ratings["salty"]
                }
                for ramen, ratings in st.session_state.ramen_ratings.items()
            },
            "taste_preferences": {
                "spicy": {
                    "capsaicin": st.session_state.preference_ratings.get('capsaicin', 3),
                    "pepper": st.session_state.preference_ratings.get('piperine', 3),
                    "garlic_onion": st.session_state.preference_ratings.get('garlic', 3)
                },
                "sweet": {
                    "sugar": st.session_state.preference_ratings.get('sugar', 3),
                    "sweetener": st.session_state.preference_ratings.get('sweetener', 3)
                },
                "salty": {
                    "overall_saltiness": st.session_state.preference_ratings.get('saltiness', 3)
                }
            }
        }
        
        # JSON 포맷팅
        json_str = json.dumps(survey_result, ensure_ascii=False, indent=2)
        
        save_path = os.path.join(SAVE_DIR, f"{user_id}_survey.json")
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(survey_result, f, ensure_ascii=False, indent=2)

        st.info(f"💾 설문 결과 저장 완료 → {save_path}")
        


        # ==================== 벡터 생성 (user_vector_generator.py 실행) ====================
        # 벡터 생성
        try:
            output_path = os.path.join(SAVE_DIR, f"{user_id}_taste_vector.json")
            with st.spinner("🧠 사용자 미각 벡터 생성 중..."):
                result = generate_user_vector_from_resources(
                    user_id=user_id,
                    survey_data=survey_result,
                    products=products,
                    model=model,
                    flavorgraph=flavorgraph,
                    client=client,
                    node_names=node_names,
                    node_embeds=node_embeds,
                    output_path=output_path,
                )
            st.success("✅ 사용자 미각 벡터 생성 완료!")
        except Exception as e:
            st.error(f"🚨 벡터 생성 중 오류: {e}")

        # ==================== 결과 벡터 출력 ================
        OUTPUT_PATH = f"data/user/{user_id}_taste_vector.json"
        if os.path.exists(OUTPUT_PATH):
            with open(OUTPUT_PATH, "r", encoding="utf-8") as f:
                result_json = json.load(f)

            st.markdown("---")
            st.markdown("### 🎯 생성된 사용자 미각 벡터")
            st.json(result_json)

        # ==================== 결과 요약 ================
        st.markdown("---")
        st.markdown("### 📊 나의 입맛 프로필")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**선택한 기준 라면**")
            for ramen in st.session_state.selected_ramens:
                st.write(f"- {ramen}")
        
        with col2:
            st.markdown("**선호 맛 강도 (평균)**")
            pref = st.session_state.preference_ratings
            avg_spicy = (pref.get('capsaicin', 3) + pref.get('piperine', 3) + pref.get('garlic', 3)) / 3
            avg_sweet = (pref.get('sugar', 3) + pref.get('sweetener', 3)) / 2
            
            st.metric("🌶️ 매운맛", f"{avg_spicy:.1f}/5")
            st.metric("🍭 단맛", f"{avg_sweet:.1f}/5")
            st.metric("🧂 짠맛", f"{pref.get('saltiness', 3)}/5")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
        with col_btn2:
            if st.button("🏠 홈으로 돌아가기", use_container_width=True, type="primary"):
                # 설문 초기화 (원한다면)
                # st.session_state.survey_step = 1
                st.success("홈 화면으로 이동하려면 왼쪽 메뉴에서 'HOME'을 선택해주세요!")
            
            if st.button("🔄 설문 다시하기", use_container_width=True):
                # 설문 데이터 초기화
                st.session_state.survey_step = 1
                st.session_state.selected_ramens = []
                st.session_state.ramen_ratings = {}
                st.session_state.preference_ratings = {}
                st.rerun()