import streamlit as st
from openai import OpenAI

# 페이지 설정
st.set_page_config(page_title="Chatbot", layout="wide")

# Show title and description.
st.title("💬 Chatbot")
st.write(
    "This is a simple chatbot that uses OpenAI's GPT models to generate responses. "
    "To use this app, you need to provide an OpenAI API key, which you can get [here](https://platform.openai.com/account/api-keys). "
    "You can customize the model settings in the sidebar."
)

# ===== 사이드바 설정 =====
st.sidebar.title("⚙️ Settings")

# OpenAI API Key
openai_api_key = st.sidebar.text_input("OpenAI API Key", type="password")

# 모델 설정을 위한 expandable 섹션
with st.sidebar.expander("🤖 Model Configuration", expanded=True):
    # 사용 가능한 모델 목록
    available_models = [
        "gpt-4-turbo",
        "gpt-4",
        "gpt-3.5-turbo",
        "gpt-4o",
        "gpt-4o-mini"
    ]
    
    selected_model = st.selectbox(
        "Select Model",
        options=available_models,
        index=2,  # gpt-3.5-turbo가 기본값
        help="Choose the AI model to use for responses"
    )
    
    # 시스템 프롬프트
    system_prompt = st.text_area(
        "System Prompt",
        value="You are a helpful assistant.",
        height=100,
        help="Define the behavior and role of the assistant"
    )
    
    # Temperature 슬라이더
    temperature = st.slider(
        "Temperature",
        min_value=0.0,
        max_value=2.0,
        value=0.7,
        step=0.1,
        help="Higher values make the output more random, lower values make it more deterministic"
    )
    
    # Max Tokens
    max_tokens = st.number_input(
        "Max Tokens",
        min_value=100,
        max_value=4000,
        value=1000,
        step=100,
        help="Maximum length of the response"
    )

if not openai_api_key:
    st.info("Please add your OpenAI API key in the sidebar to continue.", icon="🗝️")
else:

    # Create an OpenAI client.
    client = OpenAI(api_key=openai_api_key)

    # Create a session state variable to store the chat messages. This ensures that the
    # messages persist across reruns.
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display the existing chat messages via `st.chat_message`.
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Create a chat input field to allow the user to enter a message. This will display
    # automatically at the bottom of the page.
    if prompt := st.chat_input("What is up?"):

        # Store and display the current prompt.
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate a response using the OpenAI API.
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

        # Stream the response to the chat using `st.write_stream`, then store it in 
        # session state.
        with st.chat_message("assistant"):
            response = st.write_stream(stream)
        st.session_state.messages.append({"role": "assistant", "content": response})
