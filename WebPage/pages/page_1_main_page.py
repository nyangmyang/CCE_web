"""page_4_dash_board.py – Security KPI Dashboard (stable build with inline comments)

* 2025‑06‑20 • 완전판 + 풍부한 한글 인라인 주석
* 주요 포인트
    1. Plotly는 지연 import 로 첫 로딩 속도 최적화
    2. JSON → DataFrame 변환 시 부서·카테고리까지 파생 필드 생성
    3. KPI 계산은 DataFrame 해시 기반 LRU 캐시로 중복 호출 방지
    4. 시각 요소(Gauge·Pie·Bar etc.)는 색상 접근성 고려한 팔레트 사용
    5. 게이지바 생성
"""
from __future__ import annotations

import os
import json
from datetime import datetime
from functools import lru_cache
from typing import List, Dict
from pathlib import Path

import pandas as pd
import streamlit as st

# ──────────────────────────────────────────────────────────────────────────────
# 글로벌 설정 - 대시보드 방식으로 통일
# ──────────────────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent
RESULT_DIR = (BASE_DIR / "../result").resolve()

# ──────────────────────────────────────────────────────────────────────────────
# 1) Plotly 모듈은 무거우므로 필요할 때만 import → 캐싱
# ──────────────────────────────────────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def _lazy_plotly():
    """Plotly 관련 모듈을 지연 import 하고, 게이지 생성 헬퍼를 반환."""
    import plotly.express as px
    import plotly.graph_objects as go

    def semicircle_gauge(vuln_ratio: float, total_items: int = 0) -> go.Figure:
        """취약점 비율을 기반으로 게이지를 생성
        Args:
            vuln_ratio: 취약 비율 (0-100)
            total_items: 전체 점검 항목 수
        """
        # 취약 항목 개수 계산
        vuln_count = int(vuln_ratio * total_items / 100) if total_items > 0 else 0


        fig = go.Figure(
            go.Indicator(
                mode="gauge+number",
                value=vuln_ratio,
                domain={"x": [0, 1], "y": [0, 1]},
                title = {
                'text': f"<b>취약점 현황</b><br><span style='font-size:14px;color:#666'>{vuln_count}개 항목 취약</span>",
                'font': {'size': 18}},
                number = {'suffix': "%"},
                gauge={
                    # 축 범위 설정
                    "axis": {"range": [0, 100],
                             'tickwidth': 1,
                             'tickcolor': "darkblue"},
                    # 현재 값 표시 색(값 범위에 따라 동적 변경)
                    "bar": {
                        "color": "#D0021B" if vuln_ratio > 66 else "#F5A623" if vuln_ratio > 33 else "#7ED321",
                    },
                    # 단계별 배경색 (rgba 로 투명도 적용)
                    "steps": [
                        {"range": [0, 33], "color": "rgba(126,211,33,0.3)"},   # low risk – green
                        {"range": [33, 66], "color": "rgba(245,166,35,0.3)"}, # medium – orange
                        {"range": [66, 100], "color": "rgba(208,2,27,0.3)"},  # high – red
                    ],
                     # 임계값 표시 (50% 위험선)
                    'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 50}
                },
            )
        )
        fig.update_layout(margin=dict(t=60, b=20, l=20, r=20),
            height=280,
            font={'color': "darkblue", 'family': "Arial"}
        )
        
        return fig

    return px, go, semicircle_gauge

# ──────────────────────────────────────────────────────────────────────────────
# 2) JSON 결과 로딩 & 전처리 (캐시) - 대시보드 방식으로 수정
# ──────────────────────────────────────────────────────────────────────────────
@st.cache_data(ttl=600, show_spinner=False)
def load_json_files() -> list[dict]:
    """result 폴더의 모든 JSON을 로드하여 리스트로 반환"""
    if not RESULT_DIR.exists():
        st.warning(f"⚠️ result 폴더가 없습니다: {RESULT_DIR}")
        return []

    json_paths = list(RESULT_DIR.glob("*.json"))
    if not json_paths:
        st.warning("⚠️ result 폴더에 JSON 파일이 없습니다.")
        return []

    data = []
    for path in json_paths:
        try:
            data.append(json.loads(path.read_text(encoding="utf-8")))
        except json.JSONDecodeError as err:
            st.error(f"❌ {path.name} 파싱 오류: {err}")
    return data

# 매핑 테이블
RESULT_MAP = {0: "양호", 1: "취약", 2: "해당없음"}
IMPORTANCE_MAP = {1: "낮음", 2: "보통", 3: "높음"}

def preprocess() -> pd.DataFrame:
    """JSON 리스트를 DataFrame 으로 변환"""
    raw_json = load_json_files()
    if not raw_json:
        return pd.DataFrame()

    records: list[dict] = []
    for blob in raw_json:
        target_ip = blob.get("targetip", "Unknown")
        tested_time = blob.get("testedtime", "Unknown")
        os_info = blob.get("osinfo", "Unknown")

        for item in blob.get("result", []):
            records.append(
                {
                    "PC명": f"PC-{target_ip.split('.')[-1]}" if target_ip != "Unknown" else "PC-Unknown",
                    "점검항목": item.get("title", "N/A"),
                    "진단시점": parse_time(tested_time),
                    "확인결과": RESULT_MAP.get(item.get("result"), "알수없음"),
                    "위험도": IMPORTANCE_MAP.get(item.get("importance"), "알수없음"),
                    "조치방법": item.get("resultdetail", "N/A"),
                    "카테고리": classify(item.get("title", "")),
                    "부서": department_from_ip(target_ip),
                    "OS": os_info,
                    # 원본
                    "진단코드": item.get("itemcode", "N/A"),
                    "중요도_원본": item.get("importance", 0),
                    "점검결과_원본": item.get("result", 0),
                }
            )

    df = pd.DataFrame.from_records(records)
    if not df.empty:
        st.toast(f"✅ {len(df)}개 항목 로드 완료", icon="✅")
    return df

# 헬퍼 함수들
def parse_time(ts: str) -> datetime:
    try:
        return datetime.strptime(ts, "%Y-%m-%d %H:%M:%S") if ts != "Unknown" else datetime.now()
    except ValueError:
        return datetime.now()

def classify(title: str) -> str:
    """keyword 매핑으로 카테고리 라벨 반환"""
    title = title.lower()
    rules = {
        "패스워드 정책": ["password", "passwd", "패스워드", "암호"],
        "계정 관리": ["account", "계정", "user"],
        "서비스 관리": ["service", "서비스", "daemon"],
        "네트워크 보안": ["network", "네트워크", "port"],
        "파일 시스템": ["file", "파일", "directory"],
        "로그 관리": ["log", "로그", "audit"],
    }
    for label, keys in rules.items():
        if any(k in title for k in keys):
            return label
    return "기타 보안"

def department_from_ip(ip: str) -> str:
    if ip == "Unknown":
        return "알수없음"
    try:
        octet = int(ip.split(".")[-1])
        if octet <= 50:
            return "개발팀"
        if octet <= 100:
            return "운영팀"
        if octet <= 150:
            return "보안팀"
        return "관리팀"
    except ValueError:
        return "기타"

# ──────────────────────────────────────────────────────────────────────────────
# 3) KPI 계산
# ──────────────────────────────────────────────────────────────────────────────
def calc_kpi(df: pd.DataFrame) -> dict:
    total = len(df)
    if not total:
        return dict.fromkeys(
            ["total", "good_ratio", "vuln_ratio", "high_risk", "score"], 0
        )

    good = (df["확인결과"] == "양호").sum()
    vuln = (df["확인결과"] == "취약").sum()
    high = ((df["위험도"] == "높음") & (df["확인결과"] == "취약")).sum()

    good_ratio = round(good / total * 100, 1)
    vuln_ratio = round(vuln / total * 100, 1)
    penalty = high / total * 20
    score = round(max(0, good_ratio - penalty), 1)

    return {
        "total": total,
        "good_ratio": good_ratio,
        "vuln_ratio": vuln_ratio,
        "high_risk": high,
        "score": score,
    }

# ──────────────────────────────────────────────────────────────────────────────
# 4) UI – CSS & 작은 컴포넌트들
# ──────────────────────────────────────────────────────────────────────────────
_CSS = """
<style>
.kpi-card{background:var(--bg);padding:18px;border-radius:10px;border-left:4px solid var(--line);box-shadow:0 1px 3px rgb(0 0 0/.1);text-align:center;margin:4px}
.kpi-card h4{margin:0;font-size:13px;color:#555}
.kpi-card h1{margin:8px 0;font-size:28px;color:var(--line)}
.kpi-card p{margin:0;font-size:11px;color:#777}
.icon-box{padding:8px 0;text-align:center;border-bottom:3px solid transparent}
.icon-box:hover{background:#f5f7fb;border-bottom-color:#3d7eff;cursor:pointer}
</style>
"""

COLOR = {
    "primary": "#4A90E2",
    "good": "#7ED321",
    "warning": "#F5A623",
    "danger": "#D0021B",
    "info": "#9013FE",
    "muted": "#9B9B9B",
}



def kpi_card(label: str, value, unit: str, color: str):
    st.markdown(
        f"""
        <div style='background:linear-gradient(135deg,{color}15,{color}25);padding:18px;border-radius:10px;border-left:4px solid {color};text-align:center;'>
            <h4 style='margin:0;font-size:14px;color:#333'>{label}</h4>
            <h1 style='margin:8px 0;font-size:32px;color:{color};font-weight:700'>{value}</h1>
            <p style='margin:0;font-size:12px;color:#666'>{unit}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

def _top_vulnerable(df: pd.DataFrame) -> None:
    """PC 별 취약건수 Top 5 테이블."""
    vuln = df[df["확인결과"] == "취약"]
    if vuln.empty:
        st.success("🎉 취약한 항목이 없습니다!")
        return
    tbl = (
        vuln.groupby("PC명").size()
        .sort_values(ascending=False)
        .head(5)
        .reset_index(name="취약건수")
    )
    st.table(tbl)
# ──────────────────────────────────────────────────────────────────────────────
# 6) 취약점 대시보드 함수 _ 페이지 중간 부분 / 진행 중인 서버 && 취약점 바 그래프 
# ──────────────────────────────────────────────────────────────────────────────
#서버별 위험도별 취약점 추이 차트 _서버별로 다른 색상
def create_server_list(df: pd.DataFrame) -> None:
    """왼쪽 서버 리스트 UI - Most vulnerable computers"""
    
    st.markdown("### 📊 Most vulnerable computers")
    
    # 서버별 취약률 계산
    server_stats = []
    for pc_name in df["PC명"].unique():
        server_data = df[df["PC명"] == pc_name]
        total = len(server_data)
        vuln_count = (server_data["확인결과"] == "취약").sum()
        vuln_ratio = (vuln_count / total * 100) if total > 0 else 0
        
        server_stats.append({
            'server': pc_name,
            'vuln_ratio': vuln_ratio,
            'vuln_count': vuln_count,
            'total': total
        })
    
    # 취약률 높은 순으로 정렬 (Top 5)
    server_stats.sort(key=lambda x: x['vuln_ratio'], reverse=True)
    top_servers = server_stats[:5]
    
    # 서버 리스트 표시
    for i, server in enumerate(top_servers):
        # 위험도에 따른 색상 결정
        if server['vuln_ratio'] >= 60:
            color = "#D0021B"  # 빨강
            icon = "🔴"
        elif server['vuln_ratio'] >= 40:
            color = "#F5A623"  # 주황
            icon = "🟡"
        else:
            color = "#7ED321"  # 초록
            icon = "🟢"
        
        # 서버 카드 스타일
        st.markdown(f"""
        <div style='display:flex;align-items:center;padding:10px;margin:5px 0;
                    background:white;border-radius:8px;border-left:4px solid {color};
                    box-shadow:0 2px 4px rgba(0,0,0,0.1)'>
            <div style='margin-right:10px;font-size:20px'>{icon}</div>
            <div style='flex:1'>
                <div style='font-weight:bold;font-size:14px;color:#333'>{server['server']}</div>
                <div style='font-size:12px;color:#666'>{server['vuln_count']}/{server['total']} 취약</div>
            </div>
            <div style='font-weight:bold;font-size:16px;color:{color}'>
                {server['vuln_ratio']:.1f}%
            </div>
        </div>
        """, unsafe_allow_html=True)

def create_server_focused_trend_chart(df: pd.DataFrame):
    """
    서버별로 구분된 취약점 추이 차트 - 조원용 상세 주석 버전
    
    📊 차트 설명:
    - X축: 날짜 (각 서버마다 다른 날짜로 분산)
    - Y축: 취약점 수 (0~36개)
    - 색상: 서버별로 다른 색상 (빨강, 파랑, 초록, 보라 등)
    - 선 스타일: 위험도별 구분
      * 실선(—): High 위험도 (두께 3)
      * 점선(- -): Medium 위험도 (두께 2) 
      * 점점선(···): Low 위험도 (두께 1)
    
    💡 사용 목적:
    - 각 서버별로 High/Medium/Low 위험도 취약점이 얼마나 있는지 한눈에 파악
    - 어떤 서버가 어떤 위험도에서 문제가 많은지 비교 분석
    
    Args:
        df (pd.DataFrame): 전체 보안 점검 데이터 
                          (PC명, 확인결과, 위험도, 진단시점 등 포함)
    
    Returns:
        go.Figure: Plotly 그래프 객체
    """
    
    # Plotly 모듈 가져오기
    px, go, _ = _lazy_plotly()
    
    # 📋 1단계: 서버 목록 추출 및 기준 날짜 설정
    servers = df['PC명'].unique()
    
    # 실제 데이터의 진단시점을 기준 날짜로 사용
    if not df.empty and '진단시점' in df.columns:
        base_date = df['진단시점'].iloc[0].date()
    else:
        # 데이터가 없으면 오늘 날짜 사용
        base_date = pd.Timestamp.now().date()
    
    # 🔍 데이터 부족시 샘플 데이터 생성 (조원들 시연용)
    if len(servers) < 2:
        st.warning("⚠️ 실제 서버 데이터가 부족하여 샘플 데이터로 차트를 표시합니다.")
        return create_sample_server_focused_chart()
    
    # 📊 2단계: 각 서버별 취약점 데이터 계산
    trend_data = []
    
    for i, server in enumerate(servers):
        # 해당 서버의 데이터만 필터링
        server_data = df[df['PC명'] == server]
        
        # 시각화를 위해 각 서버마다 다른 날짜 할당 (2일 간격)
        # 예: 첫 번째 서버는 base_date, 두 번째는 base_date+2일, 세 번째는 base_date+4일...
        server_date = base_date + pd.Timedelta(days=i*2)
        
        # 🎯 핵심 계산: 위험도별 취약점 수 집계
        # 전체 취약점 수 (확인결과가 '취약'인 것들)
        total_vuln = (server_data["확인결과"] == "취약").sum()
        
        # 고위험 취약점 수 (위험도가 '높음'이면서 확인결과가 '취약')
        high_vuln = ((server_data["위험도"] == "높음") & (server_data["확인결과"] == "취약")).sum()
        
        # 중위험 취약점 수 (위험도가 '보통'이면서 확인결과가 '취약')
        medium_vuln = ((server_data["위험도"] == "보통") & (server_data["확인결과"] == "취약")).sum()
        
        # 저위험 취약점 수 (위험도가 '낮음'이면서 확인결과가 '취약')
        low_vuln = ((server_data["위험도"] == "낮음") & (server_data["확인결과"] == "취약")).sum()
        
        # 계산 결과를 딕셔너리로 저장
        trend_data.append({
            'Date': server_date,      # 해당 서버의 할당된 날짜
            'Total': total_vuln,      # 전체 취약점 수
            'High': high_vuln,        # 고위험 취약점 수
            'Medium': medium_vuln,    # 중위험 취약점 수
            'Low': low_vuln,          # 저위험 취약점 수
            'Server': server          # 서버명
        })
    
    # 리스트를 DataFrame으로 변환 (차트 생성을 위해)
    trend_df = pd.DataFrame(trend_data)
    
    # 🎨 3단계: 차트 생성 시작
    fig = go.Figure()
    
    # 서버별로 다른 색상 할당 (최대 10개 서버까지 지원)
    # Set1 색상 팔레트: 빨강, 파랑, 초록, 보라, 주황, 노랑, 분홍, 회색, 올리브, 하늘색
    server_colors = px.colors.qualitative.Set1[:len(servers)]
    
    # 📈 4단계: 각 서버별로 3개 선(High/Medium/Low) 추가
    for i, server in enumerate(servers):
        # 해당 서버의 데이터만 추출
        server_data = trend_df[trend_df['Server'] == server]
        
        # 🔴 High 위험도 선 추가 (실선, 굵게)
        fig.add_trace(go.Scatter(
            x=server_data['Date'],           # X축: 날짜
            y=server_data['High'],           # Y축: 고위험 취약점 수
            mode='lines+markers',            # 선과 마커 모두 표시
            name=f'{server} (High)',         # 범례에 표시될 이름
            line=dict(
                color=server_colors[i],      # 서버별 고유 색상
                width=3,                     # 선 두께 (가장 굵게)
                dash='solid'                 # 실선 (——————)
            ),
            marker=dict(size=8),             # 마커 크기 (가장 크게)
            hovertemplate=f'<b>{server}</b><br>' +  # 마우스 올릴 때 표시 정보
                         'Date: %{x}<br>' +
                         'High Risk: %{y}개<extra></extra>'
        ))
        
        # 🟡 Medium 위험도 선 추가 (점선, 중간 굵기)
        fig.add_trace(go.Scatter(
            x=server_data['Date'],           # X축: 날짜  
            y=server_data['Medium'],         # Y축: 중위험 취약점 수
            mode='lines+markers',            # 선과 마커 모두 표시
            name=f'{server} (Medium)',       # 범례에 표시될 이름
            line=dict(
                color=server_colors[i],      # 서버별 고유 색상 (High와 같은 색)
                width=2,                     # 선 두께 (중간)
                dash='dash'                  # 점선 (— — — —)
            ),
            marker=dict(size=6),             # 마커 크기 (중간)
            hovertemplate=f'<b>{server}</b><br>' +  # 마우스 올릴 때 표시 정보
                         'Date: %{x}<br>' +
                         'Medium Risk: %{y}개<extra></extra>'
        ))
        
        # 🟢 Low 위험도 선 추가 (점점선, 얇게)
        fig.add_trace(go.Scatter(
            x=server_data['Date'],           # X축: 날짜
            y=server_data['Low'],            # Y축: 저위험 취약점 수
            mode='lines+markers',            # 선과 마커 모두 표시
            name=f'{server} (Low)',          # 범례에 표시될 이름
            line=dict(
                color=server_colors[i],      # 서버별 고유 색상 (High, Medium과 같은 색)
                width=1,                     # 선 두께 (가장 얇게)
                dash='dot'                   # 점점선 (· · · ·)
            ),
            marker=dict(size=4),             # 마커 크기 (가장 작게)
            hovertemplate=f'<b>{server}</b><br>' +  # 마우스 올릴 때 표시 정보
                         'Date: %{x}<br>' +
                         'Low Risk: %{y}개<extra></extra>'
        ))
    
    # 🎨 5단계: 차트 레이아웃 및 스타일 설정
    fig.update_layout(
        title={
            'text': 'Server Vulnerability Trends by Risk Level',
            'x': 0.5,                        # 제목 가운데 정렬
            'font': {'size': 16}             # 제목 크기
        },
        xaxis_title='Date',                  # X축 제목
        yaxis_title='Vulnerability Count (0-36)',  # Y축 제목
        height=400,                          # 차트 높이
        
        # 📋 범례 설정 (오른쪽에 세로로 배치)
        legend=dict(
            orientation="v",                 # 세로 방향
            yanchor="top",                   # 위쪽 기준
            y=1,                            # 맨 위에 배치
            xanchor="left",                 # 왼쪽 기준  
            x=1.02,                         # 차트 오른쪽 바깥에 배치
            bgcolor="rgba(255,255,255,0.8)", # 반투명 배경
            bordercolor="gray",             # 테두리 색상
            borderwidth=1                   # 테두리 두께
        ),
        
        # 📏 여백 설정 (범례 공간 확보)
        margin=dict(r=150),                 # 오른쪽 여백 150px
        
        # 🎯 그리드 설정
        xaxis=dict(showgrid=True, gridcolor='lightgray'),
        yaxis=dict(showgrid=True, gridcolor='lightgray'),
        
        # 🖱️ 인터랙션 설정
        hovermode='x unified'               # 같은 X축 값에서 모든 정보 표시
    )
    
    return fig

def create_sample_server_focused_chart():
    """
    샘플 데이터로 서버별 트렌드 차트 생성 (실제 데이터 부족시 사용)
    
    💡 용도: 조원들에게 차트 형태를 보여주기 위한 데모용
    """
    
    px, go, _ = _lazy_plotly()
    
    # 📋 샘플 서버 데이터 정의
    sample_data = [
        {
            'Date': pd.Timestamp('2025-06-15').date(),
            'Server': 'PC-192.168.1.10',
            'High': 18,      # 고위험 취약점 18개 (심각한 서버)
            'Medium': 3,     # 중위험 취약점 3개
            'Low': 0         # 저위험 취약점 0개
        },
        {
            'Date': pd.Timestamp('2025-06-17').date(),
            'Server': 'PC-192.168.1.25', 
            'High': 12,      # 고위험 취약점 12개 (중간 위험 서버)
            'Medium': 4,     # 중위험 취약점 4개
            'Low': 2         # 저위험 취약점 2개
        },
        {
            'Date': pd.Timestamp('2025-06-19').date(),
            'Server': 'PC-192.168.1.55',
            'High': 6,       # 고위험 취약점 6개 (양호한 서버)
            'Medium': 6,     # 중위험 취약점 6개  
            'Low': 3         # 저위험 취약점 3개
        },
        {
            'Date': pd.Timestamp('2025-06-21').date(),
            'Server': 'PC-192.168.1.88',
            'High': 2,       # 고위험 취약점 2개 (매우 안전한 서버)
            'Medium': 3,     # 중위험 취약점 3개
            'Low': 2         # 저위험 취약점 2개
        }
    ]
    
    # DataFrame 생성
    trend_df = pd.DataFrame(sample_data)
    
    # 차트 생성 (위의 로직과 동일)
    fig = go.Figure()
    
    servers = trend_df['Server'].unique()
    server_colors = px.colors.qualitative.Set1[:len(servers)]
    
    for i, server in enumerate(servers):
        server_data = trend_df[trend_df['Server'] == server]
        
        # High, Medium, Low 선 추가 (동일한 로직)
        for risk_level, line_style in [
            ('High', {'width': 3, 'dash': 'solid', 'marker_size': 8}),
            ('Medium', {'width': 2, 'dash': 'dash', 'marker_size': 6}),
            ('Low', {'width': 1, 'dash': 'dot', 'marker_size': 4})
        ]:
            fig.add_trace(go.Scatter(
                x=server_data['Date'],
                y=server_data[risk_level],
                mode='lines+markers',
                name=f'{server} ({risk_level})',
                line=dict(
                    color=server_colors[i],
                    width=line_style['width'],
                    dash=line_style['dash']
                ),
                marker=dict(size=line_style['marker_size'])
            ))
    
    # 레이아웃 설정 (동일)
    fig.update_layout(
        title='Sample: Server Vulnerability Trends by Risk Level',
        xaxis_title='Date',
        yaxis_title='Vulnerability Count (0-36)', 
        height=400,
        legend=dict(orientation="v", yanchor="top", y=1, xanchor="left", x=1.02),
        margin=dict(r=150)
    )
    
    return fig






# ──────────────────────────────────────────────────────────────────────────────
# 5) Main 엔트리 – Streamlit 페이지
# ──────────────────────────────────────────────────────────────────────────────

def show():
    """app.py 라우팅에서 호출되는 메인 함수."""
    st.markdown(_CSS, unsafe_allow_html=True)
    
    st.markdown("---")

    # 데이터 로딩 - 대시보드 방식으로 수정 ----------------------------------------
    df = preprocess()
    if df.empty:
        st.error("📊 표시할 데이터가 없습니다. JSON 파일을 확인해주세요.")
        # 샘플 대시보드 표시
        
        return

    # KPI 계산 --------------------------------------------------------------------
    metrics = calc_kpi(df)
    
    # Plotly 객체 지연 import -------------------------------------------------------
    px, go, gauge_fn = _lazy_plotly()

    # ── 상단 배너 ---------------------------------------------------------------
    st.subheader(f"Entire Network – {metrics['total']} Computers")
    col_gauge, col_stats = st.columns([2, 4])

    with col_gauge:
        st.markdown("##### Vulnerability Level")
        st.plotly_chart(gauge_fn(metrics['vuln_ratio']), use_container_width=True)

    with col_stats:
        st.markdown("##### Quick Stats")
        for lbl, cnt in {
            "Vulnerabilities": metrics['total'] - (df["확인결과"] == "양호").sum(),
            "High Risk": metrics['high_risk'],
            "Good": (df["확인결과"] == "양호").sum(),
        }.items():
            pct = cnt / metrics['total'] * 100 if metrics['total'] else 0
            st.progress(pct / 100, text=f"{lbl}: {cnt} devices ({pct:.1f}%)")

    # ── 🎯  취약점 대시보드 섹션 추가 ──────────────────────────────────────
    st.markdown("---")
    st.markdown("### 🔍 상세 취약점 분석")
    
    # 2열 레이아웃: 왼쪽(서버 리스트) + 오른쪽(트렌드 차트)
    col_servers, col_trend = st.columns([1, 2])
    
    with col_servers:
        create_server_list(df)
    
    with col_trend:
        trend_fig = create_server_focused_trend_chart(df)  
        st.plotly_chart(trend_fig, use_container_width=True)

    # ── 서버별 상세 현황 (기존 코드 유지) ─────────────────────────────────────────
    if st.checkbox("🔍 서버별 상세 현황 보기"):
        st.markdown("### 📊 서버별 상세 현황")
        
        if 'server_details' in metrics and metrics['server_details']:
            server_df = pd.DataFrame(metrics['server_details'])
            server_df = server_df.rename(columns={
                'pc_name': 'PC명',
                'total': '총 항목',
                'vuln_count': '취약 항목', 
                'good_count': '양호 항목',
                'vuln_ratio': '취약률(%)',
                'good_ratio': '양호율(%)'
            })
            
            server_df = server_df.sort_values('취약률(%)', ascending=False)
            
            st.dataframe(
                server_df[['PC명', '총 항목', '취약 항목', '양호 항목', '취약률(%)', '양호율(%)']],
                use_container_width=True,
                hide_index=True
            )


    
    

    
    

if __name__ == "__main__":
    show()