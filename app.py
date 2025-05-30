import streamlit as st
import google.generativeai as genai
from datetime import datetime

# 페이지 설정
st.set_page_config(
    page_title="Gemini GPTs 봇",
    page_icon="🤖",
    layout="wide"
)

# 스타일 설정
st.markdown("""
<style>
    /* 메시지 컨테이너 스타일 */
    .chat-message {
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        display: flex;
        flex-direction: column;
        max-width: 80%;
    }
    
    .user-message {
        background-color: #e6f3ff;
        margin-left: auto;
        border-bottom-right-radius: 0;
    }
    
    .bot-message {
        background-color: #f0f2f6;
        margin-right: auto;
        border-bottom-left-radius: 0;
    }
    
    /* 역할 표시 스타일 */
    .role-display {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f0f2f6;
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []

if "role" not in st.session_state:
    st.session_state.role = "당신은 친절한 AI 어시스턴트입니다."

# Gemini 설정
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    model = genai.GenerativeModel("gemini-1.5-flash")
except Exception as e:
    st.error("API 키 설정에 문제가 발생했습니다. .streamlit/secrets.toml 파일에 유효한 API 키가 설정되어 있는지 확인해주세요.")
    st.stop()

# 사이드바 - 역할 설정
with st.sidebar:
    st.title("🤖 역할 설정")
    new_role = st.text_area(
        "AI의 역할을 설정해주세요",
        value=st.session_state.role,
        height=150,
        help="AI의 성격, 말투, 전문 분야 등을 자유롭게 설정할 수 있습니다."
    )
    
    if st.button("프롬프트 적용", type="primary"):
        st.session_state.role = new_role
        st.session_state.messages = []  # 대화 초기화
        st.rerun()

# 메인 화면 - 현재 역할 표시
st.markdown(f"""
<div class="role-display">
    <h3>🎭 현재 역할</h3>
    <p>{st.session_state.role}</p>
</div>
""", unsafe_allow_html=True)

# 채팅 메시지 표시
for message in st.session_state.messages:
    role = message["role"]
    content = message["content"]
    
    # HTML로 메시지 스타일링
    if role == "user":
        st.markdown(f"""
        <div class="chat-message user-message">
            <p>{content}</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="chat-message bot-message">
            <p>{content}</p>
        </div>
        """, unsafe_allow_html=True)

# 사용자 입력
user_input = st.chat_input("메시지를 입력하세요")

if user_input:
    # 사용자 메시지 추가
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # 로딩 표시
    with st.status("생각하는 중...", expanded=True) as status:
        try:
            # 대화 컨텍스트 구성
            chat = model.start_chat(history=[])
            context = [st.session_state.role]  # 역할 설정을 컨텍스트의 시작으로 추가
            
            # 이전 대화 기록 추가
            for msg in st.session_state.messages:
                context.append(f"{'사용자' if msg['role'] == 'user' else 'AI'}: {msg['content']}")
            
            # Gemini API 호출
            response = chat.send_message(
                "\n".join(context),
                generation_config={
                    "temperature": 0.7,
                    "max_output_tokens": 2048,
                }
            )
            
            # 응답 메시지 추가
            bot_message = response.text
            st.session_state.messages.append({"role": "assistant", "content": bot_message})
            
            status.update(label="답변 완료!", state="complete", expanded=False)
            
        except Exception as e:
            st.error(f"""
            죄송합니다. 응답 생성 중에 문제가 발생했습니다.
            잠시 후 다시 시도해주세요.
            
            오류 내용: {str(e)}
            """)
            
        st.rerun()  # 화면 갱신
