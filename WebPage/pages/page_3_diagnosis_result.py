from __future__ import annotations

import json
import os
from datetime import datetime
from functools import lru_cache
from typing import Dict, List

import pandas as pd
import streamlit as st

# 외부 모듈 지연 import ---------------------------------------------------------
@st.cache_resource(show_spinner=False)
def _lazy_parsing_proc():
    from Parsing.parsingMain import process_json_files
    return process_json_files

# JSON → DataFrame -------------------------------------------------------------
@st.cache_data(show_spinner=False)
def _load_df(result_dir: str) -> pd.DataFrame:
    rows: List[Dict] = []
    for fname in os.listdir(result_dir):
        if not fname.endswith(".json"):
            continue
        with open(os.path.join(result_dir, fname), encoding="utf-8") as fp:
            js = json.load(fp)
        rows.extend(_parse_json(js, fname))
    return pd.DataFrame(rows)


def _parse_json(js: Dict, fname: str) -> List[Dict]:
    imp = {1: "하", 2: "중", 3: "상"}.get
    risk = {1: "낮음", 2: "보통", 3: "높음"}.get
    res = {0: "양호", 1: "취약", 2: "수동"}.get
    rows: List[Dict] = []
    for it in js.get("result", []):
        rows.append(
            {
                "진단코드": it.get("itemcode", "N/A"),
                "중요도": imp(it.get("importance", 0)),
                "진단항목": it.get("title", "N/A"),
                "위험도": risk(it.get("importance", 0)),
                "결과": res(it.get("result", 0)),
                "조치방법": it.get("resultdetail", "N/A"),
                "PC명": os.path.splitext(fname)[0],
                "진단시점": js.get("testedtime", "Unknown"),
                "OS정보": js.get("osinfo", "Unknown"),
            }
        )
    return rows

# KPI 계산 ---------------------------------------------------------------------
@lru_cache(maxsize=None)
def _kpi(_: int, total: int, vuln: int, good: int, high: int):
    g_ratio = round(good / total * 100, 1) if total else 0.0
    v_ratio = round(vuln / total * 100, 1) if total else 0.0
    score = round(max(0, g_ratio - (high / total * 20) if total else 0), 1)
    return g_ratio, v_ratio, score

# CSS --------------------------------------------------------------------------
CSS = """
<style>
*{font-family:'Nanum Gothic',sans-serif;}
.page-title{display:flex;align-items:center;margin:20px 0 30px;border-bottom:2px solid #e0e0e0}
.page-icon{font-size:32px;margin-right:15px;color:#2196f3}
.page-title h1{margin:0;font-size:28px;color:#333;font-weight:bold}
.filter-section,.results-section,.actions-section{background:#fff;border:2px solid #2196f3;border-radius:8px;padding:20px;margin:20px 0}
.actions-section{background:#f8f9fa;border:none}
.table-scroll{max-height:500px;overflow-y:auto;width:100%;}
</style>
"""

# PDF -------------------------------------------------------------------------

def _generate_pdf(df: pd.DataFrame) -> bytes:
    vuln = (df["결과"] == "취약").sum()
    good = (df["결과"] == "양호").sum()
    high = (df["위험도"] == "높음").sum()
    txt = (
        "진단 결과 보고서\n"
        f"생성일시: {datetime.now():%Y-%m-%d %H:%M:%S}\n"
        f"총 항목: {len(df)}\n"
        f"취약: {vuln}  양호: {good}  고위험: {high}\n"
        "\n※ 상세 내용은 Excel 보고서를 참조하십시오."
    )
    return txt.encode("utf-8")

# Header ----------------------------------------------------------------------

def _header():
    st.markdown(CSS, unsafe_allow_html=True)
    st.markdown(
        '<div class="page-title"><span class="page-icon">📁</span><h1>3️⃣ 진단 결과 페이지</h1></div>',
        unsafe_allow_html=True,
    )

# Filter box ------------------------------------------------------------------

def _filter_box(df: pd.DataFrame) -> pd.DataFrame:
    st.markdown('<div class="filter-section">', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    imp = c1.selectbox("중요도", ["전체"] + sorted(df["중요도"].unique()))
    res = c2.selectbox("결과", ["전체"] + sorted(df["결과"].unique()))
    risk = c3.selectbox("위험도", ["전체"] + sorted(df["위험도"].unique()))
    pc = c4.selectbox("PC명", ["전체"] + sorted(df["PC명"].unique()))
    col5, col6, col7 = st.columns([2, 1, 1])
    s_col = col5.selectbox("정렬", ["진단코드", "중요도", "진단항목", "위험도", "결과"])
    s_ord = col6.selectbox("순서", ["오름차순", "내림차순"])
    if col7.button("🔄 초기화"):
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    out = df.copy()
    if imp != "전체":
        out = out[out["중요도"] == imp]
    if res != "전체":
        out = out[out["결과"] == res]
    if risk != "전체":
        out = out[out["위험도"] == risk]
    if pc != "전체":
        out = out[out["PC명"] == pc]
    out = out.sort_values(s_col, ascending=(s_ord == "오름차순"))
    return out.reset_index(drop=True)

# Styler → HTML ---------------------------------------------------------------

def _styled_html(df: pd.DataFrame) -> str:
    color_map_res = {"취약": "#ffebee;color:#c62828", "양호": "#e8f5e8;color:#2e7d32", "수동": "#fff3e0;color:#ef6c00"}
    color_map_risk = {"높음": "#ffebee;color:#c62828", "보통": "#fff3e0;color:#ef6c00", "낮음": "#e8f5e8;color:#2e7d32"}

    def row_style(row):
        styles = ["" for _ in row]
        if "결과" in row.index:
            styles[row.index.get_loc("결과")] = f"background-color:{color_map_res.get(row['결과'], '')};font-weight:bold"
        if "위험도" in row.index:
            styles[row.index.get_loc("위험도")] = f"background-color:{color_map_risk.get(row['위험도'], '')};font-weight:bold"
        return styles

    html = (
        df.style.apply(row_style, axis=1)
        .set_table_attributes('class="dataframe" style="border-collapse:collapse;width:100%"')
        .hide(axis="index")
        .to_html()
    )
    return html

# Results section -------------------------------------------------------------

def _results_section(df: pd.DataFrame):
    st.markdown('<div class="results-section">', unsafe_allow_html=True)
    if df.empty:
        st.info("조건에 맞는 데이터가 없습니다.")
        st.markdown("</div>", unsafe_allow_html=True); return
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("총 항목", len(df))
    c2.metric("취약", (df["결과"] == "취약").sum())
    c3.metric("양호", (df["결과"] == "양호").sum())
    c4.metric("고위험", (df["위험도"] == "높음").sum())
    st.markdown("---")
    html = _styled_html(df[["진단코드", "중요도", "진단항목", "위험도", "결과", "조치방법"]])
    st.markdown(f'<div class="table-scroll">{html}</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ---- Actions ----------------------------------------------------------------

def _actions(df: pd.DataFrame):
    st.markdown('<div class="actions-section">', unsafe_allow_html=True)
    col_pdf,col_xls = st.columns(2)
    if col_pdf.button('📄 PDF 내보내기', use_container_width=True):
        st.download_button('PDF 다운로드', _generate_pdf(df), file_name=f'report_{datetime.now():%Y%m%d_%H%M%S}.pdf', mime='application/pdf')
    if col_xls.button('📊 Excel 내보내기', use_container_width=True):
        st.info('보고서 생성 중…')
        try:
            _lazy_parsing_proc()()
            st.success('완료!')
        except Exception as e:
            st.error(f'오류: {e}')
    st.markdown('</div>', unsafe_allow_html=True)

# ---- Main -------------------------------------------------------------------

def show():
    _header()
    base = os.path.dirname(os.path.abspath(__file__))
    df = _load_df(os.path.join(base, '../result'))
    if df.empty:
        st.warning('데이터가 없습니다.'); return
    filtered = _filter_box(df)
    _results_section(filtered)
    _actions(filtered)

if __name__=='__main__':
    st.set_page_config(page_title='진단 결과', layout='wide')
    show()