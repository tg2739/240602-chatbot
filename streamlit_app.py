import streamlit as st
from openai import OpenAI

# 페이지 설정
st.set_page_config(
    page_title="과학 탐험 챗봇", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# 커스텀 CSS 스타일링 - 아이들을 위한 밝고 재미있는 디자인
st.markdown("""
    <style>
    .main-header {
        text-align: center;
        color: #FF6B6B;
        font-size: 2.5em;
        font-weight: bold;
        margin-bottom: 10px;
    }
    .sub-header {
        text-align: center;
        color: #4ECDC4;
        font-size: 1.2em;
        margin-bottom: 20px;
    }
    .info-box {
        background-color: #FFF3CD;
        border-left: 4px solid #FFC107;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
    .success-box {
        background-color: #D4EDDA;
        border-left: 4px solid #28A745;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
    </style>
""", unsafe_allow_html=True)

# Title과 설명
st.markdown('<div class="main-header">🔬 과학 탐험 챗봇</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">과학의 신비로운 세계를 함께 탐험해요!</div>', unsafe_allow_html=True)

st.write(
    "과학은 우리 주변의 모든 것을 설명해 주는 신비한 도구예요! 🌍 이 챗봇과 함께 "
    "흥미로운 질문을 하고, 과학의 재미있는 원리를 배워보세요. 궁금한 것을 물어보면 "
    "함께 생각하며 깨닫게 될 거예요!"
)

# ===== 사이드바 설정 =====
st.sidebar.title("⚙️ 설정")

# OpenAI API Key
openai_api_key = st.sidebar.text_input("OpenAI API Key", type="password")

# 모델 설정을 위한 expandable 섹션
with st.sidebar.expander("🤖 모델 설정", expanded=True):
    # 사용 가능한 모델 목록
    available_models = [
        "gpt-4-turbo",
        "gpt-4",
        "gpt-3.5-turbo",
        "gpt-4o",
        "gpt-4o-mini"
    ]
    
    selected_model = st.selectbox(
        "모델 선택",
        options=available_models,
        index=2,
        help="어떤 AI 모델을 사용할지 선택하세요"
    )
    
    # 난이도 설정
    difficulty_level = st.radio(
        "🎓 설명 난이도",
        options=["초급 (쉬워요)", "중급 (적당해요)", "고급 (어려워요)"],
        index=1,
        help="아이의 수준에 맞게 선택하세요"
    )
    
    # 시스템 프롬프트 (난이도에 따라 동적으로 변경)
    difficulty_map = {
        "초급 (쉬워요)": "너는 초등학교 1-3학년 아이들이 성장할 수 있게 도와주는 친절한 과학 선생님이야. 아주 간단하고 친근한 예시(장난감, 동물, 음식 등)를 들어서 설명해주고, 아이들이 깨닫을 수 있게 질문을 계속 던져줘. 과학의 기본 개념을 쉽게 이해할 수 있도록 도와주세요.",
        "중급 (적당해요)": "너는 초등학교 4-6학년 아이들이 성장할 수 있게 도와주는 과학 선생님이야. 아이들의 수준을 파악해서 답을 알려주기 보다는 조금 위 수준을 알려주고 그러다 보면 아이들이 깨닫을 수 있게 질문을 계속 던져줘. 재미있는 예시와 함께 과학 이론을 설명하세요.",
        "고급 (어려워요)": "너는 초등학교 고학년 아이들이 더 깊이 있게 과학을 이해할 수 있게 도와주는 과학 선생님이야. 아이들의 호기심을 자극하는 질문을 던지고, 실험적 사고를 격려하며, 과학의 연결성을 보도록 도와줘. 복잡한 개념도 단계적으로 설명해주세요."
    }
    
    system_prompt = difficulty_map[difficulty_level]
    
    st.text_area(
        "시스템 프롬프트",
        value=system_prompt,
        height=100,
        disabled=True,
        help="난이도에 따라 자동으로 설정됩니다"
    )
    
    # Temperature 슬라이더
    temperature = st.slider(
        "창의성 레벨 🎨",
        min_value=0.0,
        max_value=2.0,
        value=1.2,
        step=0.1,
        disabled=True,
        help="창의적인 답변을 위해 고정되었습니다"
    )
    
    # Max Tokens
    max_tokens = st.number_input(
        "답변 길이",
        min_value=100,
        max_value=4000,
        value=1500,
        step=100,
        help="답변의 최대 길이를 조절하세요"
    )

# 사이드바에 초기화 버튼 추가
st.sidebar.markdown("---")
col1, col2 = st.sidebar.columns(2)
with col1:
    if st.button("🔄 새로운 대화", use_container_width=True, key="reset_chat"):
        st.session_state.messages = []
        st.rerun()

with col2:
    if st.button("💾 대화 저장", use_container_width=True, key="save_chat"):
        if st.session_state.messages:
            chat_text = "\n".join([f"{msg['role'].upper()}: {msg['content']}" for msg in st.session_state.messages])
            st.download_button(
                label="다운로드",
                data=chat_text,
                file_name="과학탐험_대화.txt",
                mime="text/plain",
                key="download_chat"
            )

# 현재 난이도 표시
st.sidebar.markdown(f"**현재 난이도**: {difficulty_level}")

if not openai_api_key:
    st.markdown('<div class="info-box"><h3>🔑 API 키를 입력해주세요!</h3> OpenAI API 키를 사이드바에 입력하면 챗봇과 대화할 수 있어요.</div>', unsafe_allow_html=True)
else:

    # Create an OpenAI client.
    client = OpenAI(api_key=openai_api_key)

    # Create a session state variable to store the chat messages.
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "message_feedback" not in st.session_state:
        st.session_state.message_feedback = {}

    # Display the existing chat messages
    for idx, message in enumerate(st.session_state.messages):
        with st.chat_message(message["role"], avatar="👨‍🔬" if message["role"] == "assistant" else "👧"):
            st.markdown(message["content"])
            
            # 어시스턴트 메시지에 대한 피드백 버튼 추가
            if message["role"] == "assistant":
                col1, col2, col3 = st.columns([1, 1, 3])
                with col1:
                    if st.button("👍", key=f"like_{idx}"):
                        st.session_state.message_feedback[idx] = "good"
                        st.success("좋은 답변이라고 표시했어요!")
                with col2:
                    if st.button("👎", key=f"dislike_{idx}"):
                        st.session_state.message_feedback[idx] = "bad"
                        st.info("더 나은 답변을 원하신다고 표시했어요!")

    # Chat input
    if prompt := st.chat_input("궁금한 과학 질문을 해보세요! 🤔"):

        # Store and display the current prompt.
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="👧"):
            st.markdown(prompt)

        # Generate a response using the OpenAI API.
        with st.spinner("🔬 과학 선생님이 생각하고 있어요..."):
            stream = client.chat.completions.create(
                model=selected_model,
                messages=[
                    {"role": "system", "content": system_prompt}
                ] + [
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
                stream=True,
                temperature=temperature,
                max_tokens=max_tokens,
            )

            # Stream the response to the chat
            with st.chat_message("assistant", avatar="👨‍🔬"):
                response = st.write_stream(stream)
            st.session_state.messages.append({"role": "assistant", "content": response})
            
            # 새 메시지에 대한 피드백 버튼
            st.markdown("---")
            col1, col2, col3 = st.columns([1, 1, 3])
            with col1:
                if st.button("👍", key=f"like_{len(st.session_state.messages)-1}"):
                    st.success("좋은 답변이라고 표시했어요!")
            with col2:
                if st.button("👎", key=f"dislike_{len(st.session_state.messages)-1}"):
                    st.info("더 나은 답변을 원하신다고 표시했어요!")

# 하단에 팁 표시
st.markdown("---")
st.markdown("""
### 💡 대화 팁
- 🔍 **자세히 물어보세요**: "왜?", "어떻게?" 같은 질문이 더 좋아요
- 🌍 **주변 세상과 연결해보세요**: 일상에서 과학을 찾아보세요
- 🧪 **실험해보세요**: 배운 내용을 직접 해봐요
- 📚 **계속 탐험하세요**: 하나의 질문이 새로운 질문을 만들어요!
""")
