from __future__ import annotations

import importlib
import sys
from functools import lru_cache
from types import ModuleType
from typing import Dict
from pathlib import Path

import streamlit as st

# ──────────────────────────────────────────────────────────────
# ✅ [핵심] 경로 문제 방지: 루트 경로를 sys.path에 추가!
# ──────────────────────────────────────────────────────────────
# 루트: app.py 기준 상위 경로
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.append(str(PROJECT_ROOT))

# ──────────────────────────────────────────────────────────────
# Streamlit 기본 설정
# ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="보안 점검 시스템",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────────────────────
# ✅ [중요] 실제 폴더 구조에 맞게 import 경로 점검
# 예) WebPage/pages/page_1_main_page.py 이면 → 'WebPage.pages.page_1_main_page'
# ──────────────────────────────────────────────────────────────
PAGES: Dict[str, str] = {
    "🏠 메인페이지":       "WebPage.pages.page_1_main_page",
    "✅ 점검":             "WebPage.pages.page_5_scanpage",
    "📋 진단 결과 분석":   "WebPage.pages.page_3_diagnosis_result",
}

CAPTIONS: Dict[str, str] = {
    "🏠 메인페이지":       "시스템 개요 및 안내 페이지입니다.",
    "✅ 점검":             "선택 서버에 대해 실시간 보안 점검을 수행합니다.",
    "📋 진단 결과 분석":   "전체 진단 결과를 테이블로 확인하고 조치 방법을 검토합니다.",
}

# ──────────────────────────────────────────────────────────────
# 최초 진입 시 기본 페이지 설정
# ──────────────────────────────────────────────────────────────
if "current_page" not in st.session_state:
    st.session_state.current_page = next(iter(PAGES))  # 첫 항목

@lru_cache(maxsize=None)
def _import_page(module_path: str) -> ModuleType:
    """동적 import + 캐싱"""
    return importlib.import_module(module_path)

# ──────────────────────────────────────────────────────────────
# 사이드바 UI
# ──────────────────────────────────────────────────────────────
st.sidebar.title("🛡️ 보안 점검 시스템")
st.sidebar.markdown("---")

page_selection = st.sidebar.radio(
    "🧭 **페이지 이동**",
    list(PAGES.keys()),
    index=list(PAGES.keys()).index(st.session_state.current_page),
    key="current_page",
)

st.sidebar.caption(CAPTIONS[page_selection])
st.sidebar.markdown("---")
st.sidebar.metric("연결 상태", "🟢 정상")
st.sidebar.caption("© 2025 보안 점검 시스템 v1.0.0")

# ──────────────────────────────────────────────────────────────
# 페이지 렌더링
# ──────────────────────────────────────────────────────────────
try:
    _import_page(PAGES[page_selection]).show()
except ModuleNotFoundError as err:
    st.error(f"❌ 모듈을 찾을 수 없습니다: `{PAGES[page_selection]}`\n\n{err}")
    st.info("📌 import 경로와 폴더 구조를 다시 확인해주세요!")
except Exception as err:
    st.exception(err)
    st.info("🔄 새로고침 후 다시 시도해 주세요.")
