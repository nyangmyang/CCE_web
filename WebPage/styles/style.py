STYLES = """
<style>
* {font-family:'Nanum Gothic', sans-serif;}

/* 전체 컨테이너 */
.stApp > div:first-child > div:first-child > div:first-child {
    padding-top: 1rem;
}

/* 메인 영역 */
.main-container {
    padding: 2rem;    
}

/* 콘텐츠 영역 - 스크롤 설정 */
.content-area {
    background: white;
    border-radius: 8px;
    padding: 2rem;
    margin-bottom: 2rem;
    max-height: 500px;
    overflow-y: auto;
    border: 1px solid #e0e0e0;
}

/* 커스텀 스크롤바 */
.content-area::-webkit-scrollbar {
    width: 8px;
}

.content-area::-webkit-scrollbar-track {
    background: #f1f1f1;
    border-radius: 4px;
}

.content-area::-webkit-scrollbar-thumb {
    background: #c1c1c1;
    border-radius: 4px;
}

.content-area::-webkit-scrollbar-thumb:hover {
    background: #a8a8a8;
}

/* 헤더 영역 */
.header-section {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 2rem;
}

.header-title {
    font-size: 1.5rem;
    font-weight: bold;
    color: #333;
}

/* 호스트 그리드 */
.host-grid {
    width: 100%;
}

.host-row {
    display: flex;
    gap: 1rem;
    margin-bottom: 1rem;
}

.host-col {
    flex: 1;
}

/* 호스트 카드 */
.host-card {
    background: #9e9e9e;
    color: white;
    border-radius: 12px;
    padding: 1.5rem;
    text-align: center;
    min-height: 150px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    cursor: pointer;
    transition: transform 0.2s, box-shadow 0.2s;
}

.host-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0,0,0,0.15);
}

.host-card img {
    width: 48px;
    height: 48px;
    margin-bottom: 0.8rem;
    object-fit: contain;
}

.host-card .host-info {
    line-height: 1.4;
}

.host-card .host-info div {
    margin: 3px 0;
    font-size: 14px;
}

/* 실행 버튼 영역 */
.run-button-container {
    position: fixed;
    bottom: 2rem;
    right: 2rem;
    z-index: 1000;
}

/* Streamlit 기본 스타일 조정 */
.stButton > button {
    background-color: #666;
    color: white;
    border: none;
    padding: 0.5rem 2rem;
    border-radius: 4px;
    font-size: 14px;
}

.stButton > button:hover {
    background-color: #555;
}

/* 사이드바 숨기기 */
.css-1d391kg {
    display: none;
}

/* 여백 조정 */
.block-container {
    padding-top: 1rem;
    padding-bottom: 1rem;
}

/* 스크롤 영역 내부 여백 */
.element-container {
    margin-bottom: 0.5rem;
}
</style>
"""