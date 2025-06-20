#figma image 3
#중간점검 페이지
import streamlit as st
import pandas as pd
import os
import json
from datetime import datetime

def show():
    """app.py에서 호출하는 메인 함수"""
    # 커스텀 CSS 적용
    apply_custom_css()
    
    # 페이지 헤더
    show_page_header()
    
    # 메인 레이아웃 (좌측 메뉴 + 우측 테이블)
    create_main_layout()
    
    # 하단 점수 + 다운로드 섹션
    show_bottom_section()

def main():
    """독립 실행용 메인 페이지 함수"""
    st.set_page_config(page_title="중간 점검", layout="wide")
    show()

def apply_custom_css():
    """피그마 디자인 기반 커스텀 CSS"""
    st.markdown("""
    <style>
    * {font-family: 'Nanum Gothic', sans-serif;}
    
    .page-header {
        background-color: #f0f0f0;
        padding: 15px 25px;
        border-radius: 8px;
        margin-bottom: 25px;
        border-bottom: 3px solid #000;
    }
    
    .menu-container {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 15px;
        border: 1px solid #dee2e6;
    }
    
    .menu-item {
        display: flex;
        align-items: center;
        padding: 12px 15px;
        margin: 5px 0;
        background-color: white;
        border: 1px solid #e9ecef;
        border-radius: 6px;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .menu-item:hover {
        background-color: #e3f2fd;
        border-color: #2196f3;
    }
    
    .menu-item.active {
        background-color: #2196f3;
        color: white;
        border-color: #1976d2;
    }
    
    .table-container {
        background-color: white;
        border: 2px solid #2196f3;
        border-radius: 8px;
        padding: 20px;
        margin-left: 10px;
    }
    
    .score-card {
        background: linear-gradient(135deg, #e3f2fd, #bbdefb);
        border: 2px solid #2196f3;
        border-radius: 12px;
        padding: 25px;
        text-align: center;
        margin: 20px 0;
    }
    
    .download-section {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 20px;
        margin-top: 20px;
    }
    
    .stButton button {
        width: 100%;
        margin: 5px 0;
        border-radius: 6px;
        transition: all 0.3s ease;
    }
    
    .category-icon {
        font-size: 20px;
        margin-right: 10px;
        width: 30px;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

def show_page_header():
    """페이지 상단 헤더"""
    st.markdown('<div class="page-header">', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # 탭 스타일 제목
        st.markdown("### 📋 점검 결과 &nbsp;&nbsp;&nbsp; 📊 전체 요약")
        
    with col2:
        # 서버 선택 박스
        show_server_selection()
    
    st.markdown('</div>', unsafe_allow_html=True)

def show_server_selection():
    """서버 선택 드롭다운 (피그마 스타일)"""
    # JSON 데이터에서 서버 목록 가져오기
    available_servers = get_available_servers()
    
    # 선택박스 스타일링
    st.markdown("**서버:**")
    selected_server = st.selectbox(
        "서버 선택",
        available_servers,
        key="inspection_server_select",
        label_visibility="collapsed"
    )
    
    # 세션 상태에 저장
    st.session_state.selected_inspection_server = selected_server
    return selected_server

def get_available_servers():
    """JSON 데이터에서 사용 가능한 서버 목록 추출"""
    try:
        data = load_json_data()
        if not data.empty and 'OS정보' in data.columns:
            servers = data['OS정보'].unique().tolist()
            servers = [s for s in servers if s != 'Unknown']
            return servers if servers else ["Ubuntu (sample)"]
        else:
            return ["Ubuntu (sample)", "CentOS (sample)", "Windows Server (sample)"]
    except:
        return ["Ubuntu (sample)"]

def create_main_layout():
    """메인 레이아웃: 좌측 메뉴 + 우측 테이블"""
    col_menu, col_table = st.columns([1, 3])
    
    with col_menu:
        # 좌측 카테고리 메뉴
        selected_category = show_category_menu()
    
    with col_table:
        # 우측 상세 테이블
        selected_item = show_category_table(selected_category)
    
    return selected_category, selected_item

def show_category_menu():
    """좌측 카테고리 메뉴 (피그마 아이콘 스타일)"""
    st.markdown('<div class="menu-container">', unsafe_allow_html=True)
    st.markdown("### 📋 점검 항목")
    
    # 카테고리 정의 (피그마 기준)
    categories = [
        {"name": "취약점 분석 현황", "icon": "🛡️", "color": "#e53e3e"},
        {"name": "설치프로그램 분석", "icon": "📦", "color": "#3182ce"},
        {"name": "윈도우 업데이트 현황", "icon": "🔄", "color": "#38a169"},
        {"name": "실행중인 서비스 현황", "icon": "⚙️", "color": "#805ad5"},
        {"name": "USB 사용 내역", "icon": "🔌", "color": "#d69e2e"},
        {"name": "이벤트 로그 분석", "icon": "📊", "color": "#dd6b20"}
    ]
    
    # 세션 상태 초기화
    if 'selected_category' not in st.session_state:
        st.session_state.selected_category = categories[0]["name"]
    
    selected_category = st.session_state.selected_category
    
    # 카테고리 버튼들
    for category in categories:
        # 활성/비활성 스타일
        is_active = (category["name"] == selected_category)
        button_style = "primary" if is_active else "secondary"
        
        # 아이콘과 함께 버튼 표시
        button_text = f"{category['icon']} {category['name']}"
        
        if st.button(
            button_text, 
            key=f"cat_{category['name']}", 
            use_container_width=True,
            type=button_style
        ):
            st.session_state.selected_category = category["name"]
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    return st.session_state.selected_category

def show_category_table(selected_category):
    """선택된 카테고리의 상세 테이블"""
    st.markdown('<div class="table-container">', unsafe_allow_html=True)
    
    # 테이블 헤더
    col_title, col_stats = st.columns([2, 1])
    
    with col_title:
        st.markdown(f"### 📊 {selected_category}")
    
    # 데이터 로드 및 필터링
    data = load_json_data()
    
    if data.empty:
        st.warning("⚠️ 표시할 데이터가 없습니다.")
        st.markdown('</div>', unsafe_allow_html=True)
        return None
    
    # 카테고리로 필터링
    filtered_data = filter_data_by_category(data, selected_category)
    
    with col_stats:
        if not filtered_data.empty:
            total_items = len(filtered_data)
            vulnerable_items = len(filtered_data[filtered_data['확인결과'] == '취약'])
            st.metric("총 항목", f"{total_items}개")
            st.metric("취약 항목", f"{vulnerable_items}개", 
                     delta=f"{vulnerable_items/total_items*100:.1f}%" if total_items > 0 else "0%")
    
    if filtered_data.empty:
        st.info(f"📋 {selected_category}에 해당하는 데이터가 없습니다.")
        st.markdown('</div>', unsafe_allow_html=True)
        return None
    
    # 필터 옵션
    show_table_filters(filtered_data)
    
    # 테이블 표시
    selected_item = display_inspection_table(filtered_data, selected_category)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    return selected_item

def filter_data_by_category(data, category):
    """카테고리별 데이터 필터링"""
    if '카테고리' in data.columns:
        return data[data['카테고리'] == category].copy()
    else:
        # 카테고리 컬럼이 없으면 제목으로 추정
        return classify_by_title(data, category)

def classify_by_title(data, target_category):
    """제목 기반으로 카테고리 분류"""
    if '점검항목' not in data.columns:
        return pd.DataFrame()
    
    filtered_items = []
    
    for _, row in data.iterrows():
        title = str(row.get('점검항목', '')).lower()
        category = classify_item_category(title)
        
        if category == target_category:
            filtered_items.append(row)
    
    return pd.DataFrame(filtered_items) if filtered_items else pd.DataFrame()

def classify_item_category(title):
    """제목 기반 카테고리 분류"""
    title_lower = title.lower()
    
    if any(keyword in title_lower for keyword in ['프로그램', '소프트웨어', 'software', 'program']):
        return '설치프로그램 분석'
    elif any(keyword in title_lower for keyword in ['업데이트', '패치', 'update', 'patch']):
        return '윈도우 업데이트 현황'
    elif any(keyword in title_lower for keyword in ['서비스', '데몬', 'service', 'daemon']):
        return '실행중인 서비스 현황'
    elif any(keyword in title_lower for keyword in ['usb', '외부', '이동식']):
        return 'USB 사용 내역'
    elif any(keyword in title_lower for keyword in ['로그', '감사', 'log', 'audit', 'event']):
        return '이벤트 로그 분석'
    else:
        return '취약점 분석 현황'

def show_table_filters(data):
    """테이블 필터링 옵션"""
    with st.expander("🔍 필터 옵션", expanded=False):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if 'PC명' in data.columns:
                pc_options = ["전체"] + sorted(data['PC명'].unique().tolist())
                pc_filter = st.selectbox("PC명", pc_options, key="pc_filter")
            else:
                pc_filter = "전체"
        
        with col2:
            if '확인결과' in data.columns:
                status_options = ["전체"] + sorted(data['확인결과'].unique().tolist())
                status_filter = st.selectbox("확인결과", status_options, key="status_filter")
            else:
                status_filter = "전체"
        
        with col3:
            if '위험도' in data.columns:
                risk_options = ["전체"] + sorted(data['위험도'].unique().tolist())
                risk_filter = st.selectbox("위험도", risk_options, key="risk_filter")
            else:
                risk_filter = "전체"
    
    return pc_filter, status_filter, risk_filter

def display_inspection_table(data, category):
    """점검 테이블 표시 (피그마 스타일)"""
    # 표시할 컬럼 정의
    display_columns = ['PC명', '점검항목', '확인결과', '위험도', '조치방법']
    
    # 사용 가능한 컬럼만 선택
    available_columns = [col for col in display_columns if col in data.columns]
    
    if not available_columns:
        st.error("표시할 수 있는 컬럼이 없습니다.")
        return None
    
    display_data = data[available_columns].copy()
    
    # 결과에 따른 색상 표시를 위한 스타일링
    def style_result(val):
        if val == '취약':
            return 'background-color: #ffebee; color: #c62828'
        elif val == '양호':
            return 'background-color: #e8f5e8; color: #2e7d32'
        return ''
    
    # 항목 수가 많으면 페이지네이션
    if len(display_data) > 10:
        # 페이지 선택
        page_size = 10
        total_pages = (len(display_data) - 1) // page_size + 1
        
        col_page1, col_page2, col_page3 = st.columns([1, 2, 1])
        with col_page2:
            current_page = st.selectbox(
                f"페이지 선택 (총 {total_pages}페이지)", 
                range(1, total_pages + 1),
                key=f"page_{category}"
            )
        
        # 현재 페이지 데이터
        start_idx = (current_page - 1) * page_size
        end_idx = start_idx + page_size
        page_data = display_data.iloc[start_idx:end_idx]
    else:
        page_data = display_data
    
    # 테이블 표시
    if not page_data.empty:
        # 행 선택을 위한 라디오 버튼
        if len(page_data) > 1:
            row_options = [f"{i+1}. {row.get('PC명', 'N/A')} - {str(row.get('점검항목', 'N/A'))[:40]}..." 
                          for i, (_, row) in enumerate(page_data.iterrows())]
            
            selected_row_idx = st.radio(
                "📋 상세 정보를 볼 항목을 선택하세요:",
                range(len(row_options)),
                format_func=lambda x: row_options[x],
                key=f"row_select_{category}"
            )
        else:
            selected_row_idx = 0
        
        # 선택된 행 강조
        st.markdown("**📊 점검 항목 목록:**")
        st.dataframe(
            page_data.style.applymap(style_result, subset=['확인결과'] if '확인결과' in page_data.columns else []),
            use_container_width=True,
            hide_index=True
        )
        
        # 선택된 항목 반환
        if selected_row_idx is not None and selected_row_idx < len(page_data):
            selected_item = page_data.iloc[selected_row_idx]
            
            # 조치 버튼
            col_btn1, col_btn2, col_btn3 = st.columns([2, 1, 1])
            with col_btn3:
                if st.button("🔧 조치방법", key=f"action_{category}", type="primary"):
                    show_action_guide(selected_item)
            
            return selected_item
    
    return None

def show_action_guide(item):
    """선택된 항목의 조치방법 표시"""
    st.markdown("---")
    st.markdown("### 🔧 조치방법 안내")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("**항목 정보:**")
        st.write(f"**PC명:** {item.get('PC명', 'N/A')}")
        st.write(f"**확인결과:** {item.get('확인결과', 'N/A')}")
        st.write(f"**위험도:** {item.get('위험도', 'N/A')}")
    
    with col2:
        st.markdown("**조치방법:**")
        action_method = item.get('조치방법', '조치방법이 제공되지 않았습니다.')
        st.info(action_method)
        
        # 조치 완료 버튼
        if st.button("✅ 조치 완료", key="action_complete"):
            st.success("조치가 완료되었습니다!")

def show_bottom_section():
    """하단 점수 + 다운로드 섹션"""
    col_score, col_download = st.columns([1, 2])
    
    with col_score:
        show_security_score_card()
    
    with col_download:
        show_download_buttons()

def show_security_score_card():
    """취약점 분석 점수 카드 (피그마 87.50 스타일)"""
    st.markdown('<div class="score-card">', unsafe_allow_html=True)
    
    # 동적 점수 계산
    score = calculate_security_score()
    
    st.markdown("### 🏆 취약점 분석 점수")
    st.markdown(f"""
    <div style="text-align: center; margin: 20px 0;">
        <h1 style="color: #1976d2; font-size: 48px; margin: 0;">{score}</h1>
        <h3 style="color: #666; margin: 0;">점</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # 점수별 상태 메시지
    if score >= 90:
        st.success("🟢 우수한 보안 상태")
    elif score >= 70:
        st.warning("🟡 보통 수준")
    else:
        st.error("🔴 개선 필요")
    
    st.markdown('</div>', unsafe_allow_html=True)

def calculate_security_score():
    """동적 보안 점수 계산"""
    data = load_json_data()
    
    if data.empty:
        return 87.5  # 샘플 점수
    
    total_items = len(data)
    if total_items == 0:
        return 0.0
    
    # 양호 항목 비율
    good_items = len(data[data['확인결과'] == '양호']) if '확인결과' in data.columns else 0
    base_score = (good_items / total_items) * 100
    
    # 고위험 항목 페널티
    high_risk_items = 0
    if '위험도' in data.columns and '확인결과' in data.columns:
        high_risk_items = len(data[(data['위험도'] == '높음') & (data['확인결과'] == '취약')])
    
    penalty = (high_risk_items / total_items) * 20
    final_score = max(0, base_score - penalty)
    
    return round(final_score, 1)

def show_download_buttons():
    """다운로드 버튼 섹션"""
    st.markdown('<div class="download-section">', unsafe_allow_html=True)
    st.markdown("### 📥 전체 상세 보고서 다운로드")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📄 PDF 보고서", use_container_width=True):
            st.info("PDF 보고서를 생성중입니다...")
            # TODO: PDF 생성 로직
        
        if st.button("📊 Excel 보고서", use_container_width=True):
            st.info("Excel 보고서를 생성중입니다...")
            # TODO: Excel 생성 로직
    
    with col2:
        if st.button("📋 요약 보고서", use_container_width=True):
            st.info("요약 보고서를 생성중입니다...")
            # TODO: 요약 보고서 생성
        
        if st.button("🔄 새로고침", use_container_width=True):
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

def load_json_data():
    """JSON 데이터 로드"""
    try:
        # 기존 코드의 load_json_data 함수 재사용
        base_dir = os.path.dirname(os.path.abspath(__file__))
        result_dir = os.path.join(base_dir, "../result")
        
        if not os.path.exists(result_dir):
            return pd.DataFrame()
        
        json_files = [f for f in os.listdir(result_dir) if f.endswith(".json")]
        
        if not json_files:
            return pd.DataFrame()
        
        all_data = []
        
        for json_file in json_files:
            file_path = os.path.join(result_dir, json_file)
            with open(file_path, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
                processed_data = process_json_data(json_data, json_file)
                all_data.extend(processed_data)
        
        return pd.DataFrame(all_data) if all_data else pd.DataFrame()
        
    except Exception as e:
        st.error(f"데이터 로드 오류: {e}")
        return pd.DataFrame()

def process_json_data(json_data, filename):
    """JSON 데이터 처리 (기존 로직 재사용)"""
    processed_items = []
    
    target_ip = json_data.get('targetip', 'Unknown')
    tested_time = json_data.get('testedtime', 'Unknown')
    os_info = json_data.get('osinfo', 'Unknown')
    
    if 'result' in json_data and isinstance(json_data['result'], list):
        for item in json_data['result']:
            processed_item = {
                'PC명': f"PC-{target_ip.split('.')[-1]}" if target_ip != 'Unknown' else 'PC-Unknown',
                '점검항목': item.get('title', 'N/A'),
                '확인결과': convert_result_code(item.get('result', 0)),
                '위험도': convert_importance_code(item.get('importance', 0)),
                '조치방법': item.get('resultdetail', 'N/A'),
                '카테고리': classify_item_category(item.get('title', '')),
                'OS정보': os_info,
                '진단시점': tested_time
            }
            processed_items.append(processed_item)
    
    return processed_items

def convert_result_code(code):
    """결과 코드 변환"""
    mapping = {0: "양호", 1: "취약", 2: "해당없음"}
    return mapping.get(code, "알수없음")

def convert_importance_code(code):
    """중요도 코드 변환"""
    mapping = {1: "낮음", 2: "보통", 3: "높음"}
    return mapping.get(code, "알수없음")

# 메인 실행
if __name__ == "__main__":
    main()