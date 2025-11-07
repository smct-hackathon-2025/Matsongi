import streamlit as st
import requests
import json
import numpy as np
import os # 파일 저장을 위해
import re 
import update_logic 

API_ENDPOINT_URL = "https://j0bzidcs1d.execute-api.us-east-1.amazonaws.com/chat" 

# 2. (가장 중요!) user_1_taste_vector.json 파일의 정확한 경로 설정
try:
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    USER_VECTOR_PATH = os.path.join(BASE_DIR, "data", "user", "user_1_taste_vector.json") 
    
    if not os.path.exists(USER_VECTOR_PATH):
        print(f"Warning: USER_VECTOR_PATH not found at {USER_VECTOR_PATH}")

except NameError:
    BASE_DIR = os.path.abspath(".")
    USER_VECTOR_PATH = os.path.join(BASE_DIR, "data", "user", "user_1_taste_vector.json")
    print(f"Warning: __file__ not defined. Using relative path: {USER_VECTOR_PATH}")


# --- 헬퍼 함수 (벡터 검색 및 저장) ---

def find_product_matches_by_name(product_name, products_data):
    """
    st.session_state.products에서 'product_name'이 포함된 모든 제품의 'name' 리스트를 반환
    """
    if not products_data:
        return []
    
    matches = []
    product_name_lower = product_name.lower()
    
    for product in products_data:
        product_db_name = product.get('name', '').lower()
        if product_name_lower in product_db_name:
            matches.append(product.get('name')) # 전체 이름을 반환
    return matches

def find_product_vector_by_exact_name(product_name, products_data):
    """
    st.session_state.products에서 'product_name'과 *정확히* 일치하는 제품의 벡터를 반환
    """
    if not products_data:
        return None
    
    product_name_lower = product_name.lower() # 비교를 위해 소문자로
    
    for product in products_data:
        product_db_name = product.get('name', '').lower()
        if product_name_lower == product_db_name: # 정확히 일치(==)하는지 확인
            return product.get('product_vector') 
    return None

def save_user_vector(user_vector):
    """
    업데이트된 유저 벡터를 user_1_taste_vector.json 파일에 덮어쓰는 함수
    {"user_id": ..., "user_taste_vector": ...} 구조를 유지합니다.
    """
    try:
        if isinstance(user_vector, np.ndarray):
            user_vector = user_vector.tolist()
            
        data_to_save = {
            "user_id": "user_1", 
            "user_taste_vector": user_vector 
        }
            
        with open(USER_VECTOR_PATH, 'w', encoding='utf-8') as f:
            json.dump(data_to_save, f, ensure_ascii=False, indent=4)
        print(f"User vector successfully saved to {USER_VECTOR_PATH}")
    except Exception as e:
        print(f"Error saving user vector: {e}")
        st.error(f"벡터를 파일에 저장하는 중 오류 발생: {e}. (경로: {USER_VECTOR_PATH})")


# --- 메인 챗봇 실행 함수 ---

def run_chatbot():
    
    # 스타일링 코드 (전체 포함)
    st.markdown("""
        <style>
        /* 챗봇 타이틀 */
        .chatbot-title {
            font-size: 36px;
            font-weight: bold;
            color: #20314e;
            text-align: center;
            margin-bottom: 10px;
        }
        
        /* 챗 메시지 컨테이너 */
        .stChatMessage {
            background-color: #f8f9fa;
            border-radius: 15px;
            padding: 15px;
            margin: 10px 0;
        }
        
        /* 사용자 메시지 */
        [data-testid="stChatMessageContent"] {
            background-color: #ffffff;
            border-left: 4px solid #fe9600;
            padding: 12px;
            border-radius: 10px;
        }
        
        /* AI 메시지 */
        .stChatMessage[data-testid="assistant"] {
            background-color: #f0f4f8;
            border-left: 4px solid #20314e;
        }
        
        /* 채팅 입력창 */
        .stChatInput > div {
            border: 2px solid #20314e;
            border-radius: 25px;
        }
        
        .stChatInput > div:focus-within {
            border-color: #fe9600;
            box-shadow: 0 0 0 2px rgba(254, 150, 0, 0.2);
        }
        
        /* 전송 버튼 */
        .stChatInput button {
            background-color: #fe9600 !important;
            color: white !important;
            border-radius: 50%;
        }
        
        .stChatInput button:hover {
            background-color: #e58700 !important;
        }
        
        /* 스크롤바 커스터마이징 */
        ::-webkit-scrollbar {
            width: 8px;
        }
        
        ::-webkit-scrollbar-track {
            background: #f1f1f1;
        }
        
        ::-webkit-scrollbar-thumb {
            background: #20314e;
            border-radius: 4px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: #fe9600;
        }
        
        /* 채팅 영역 */
        .chat-container {
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # 챗봇 페이지 타이틀
    st.markdown('<div class="chatbot-title">🤖 챗봇</div>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #5D6D7E; margin-bottom: 30px;">제가 추천한 라면은 어떠셨나요?! 후기를 남겨주시면 입맛에 반영할게요.</p>', unsafe_allow_html=True)

    # --- 4. 챗봇 상태 관리 (동일) ---
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "chat_mode" not in st.session_state:
        st.session_state.chat_mode = "normal"
    if "review_product_context" not in st.session_state:
        st.session_state.review_product_context = {"name": None, "vector": None}
    # --- ---------------------------

    # 5. 채팅 UI (동일)
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    st.markdown('</div>', unsafe_allow_html=True)

    # 6. 사용자 입력 처리
    if user_input := st.chat_input("메시지를 입력하세요..."):
        
        # 사용자 메시지는 항상 UI에 추가하고 표시
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        # -----------------------------------------------
        # 6-A. "상품명"을 기다리던 상태일 때 (동일)
        # -----------------------------------------------
        if st.session_state.chat_mode == "awaiting_product_name":
            if "취소" in user_input.lower():
                st.session_state.chat_mode = "normal"
                response = "알겠습니다. 후기 작성을 취소합니다."
                st.session_state.messages.append({"role": "assistant", "content": response})
                with st.chat_message("assistant"):
                    st.markdown(response)
                st.rerun() 
                return 

            product_name_input = user_input 
            product_vector = None
            product_name_found = None
            response = None 

            product_vector = find_product_vector_by_exact_name(product_name_input, st.session_state.get("products", []))
            
            if product_vector:
                product_name_found = product_name_input
            else:
                partial_matches = find_product_matches_by_name(product_name_input, st.session_state.get("products", []))
                
                if len(partial_matches) == 1:
                    product_name_found = partial_matches[0]
                    product_vector = find_product_vector_by_exact_name(product_name_found, st.session_state.get("products", []))
                
                elif len(partial_matches) > 1:
                    response = f"'{product_name_input}'과(와) 일치하는 상품이 여러 개 있습니다. 아래 목록에서 정확한 상품명을 복사/입력해주세요.\n\n"
                    for name in partial_matches[:10]:
                        response += f"- {name}\n"
                    response += "\n\n(후기 작성을 그만두려면 '취소'라고 입력하세요)"
                
                else:
                    response = f"'{product_name_input}' 상품을 찾지 못했어요. 정확한 상품명을 다시 알려주시겠어요? (후기 작성을 그만두려면 '취소'라고 입력하세요)"

            if product_name_found and product_vector:
                st.session_state.review_product_context = {"name": product_name_found, "vector": product_vector}
                st.session_state.chat_mode = "awaiting_review_text" # 다음 상태로
                response = f"'{product_name_found}' 상품으로 후기를 진행합니다. 맛이 어떠셨나요? (예: '짰어요', '매콤하고 좋았어요.')"
            elif product_name_found and not product_vector:
                response = f"'{product_name_found}' 상품은 찾았지만 벡터를 찾지 못했습니다. DB를 확인해주세요."

            st.session_state.messages.append({"role": "assistant", "content": response})
            with st.chat_message("assistant"):
                st.markdown(response)

        # -----------------------------------------------
        # 6-B. "후기 텍스트"를 기다리던 상태일 때 (!!! 님의 요청대로 수정 !!!)
        # -----------------------------------------------
        elif st.session_state.chat_mode == "awaiting_review_text":
            review_text = user_input
            product_name = st.session_state.review_product_context["name"]
            product_vector = st.session_state.review_product_context["vector"]
            
            with st.chat_message("assistant"):
                with st.spinner(f"후기 분석 및 입맛 반영 중..."):
                    
                    user_vector = st.session_state.get("user_vector") 

                    if not user_vector or not product_vector:
                        st.error("입맛 벡터 또는 상품 벡터를 찾을 수 없습니다. '내 입맛 찾기'를 먼저 완료해주세요.")
                        st.session_state.chat_mode = "normal"
                        return

                    # 1. (!!!) Bedrock에 보낼 '가벼운 긍/부정' 프롬프트 생성
                    # (벡터 2개를 보내지 않습니다!)
                    sentiment_prompt = f"""
                    다음 음식 후기를 분석하고, 이 후기가 'positive'(긍정), 'negative'(부정), 'neutral'(중립) 중 무엇인지 영어 단어 하나로만 대답해.
                    
                    후기: "{review_text}"
                    
                    답변 (positive, negative, neutral 중 하나):
                    """
                    
                    bot_response = ""
                    try:
                        # 2. API Gateway 호출 (가벼운 요청 -> 503/차원 불일치 오류 해결!)
                        response = requests.post(
                            API_ENDPOINT_URL, 
                            data=json.dumps({"prompt": sentiment_prompt}),
                            headers={"Content-Type": "application/json"}
                        )
                        
                        if response.status_code == 200:
                            response_body_text = response.json().get("response", "neutral")
                            
                            # 3. AI 응답에서 긍/부정 추출 (by update_logic.py)
                            sentiment = update_logic.get_sentiment(response_body_text)
                            
                            # 4. 벡터 수학 (by update_logic.py)
                            # (!!!) 모든 계산은 Lambda가 아닌 로컬에서 일어남
                            new_vector = update_logic.run_update(user_vector, product_vector, sentiment)

                            # 5. 로컬 세션 및 파일 저장
                            if isinstance(new_vector, list) and len(new_vector) == len(user_vector):
                                st.session_state.user_vector = new_vector
                                save_user_vector(new_vector) 
                                bot_response = "소중한 후기 감사합니다! 님의 입맛 정보에 반영했어요."
                            else:
                                bot_response = "벡터 계산 중 오류가 발생했습니다."
                        
                        else:
                            bot_response = f"죄송합니다, AI 서버에서 오류가 발생했습니다. (코드: {response.status_code})\n오류: {response.text}"
                    
                    except Exception as e:
                        bot_response = f"API 호출 중 심각한 오류 발생: {e}"
                    
                    st.markdown(bot_response)
                    st.session_state.messages.append({"role": "assistant", "content": bot_response})
                    
                    # 상태 초기화
                    st.session_state.chat_mode = "normal" 
                    st.session_state.review_product_context = {"name": None, "vector": None}

        # -----------------------------------------------
        # 6-C. "일반 대화" 상태일 때 (동일)
        # -----------------------------------------------
        else: # st.session_state.chat_mode == "normal"
            
            # "후기" 키워드 감지
            if "후기" in user_input or "리뷰" in user_input or "먹어봤" in user_input:
                if not st.session_state.get("user_vector"):
                    response = "후기를 남기시려면 먼저 '내 입맛 찾기' 탭에서 설문조사를 완료해주세요!"
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    with st.chat_message("assistant"):
                        st.markdown(response)
                else:
                    st.session_state.chat_mode = "awaiting_product_name" # 상태 변경
                    response = "좋습니다! 어떤 상품에 대한 후기인가요? 상품명을 정확히 알려주세요."
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    with st.chat_message("assistant"):
                        st.markdown(response)
            
            elif "취소" in user_input.lower():
                   st.session_state.chat_mode = "normal" # 상태 초기화
                   response = "알겠습니다. 언제든 다시 불러주세요."
                   st.session_state.messages.append({"role": "assistant", "content": response})
                   with st.chat_message("assistant"):
                        st.markdown(response)

            # 일반 대화 (기존 API 호출)
            else:
                with st.chat_message("assistant"):
                    with st.spinner("AI가 생각 중입니다..."):
                        try:
                            response = requests.post(
                                API_ENDPOINT_URL, 
                                data=json.dumps({"prompt": user_input}),
                                headers={"Content-Type": "application/json"}
                            )
                            if response.status_code == 200:
                                bot_response = response.json().get("response", "오류: 응답이 없습니다.")
                            else:
                                bot_response = f"죄송합니다, 오류가 발생했습니다. (코드: {response.status_code})"
                        except Exception as e:
                            bot_response = f"API 호출 중 심각한 오류 발생: {e}"
                        
                        st.markdown(bot_response)
                st.session_state.messages.append({"role": "assistant", "content": bot_response})

# 이 파일이 메인으로 실행될 경우(테스트용)
if __name__ == "__main__":
    
        
    run_chatbot()