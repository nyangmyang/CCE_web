from typing import List, Dict

def render_host_card(host: Dict, idx: int) -> str:
    """개별 호스트 카드 HTML 생성 (체크박스 포함)"""
    return f"""
    <div class='host-card'>
        <input type='checkbox' id='host-{idx}' name='host-{idx}' class='host-checkbox'/>
        <label for='host-{idx}'>
            <img src='{host["icon"]}' alt='OS Icon'/>
            <div class='host-info'>
                <div>IP: {host["ip"]}</div>
                <div>PORT: {host["port"]}</div>
                <div>설명: {host["desc"]}</div>
                <div>중요도: {host["importance"]}</div>
            </div>
        </label>
    </div>
    """

def render_host_grid(hosts: List[Dict]) -> str:
    """호스트 카드들을 HTML 그리드로 생성"""
    grid_html = "<div class='host-grid'>"
    
    for i in range(0, len(hosts), 2):
        grid_html += "<div class='host-row'>"
        
        # 첫 번째 카드
        grid_html += f"<div class='host-col'>{render_host_card(hosts[i], i)}</div>"
        
        # 두 번째 카드 (있는 경우)
        if i + 1 < len(hosts):
            grid_html += f"<div class='host-col'>{render_host_card(hosts[i + 1], i + 1)}</div>"
        else:
            grid_html += "<div class='host-col'></div>"
        
        grid_html += "</div>"
    
    grid_html += "</div>"
    return grid_html