import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from langchain.prompts import ChatPromptTemplate
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# GPT 모델 설정
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.4)

# 프롬프트 템플릿 (보안 자동화 전문가로 설정)
chat_prompt = ChatPromptTemplate.from_messages([
    ("system", 
     "너는 리눅스, 윈도우 서버 보안 및 인프라 자동화 전문가야. "
     "CCE 기반 취약점 진단, Ansible을 활용한 서버 보안 점검 자동화, "
     "OS별 패키지 관리, SSH 설정, 시스템 로그 분석, 네트워크 포트 점검 등에 대한 "
     "기술적인 질문에 정확하고 명확하게 답해줘."),
    ("user", "{question}")
])

# 체인 생성
chain = chat_prompt | llm

# Streamlit 페이지 설정
st.set_page_config(page_title="보안 자동화 챗봇", page_icon="🛡️", layout="centered")

# 🔧 메시지 스타일 조정 (폰트 크기/줄 간격)
st.markdown("""
<style>
.chat-message p {
    font-size: 14px !important;
    line-height: 1.6 !important;
    margin-bottom: 10px;
}
</style>
""", unsafe_allow_html=True)

# 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []

# 타이틀
st.title("🛡️ 보안 자동화 AI 챗봇")
st.write("Ubuntu, CentOS, Windows Server 기반 보안 점검 및 Ansible 자동화 관련 질문을 자유롭게 하세요.")

# 이전 메시지 출력
for msg in st.session_state.messages:
    if isinstance(msg, HumanMessage):
        with st.chat_message("user"):
            st.markdown(msg.content)
    elif isinstance(msg, AIMessage):
        with st.chat_message("assistant"):
            st.markdown(msg.content)

# 사용자 입력 처리
user_input = st.chat_input("보안 관련 궁금한 점을 물어보세요.")
if user_input:
    st.session_state.messages.append(HumanMessage(content=user_input))
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.spinner("답변 생성 중..."):
        try:
            response = chain.invoke({"question": user_input})
            result = response.content
        except Exception as e:
            result = f"❌ 오류 발생: {e}"

    st.session_state.messages.append(AIMessage(content=result))
    with st.chat_message("assistant"):
        st.markdown(result)