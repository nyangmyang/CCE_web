from __future__ import annotations

from typing import List, Dict

import streamlit as st
from WebPage.styles.style import STYLES  # 🌐 CSS 공용

# 외부 모듈(HTML 그리드) 지연 import
@st.cache_resource(show_spinner=False)
def _lazy_import_components():
    from WebPage.components.host_card import render_host_grid  # type: ignore
    return render_host_grid

# 샘플 데이터
HOSTS: List[Dict] = [
    {
        "icon": "https://upload.wikimedia.org/wikipedia/commons/5/5f/Windows_logo_-_2012.svg",
        "ip": "8.8.8.8",
        "port": 2222,
        "desc": "웹서버",
        "importance": "상"
    },
    {
        "icon": "https://upload.wikimedia.org/wikipedia/commons/6/63/CentOS_color_logo.svg",
        "ip": "8.8.8.8",
        "port": 2222,
        "desc": "DB서버",
        "importance": "상"
    },
    {
        "icon": "https://upload.wikimedia.org/wikipedia/commons/5/5f/Windows_logo_-_2012.svg",
        "ip": "1.1.1.1",
        "port": 22,
        "desc": "테스트",
        "importance": "중"
    },
    {
        "icon": "https://upload.wikimedia.org/wikipedia/commons/6/63/CentOS_color_logo.svg",
        "ip": "192.168.0.10",
        "port": 2200,
        "desc": "Demo",
        "importance": "하"
    },
    {
        "icon": "https://upload.wikimedia.org/wikipedia/commons/5/5f/Windows_logo_-_2012.svg",
        "ip": "192.168.1.100",
        "port": 3389,
        "desc": "파일서버",
        "importance": "중"
    },
    {
        "icon": "https://upload.wikimedia.org/wikipedia/commons/6/63/CentOS_color_logo.svg",
        "ip": "10.0.0.5",
        "port": 22,
        "desc": "백업서버",
        "importance": "상"
    },
    {
        "icon": "https://upload.wikimedia.org/wikipedia/commons/5/5f/Windows_logo_-_2012.svg",
        "ip": "172.16.0.50",
        "port": 80,
        "desc": "모니터링",
        "importance": "중"
    },
    {
        "icon": "https://upload.wikimedia.org/wikipedia/commons/6/63/CentOS_color_logo.svg",
        "ip": "172.16.0.51",
        "port": 443,
        "desc": "로그서버",
        "importance": "하"
    }
]

# ──────────────────────────────────────────────────────────────────────────────
def show() -> None:
    st.markdown(STYLES, unsafe_allow_html=True)
    st.header("✅ 호스트 점검")

    render_host_grid = _lazy_import_components()

    # 호스트 목록 캐싱
    if "hosts" not in st.session_state:
        st.session_state.hosts = HOSTS.copy()

    # 그리드 표시
    st.markdown("### 대상 호스트")

    # 호스트 추가 버튼 (우측 상단)
    col_space, col_btn = st.columns([8, 2])  # Adjusted column proportions for alignment
    with col_btn:
        if st.button("호스트 추가", key="add_host"):
            st.session_state["show_modal"] = True  # Set modal state to True
    
    # 콘텐츠 영역 (스크롤 가능)
    content_html = f"""
    <div class='content-area'>
        {render_host_grid(st.session_state.hosts)}
    </div>
    """
    st.markdown(content_html, unsafe_allow_html=True)

    # 호스트 추가 폼
    with st.expander("➕ 호스트 추가", expanded=False):
        icon = st.text_input("아이콘(URL 또는 emoji)", value="🖥️")
        ip = st.text_input("IP 주소", value="")
        port = st.number_input("Port", value=22, step=1)
        desc = st.text_input("설명", value="")
        importance = st.selectbox("중요도", ["상", "중", "하"])
        add_btn = st.button("추가", key="add_host_btn")
        if add_btn and ip:
            st.session_state.hosts.append(
                dict(icon=icon, ip=ip, port=port, desc=desc, importance=importance)
            )
            st.success(f"{ip} 추가 완료!")
            st.experimental_rerun()

    # 실행 버튼
    if st.button("🛠️ 선택 호스트 점검", use_container_width=True):
        with st.spinner("스캔 중…"):
            st.time.sleep(1)  # Fixed incorrect function call
        st.success("🎉 점검 완료!")


if __name__ == "__main__":
    st.set_page_config(page_title="호스트 점검", layout="wide")
    show()