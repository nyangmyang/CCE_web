import streamlit as st

def show():
    """호스트 추가 페이지"""
    
    st.title("호스트 추가")
    st.write("여기에서 호스트를 추가할 수 있습니다.")
    
    if st.button("완료", key="complete"):
        st.success("호스트가 추가되었습니다.")
        st.session_state["show_modal"] = False  # Close the modal