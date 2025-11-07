import streamlit as st

# boto3를 내부적으로 래핑하여 LangChain 인터페이스 제공
from langchain_aws.chat_models.bedrock import ChatBedrock

# LangChain은 메시지를 객체로 관리 (단순 dict가 아님)
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

def run_chatbot():
    # 스타일링
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
    
    # Streamlit 페이지 설정
    st.markdown('<div class="chatbot-title">🤖 챗봇</div>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #5D6D7E; margin-bottom: 30px;">제가 추천한 라면은 어떠셨나요?!</p>', unsafe_allow_html=True)

    # 세션 상태 초기화
    # messages: UI 표시용 (dict 형태로 저장)
    if "messages" not in st.session_state:
        st.session_state.messages = []
    # langchain_messages: LangChain API 호출용 (HumanMessage, AIMessage 객체)
    if "langchain_messages" not in st.session_state:
        st.session_state.langchain_messages = []


    # # LangChain ChatBedrock 모델 초기화
    # @st.cache_resource  # 앱 재실행 시에도 모델 객체를 재생성하지 않음 (성능 최적화)
    # def get_llm():
    #     return ChatBedrock(
    #         model_id="",
    #         region_name="",
    #         model_kwargs={
    #             "max_tokens": 1000,
    #             "temperature": 0.7,
    #         },
    #         streaming=True,
    #     )


    # llm = get_llm()

    # # 채팅 프롬프트 템플릿 설정
    # prompt_template = ChatPromptTemplate.from_messages(
    #     [
    #         # MessagesPlaceholder는 "여기에 메시지 리스트가 들어갈 자리"를 예약하는 것
    #         MessagesPlaceholder(variable_name="chat_history"),
    #         ("human", "{input}"),
    #     ]
    # )

    # # 채팅 체인 구성
    # chain = prompt_template | llm

    # 채팅 컨테이너
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    
    # 기존 대화 내역 표시
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    st.markdown('</div>', unsafe_allow_html=True)

    # 사용자 입력 처리
    if user_input := st.chat_input("메시지를 입력하세요..."):
        # 사용자 메시지 추가 및 표시
        # UI 표시용 저장
        st.session_state.messages.append({"role": "user", "content": user_input})
        # LangChain API 호출용 저장
        st.session_state.langchain_messages.append(HumanMessage(content=user_input))

        with st.chat_message("user"):
            st.markdown(user_input)

        # # AI 응답 생성 및 스트리밍
        # with st.chat_message("assistant"):
        #     response_placeholder = st.empty()
        #     full_response = ""

        #     # 스트리밍 응답 처리
        #     for chunk in chain.stream(
        #         {
        #             # chat_history: 이전 대화들 (마지막 사용자 메시지 제외)
        #             "chat_history": st.session_state.langchain_messages[:-1],
        #             # input: 현재 사용자 입력
        #             "input": user_input,
        #         }
        #     ):
        #         full_response += chunk.content
        #         # 화면에 실시간으로 업데이트 (▌는 타이핑 중 커서 효과)
        #         response_placeholder.markdown(full_response + "▌")

        #     # 스트리밍 완료 후 커서 제거하고 최종 응답만 표시
        #     response_placeholder.markdown(full_response)

        # # UI 표시용 저장
        # st.session_state.messages.append({"role": "assistant", "content": full_response})
        # # LangChain API 호출용 저장
        # st.session_state.langchain_messages.append(AIMessage(content=full_response))
        
        # 임시 응답 (모델 연결 전)
        with st.chat_message("assistant"):
            temp_response = "안녕하세요! 현재 AI 모델 연결 대기 중입니다. 🤖"
            st.markdown(temp_response)
        
        st.session_state.messages.append({"role": "assistant", "content": temp_response})
        st.session_state.langchain_messages.append(AIMessage(content=temp_response))