import streamlit as st
import sxtwl
from datetime import datetime, timedelta, timezone
import warnings

warnings.filterwarnings('ignore')

st.set_page_config(page_title="Kỳ Môn Phi Bàn", layout="wide", initial_sidebar_state="collapsed")

# ==========================================
# 1. HỆ THỐNG DỮ LIỆU CƠ BẢN (PHI BÀN)
# ==========================================
thien_can = "甲乙丙丁戊己庚辛壬癸"
dia_chi = "子丑寅卯辰巳午未申酉戌亥"
luc_nghi = ["戊", "己", "庚", "辛", "壬", "癸", "丁", "丙", "乙"]

luoshu_9 = [1, 2, 3, 4, 5, 6, 7, 8, 9]

star_native = ["天蓬", "天芮", "天冲", "天辅", "天禽", "天心", "天柱", "天任", "天英"]
deity_9 = ["值符", "螣蛇", "太阴", "六合", "勾陈", "太常", "朱雀", "九地", "九天"]

jq_names = ["冬至", "小寒", "大寒", "立春", "雨水", "惊蛰", "春分", "清明", "谷雨", "立夏", "小满", "芒种", 
            "夏至", "小暑", "大暑", "立秋", "处暑", "白露", "秋分", "寒露", "霜降", "立冬", "小雪", "大雪"]
yang_terms = ["冬至", "小寒", "大寒", "立春", "雨水", "惊蛰", "春分", "清明", "谷雨", "立夏", "小满", "芒种"]

solar_term_ju = {
    "冬至":[1,7,4], "小寒":[2,8,5], "大寒":[3,9,6], "立春":[8,5,2], "雨水":[9,6,3], "惊蛰":[1,7,4],
    "春分":[3,9,6], "清明":[4,1,7], "谷雨":[5,2,8], "立夏":[4,1,7], "小满":[5,2,8], "芒种":[6,3,9],
    "夏至":[9,3,6], "小暑":[8,2,5], "大暑":[7,1,4], "立秋":[2,5,8], "处暑":[1,4,7], "白露":[9,3,6],
    "秋分":[7,1,4], "寒露":[6,9,3], "霜降":[5,8,2], "立冬":[6,9,3], "小雪":[5,8,2], "大雪":[4,7,1]
}

JIEQI_PALACE_MAP = {
    "冬至": 1, "小寒": 1, "大寒": 1,
    "立春": 8, "雨水": 8, "惊蛰": 8,
    "春分": 3, "清明": 3, "谷雨": 3,
    "立夏": 4, "小满": 4, "芒种": 4,
    "夏至": 9, "小暑": 9, "大暑": 9,
    "立秋": 2, "处暑": 2, "白露": 2,
    "秋分": 7, "寒露": 7, "霜降": 7,
    "立冬": 6, "小雪": 6, "大雪": 6
}

# ==========================================
# 2. THUẬT TOÁN ĐỊNH CỤC TRÍ NHUẬN KHÁM TRẠM
# ==========================================
def get_phu_dau(d_date):
    for i in range(20):
        check_date = d_date - timedelta(days=i)
        day_obj = sxtwl.fromSolar(check_date.year, check_date.month, check_date.day)
        tg = day_obj.getDayGZ().tg  
        dz = day_obj.getDayGZ().dz  
        if (tg == 0 or tg == 5) and (dz in [0, 3, 6, 9]):
            return check_date
    return d_date

def get_station(start_date, include_start=False):
    start_offset = 0 if include_start else 1
    for i in range(start_offset, 250): 
        check_date = start_date - timedelta(days=i)
        day_obj = sxtwl.fromSolar(check_date.year, check_date.month, check_date.day)
        if day_obj.hasJieQi():
            jq_idx = day_obj.getJieQi()
            if jq_names[jq_idx] in ["芒种", "大雪"]:
                return check_date, jq_names[jq_idx]
    return None, None

def run_trinhuan_algorithm(D, T_tram_date, T_tram_name, T_prev_tram_date):
    F_past = get_phu_dau(T_tram_date)
    chao_shen = (T_tram_date - F_past).days
    
    is_leap = False
    is_fake_tie_qi = False

    if chao_shen >= 9:
        F_prev_past = get_phu_dau(T_prev_tram_date)
        chao_shen_prev = (T_prev_tram_date - F_prev_past).days
        
        if chao_shen_prev >= 9:
            is_fake_tie_qi = True
        else:
            is_leap = True 

    if is_fake_tie_qi:
        Start_Line = F_past + timedelta(days=15)
    else:
        Start_Line = F_past

    if D < Start_Line:
        T_prev2_tram_date, _ = get_station(T_prev_tram_date, include_start=False)
        day_prev_obj = sxtwl.fromSolar(T_prev_tram_date.year, T_prev_tram_date.month, T_prev_tram_date.day)
        T_prev_tram_name = jq_names[day_prev_obj.getJieQi()]
        
        return run_trinhuan_algorithm(D, T_prev_tram_date, T_prev_tram_name, T_prev2_tram_date)

    delta_days = (D - Start_Line).days
    block_index = delta_days // 15
    nguyen_index = (delta_days % 15) // 5 

    station_idx = jq_names.index(T_tram_name)
    
    if is_leap:
        if block_index == 0:
            final_idx = station_idx
        elif block_index == 1:
            final_idx = station_idx
        else:
            final_idx = (station_idx + block_index - 1) % 24 
    else:
        final_idx = (station_idx + block_index) % 24

    final_term = jq_names[final_idx]
    is_nhuan_hien_tai = (is_leap and block_index == 1)

    return final_term, nguyen_index, is_nhuan_hien_tai

def get_zhirun_ju(actual_date):
    D = actual_date
    T_tram_date, T_tram_name = get_station(D, include_start=True)
    T_prev_tram_date, _ = get_station(T_tram_date, include_start=False)
    final_term, nguyen_index, is_nhuan = run_trinhuan_algorithm(D, T_tram_date, T_tram_name, T_prev_tram_date)
    
    loai_don = "阳遁" if final_term in yang_terms else "阴遁"
    so_cuc = solar_term_ju[final_term][nguyen_index]
    ji_palace = JIEQI_PALACE_MAP[final_term]

    return loai_don, so_cuc, final_term, ji_palace, is_nhuan


# ==========================================
# 2B. CÁC HÀM TÍNH TOÁN BỔ SUNG ĐỘC LẬP 
# ==========================================
def get_cung_phi_tinh(nhat_chi, thoi_chi, loai_don):
    col_map = {
        "子": 0, "午": 0, "卯": 0, "酉": 0,
        "丑": 1, "未": 1, "辰": 1, "戌": 1,
        "寅": 2, "申": 2, "巳": 2, "亥": 2
    }
    matrix = [
        [[1, 9], [4, 6], [7, 3]], [[2, 8], [5, 5], [8, 2]], [[3, 7], [6, 4], [9, 1]], 
        [[4, 6], [7, 3], [1, 9]], [[5, 5], [8, 2], [2, 8]], [[6, 4], [9, 1], [3, 7]], 
        [[7, 3], [1, 9], [4, 6]], [[8, 2], [2, 8], [5, 5]], [[9, 1], [3, 7], [6, 4]], 
        [[1, 9], [4, 6], [7, 3]], [[2, 8], [5, 5], [8, 2]], [[3, 7], [6, 4], [9, 1]]  
    ]
    c_idx = col_map[nhat_chi]
    r_idx = dia_chi.index(thoi_chi)
    vals = matrix[r_idx][c_idx]
    return vals[0] if loai_don == "阳遁" else vals[1]

def get_luc_than(can_gio, can_cung):
    if not can_cung: return ""
    element_map = {"甲":0, "乙":0, "丙":1, "丁":1, "戊":2, "己":2, "庚":3, "辛":3, "壬":4, "癸":4}
    
    b_e = element_map[can_gio]
    t_e = element_map[can_cung]
    
    diff_e = (t_e - b_e) % 5 

    if diff_e == 0: return "兄"    
    elif diff_e == 1: return "孙"   
    elif diff_e == 2: return "财"   
    elif diff_e == 3: return "官"   
    elif diff_e == 4: return "父"   
    return ""

# ==========================================
# 3. THUẬT TOÁN PHI BÀN (TINH - MÔN - THẦN)
# ==========================================
def lap_que(hoa_giap_gio, nhat_chi, loai_don, so_cuc, ji_palace, can_thang, can_ngay, chi_thang):
    can_gio, chi_gio = hoa_giap_gio[0], hoa_giap_gio[1]
    loai = "阳" if loai_don == "阳遁" else "阴"
    
    idx_can, idx_chi = thien_can.index(can_gio), dia_chi.index(chi_gio)
    chi_tuan = dia_chi[(idx_chi - idx_can) % 12]
    can_tuan = {"子":"戊", "戌":"己", "申":"庚", "午":"辛", "辰":"壬", "寅":"癸"}[chi_tuan]

    # Khởi tạo mặc định: Màu xám đậm (#555) biểu thị trạng thái BÌNH THƯỜNG không hợp hóa
    cung_data = {i: {'dia': '', 'sao': '', 'mon': '', 'than': '', 'thien': '', 'ngua': '', 
                     'phi_tinh': 0, 'lt_thien': '', 'lt_dia': '',
                     'lt_thien_color': '#555', 'lt_thien_underline': False, 'lt_thien_circle': False} for i in range(1, 10)}

    center_num = get_cung_phi_tinh(nhat_chi, chi_gio, loai_don)
    quydo_luoshu = [5, 6, 7, 8, 9, 1, 2, 3, 4]
    
    curr_num = center_num
    for p in quydo_luoshu:
        cung_data[p]['phi_tinh'] = curr_num
        if loai == "阳":
            curr_num = (curr_num % 9) + 1 
        else:
            curr_num = 9 if curr_num == 1 else curr_num - 1 

    # --- 1. ĐỊA BÀN ---
    dia_ban = {}
    for i, can in enumerate(luc_nghi):
        p = (so_cuc + i - 1) % 9 + 1 if loai == "阳" else (so_cuc - i - 1) % 9 + 1
        dia_ban[p] = can
    
    for i in range(1, 10): 
        cung_data[i]['dia'] = dia_ban[i]
        cung_data[i]['lt_dia'] = get_luc_than(can_gio, dia_ban[i]) 

    # --- TÌM MÃ ---
    map_ngua = {"子":"寅", "丑":"亥", "寅":"申", "卯":"巳", "辰":"寅", "巳":"亥", "午":"申", "未":"巳", "申":"寅", "酉":"亥", "戌":"申", "亥":"巳"}
    cung_data[{"寅":8, "巳":4, "申":2, "亥":6}[map_ngua[chi_gio]]]['ngua'] = "马"

    # --- 2. THIÊN BÀN TINH & CAN ---
    base_star_p = [k for k, v in dia_ban.items() if v == can_tuan][0]
    target_star_p = [k for k, v in dia_ban.items() if v == (can_tuan if can_gio == "甲" else can_gio)][0]
    
    star_path_forward = luoshu_9  
    idx_base_star_fwd = star_path_forward.index(base_star_p)
    idx_target_star_fwd = star_path_forward.index(target_star_p)
    shift_for_star = (idx_target_star_fwd - idx_base_star_fwd) % 9
    
    for i in range(9):
        p_star = star_path_forward[i]
        orig_idx_star = (i - shift_for_star) % 9
        orig_p_star = star_path_forward[orig_idx_star]
        cung_data[p_star]['sao'] = star_native[orig_p_star - 1]

    path_9 = luoshu_9 if loai == "阳" else list(reversed(luoshu_9))
    idx_base = path_9.index(base_star_p)
    idx_target = path_9.index(target_star_p)
    star_shift = (idx_target - idx_base) % 9
    
    for i in range(9):
        p = path_9[i]
        orig_idx = (i - star_shift) % 9
        orig_p = path_9[orig_idx]
        
        can_thien_bay_toi = dia_ban[orig_p]
        cung_data[p]['thien'] = can_thien_bay_toi
        cung_data[p]['lt_thien'] = get_luc_than(can_gio, can_thien_bay_toi) 

        # ==============================================================
        # KIỂM TRA HỢP, KÍCH HÌNH, NHẬP KHỐ (Đọc và thiết lập CSS)
        # ==============================================================
        
        # 1. KIỂM TRA HỢP HÓA 
        combine_map = {
            '甲': ('己', '#8B4513'), '己': ('甲', '#8B4513'), # Thổ: Nâu đậm
            '乙': ('庚', '#000000'), '庚': ('乙', '#000000'), # Kim: Đen đậm
            '丙': ('辛', '#1E90FF'), '辛': ('丙', '#1E90FF'), # Thủy: Xanh da trời
            '丁': ('壬', '#008000'), '壬': ('丁', '#008000'), # Mộc: Xanh lá cây
            '戊': ('癸', '#FF0000'), '癸': ('戊', '#FF0000')  # Hỏa: Đỏ
        }
        target_can, hex_color = combine_map.get(can_thien_bay_toi, (None, '#555'))
        if target_can in [dia_ban[p], can_thang, can_ngay, can_gio]:
            cung_data[p]['lt_thien_color'] = hex_color

        # 2. KIỂM TRA KÍCH HÌNH
        kich_hinh_map = {'戊': 3, '己': 2, '庚': 8, '辛': 9, '壬': 4, '癸': 4}
        if kich_hinh_map.get(can_thien_bay_toi) == p:
            cung_data[p]['lt_thien_underline'] = True

        # 3. KIỂM TRA NHẬP KHỐ
        ruku_map = {
            '丙': ('戌', 6), '丁': ('戌', 6), '戊': ('戌', 6), '己': ('戌', 6),
            '庚': ('丑', 8), '辛': ('丑', 8),
            '壬': ('辰', 4), '癸': ('辰', 4),
            '甲': ('未', 2), '乙': ('未', 2)
        }
        if can_thien_bay_toi in ruku_map:
            kho_chi, kho_cung = ruku_map[can_thien_bay_toi]
            if p == kho_cung or chi_thang == kho_chi:
                cung_data[p]['lt_thien_circle'] = True
        # ==============================================================

    # --- 3. BÁT MÔN PHI BÀN ---
    door_native_dict = {1: "休门", 2: "死门", 3: "伤门", 4: "杜门", 6: "开门", 7: "惊门", 8: "生门", 9: "景门"}
    doors_cycle = ["休门", "死门", "伤门", "杜门", "开门", "惊门", "生门", "景门"]
    luoshu_8 = [1, 2, 3, 4, 6, 7, 8, 9]

    if base_star_p == 5:
        truc_su_door = door_native_dict[ji_palace]
    else:
        truc_su_door = door_native_dict[base_star_p]

    steps = (dia_chi.index(chi_gio) - dia_chi.index(chi_tuan)) % 12
    if loai == "阳":
        target_door_p = (so_cuc + steps - 1) % 9 + 1
    else:
        target_door_p = (so_cuc - steps - 1) % 9 + 1
        
    if target_door_p == 5:
        target_door_p = ji_palace
        
    idx_target_in_path8 = luoshu_8.index(target_door_p)
    shifted_palaces = luoshu_8[idx_target_in_path8:] + luoshu_8[:idx_target_in_path8]
    
    idx_truc_su = doors_cycle.index(truc_su_door)
    shifted_doors = doors_cycle[idx_truc_su:] + doors_cycle[:idx_truc_su]
    
    for p, door in zip(shifted_palaces, shifted_doors):
        cung_data[p]['mon'] = door

    # --- 4. CỬU THẦN ---
    for i in range(9):
        p = path_9[i]
        deity_idx = (i - idx_target) % 9
        cung_data[p]['than'] = deity_9[deity_idx]

    return cung_data

def tinh_tuan_khong_gio(hoa_giap):
    idx_can, idx_chi = thien_can.index(hoa_giap[0]), dia_chi.index(hoa_giap[1])
    idx_tuan_dau = (idx_chi - idx_can) % 12
    chi_to_cung = {"子":1, "丑":8, "寅":8, "卯":3, "辰":4, "巳":4, "午":9, "未":2, "申":2, "酉":7, "戌":6, "亥":6}
    return [chi_to_cung[dia_chi[(idx_tuan_dau - 2) % 12]], chi_to_cung[dia_chi[(idx_tuan_dau - 1) % 12]]]

# ==========================================
# 4. GIAO DIỆN LƯỚI CSS SẠCH SẼ
# ==========================================
def format_stem(stem_str):
    if not stem_str: return ""
    return stem_str

def format_sao(sao_str):
    if not sao_str: return ""
    return sao_str

def render_html_table(cung_data, tk_gio):
    luoi_lac_thu = [[4, 9, 2], [3, 5, 7], [8, 1, 6]]

    html = """
    <style>
        .qmdj-table { border-collapse: collapse; width: 100%; max-width: 550px; min-width: 320px; height: 380px; table-layout: fixed; font-family: sans-serif; margin: 0 auto; background: #fff;}
        .qmdj-td { border: 1px solid #aaa; width: 33.33%; position: relative; vertical-align: top; padding: 10px; }
        
        .cell-main {
            display: grid;
            grid-template-columns: auto auto 1fr;
            grid-template-rows: 22px 22px 22px;   
            column-gap: 15px; 
            row-gap: 6px;
            height: 100%;
            min-height: 85px;
            align-content: start;
            margin-top: 5px;
            margin-left: 5px; 
        }
        
        .item-than  { grid-column: 1 / span 2; grid-row: 1; font-size: 15px; color: #222; text-align: left; }
        .item-tinh  { grid-column: 1; grid-row: 2; font-size: 15px; color: #222; text-align: left; }
        .item-mon   { grid-column: 1; grid-row: 3; font-size: 15px; color: #222; text-align: left; }
        
        .item-thien { grid-column: 2; grid-row: 2; font-size: 15px; color: #222; text-align: left; display: flex; align-items: center;}
        .item-dia   { grid-column: 2; grid-row: 3; font-size: 15px; color: #222; text-align: left; display: flex; align-items: center;}

        .luc-than-dia { font-size: 11px; color: #555; margin-left: 6px; font-weight: normal; }
        .luc-than-thien { font-size: 11px; margin-left: 6px; font-weight: bold; }
        
        .top-right-indicators { position: absolute; top: 3px; right: 4px; display: flex; flex-direction: row; align-items: center; justify-content: flex-end; gap: 4px; color: #444; }
        .horse-icon { font-size: 14px; font-weight: bold; }
        .void-icon { font-size: 20px; font-weight: normal; line-height: 0.8; margin-top: -2px; }
        
        .bottom-left-phitinh { position: absolute; bottom: 3px; left: 5px; font-size: 15px; color: #555; font-weight: bold; }
    </style>
    <table class="qmdj-table">
    """

    for row in luoi_lac_thu:
        html += "<tr>"
        for p in row:
            d = cung_data[p]
            
            # --- Render CSS động cho Lục Thần Thiên Bàn ---
            thien_css_styles = f"color: {d['lt_thien_color']};"
            if d['lt_thien_color'] == '#000000':
                thien_css_styles += " font-weight: 900;" # Tăng độ đậm tuyệt đối cho Kim
                
            if d['lt_thien_underline']:
                thien_css_styles += " text-decoration: underline; text-underline-offset: 3px;"
                
            if d['lt_thien_circle']:
                # Dùng flexbox để mở rộng vòng tròn to rõ ràng, cân tâm chữ
                thien_css_styles += " border: 1px solid currentColor; border-radius: 50%; width: 22px; height: 22px; display: inline-flex; align-items: center; justify-content: center; margin-left: 4px;"
            
            lt_thien_html = f"<span class='luc-than-thien' style='{thien_css_styles}'>{d['lt_thien']}</span>" if d['lt_thien'] else ""
            lt_dia_html = f"<span class='luc-than-dia'>{d['lt_dia']}</span>" if d['lt_dia'] else ""
            
            thien_full = f"<span>{format_stem(d['thien'])}</span>{lt_thien_html}"
            dia_full = f"<span>{format_stem(d['dia'])}</span>{lt_dia_html}"
            
            phi_tinh_html = f"<div class='bottom-left-phitinh'>{d['phi_tinh']}</div>"
            
            if p == 5:
                html += f"""
                <td class="qmdj-td">
                    {phi_tinh_html}
                    <div class="cell-main">
                        <div class="item-than" style="visibility:hidden;">值符</div>
                        <div class="item-tinh" style="visibility:hidden;">天蓬</div>
                        <div class="item-mon" style="visibility:hidden;">休门</div>
                        
                        <div class="item-thien">{thien_full}</div>
                        <div class="item-dia">{dia_full}</div>
                    </div>
                </td>"""
                continue
                
            indicators = []
            if d.get('ngua'): indicators.append("<span class='horse-icon'>马</span>")
            if p in tk_gio: indicators.append("<span class='void-icon'>○</span>")
            indicator_html = f"<div class='top-right-indicators'>{''.join(indicators)}</div>" if indicators else ""
            
            html += f"""
            <td class="qmdj-td">
                {indicator_html}
                {phi_tinh_html}
                <div class="cell-main">
                    <div class="item-than">{d['than']}</div>
                    <div class="item-tinh">{format_sao(d['sao'])}</div>
                    <div class="item-mon"><span>{d['mon']}</span></div>
                    
                    <div class="item-thien">{thien_full}</div>
                    <div class="item-dia">{dia_full}</div>
                </div>
            </td>"""
        html += "</tr>"
        
    html += "</table>"
    return html

# ==========================================
# 5. GIAO DIỆN STREAMLIT
# ==========================================
def get_current_vn_time():
    return datetime.now(timezone(timedelta(hours=7)))

if "init_dt" not in st.session_state:
    st.session_state.init_dt = get_current_vn_time()

col1, col2 = st.columns(2)
with col1:
    selected_date = st.date_input("Ngày", value=st.session_state.init_dt.date(), min_value=datetime(1900, 1, 1).date(), max_value=datetime(2100, 12, 31).date())
with col2:
    selected_time = st.time_input("Giờ Phút", st.session_state.init_dt.time(), step=60)

user_dt = datetime.combine(selected_date, selected_time)

if user_dt.hour >= 23:
    actual_date = user_dt.date() + timedelta(days=1)
    chi_gio_idx = 0 
else:
    actual_date = user_dt.date()
    chi_gio_idx = (user_dt.hour + 1) // 2 % 12

chi_gio = dia_chi[chi_gio_idx]
day_obj = sxtwl.fromSolar(actual_date.year, actual_date.month, actual_date.day)

can_ngay_idx = day_obj.getDayGZ().tg
can_gio_idx = (can_ngay_idx % 5 * 2 + chi_gio_idx) % 10
hoa_giap_hien_tai = thien_can[can_gio_idx] + chi_gio

nhat_chi_hien_tai = dia_chi[day_obj.getDayGZ().dz] 
can_ngay_hien_tai = thien_can[day_obj.getDayGZ().tg]
can_thang_hien_tai = thien_can[day_obj.getMonthGZ().tg]
chi_thang_hien_tai = dia_chi[day_obj.getMonthGZ().dz]

bazi_dict = {
    'nam': thien_can[day_obj.getYearGZ().tg] + dia_chi[day_obj.getYearGZ().dz],
    'thang': can_thang_hien_tai + chi_thang_hien_tai,
    'ngay': can_ngay_hien_tai + nhat_chi_hien_tai
}

don, cuc, jq_name, ji_palace, is_nhuan = get_zhirun_ju(actual_date)

nhuan_str = " - 闰奇" if is_nhuan else ""
chuoi_cuc = f"飞盘 | {jq_name}{nhuan_str} - {don}{cuc}局 | 寄宫: {ji_palace}"
bazi_chuoi = f"{bazi_dict['nam']}年 {bazi_dict['thang']}月 {bazi_dict['ngay']}日 {hoa_giap_hien_tai}时"

tk_gio = tinh_tuan_khong_gio(hoa_giap_hien_tai)
data = lap_que(hoa_giap_hien_tai, nhat_chi_hien_tai, don, cuc, ji_palace, can_thang_hien_tai, can_ngay_hien_tai, chi_thang_hien_tai)

title = f"<h3 style='margin-bottom:6px; font-family:sans-serif; color: #111; font-weight: 400; font-size: 18px; text-align: center;'>{bazi_chuoi}</h3>"
sub_title = f"<h4 style='margin-top:0px; margin-bottom:15px; font-family:sans-serif; color: #555; font-weight: 300; font-size: 15px; text-align: center;'>{chuoi_cuc}</h4>"

qimen_board_html = render_html_table(data, tk_gio)

combined_html = f"""
    <div style="display: flex; flex-direction: column; align-items: center; width: 100%; padding-top: 10px;">
        <div style="display: flex; flex-direction: column; align-items: center; width: 100%; max-width: 520px;">
            {title}
            {sub_title}
            {qimen_board_html}
        </div>
    </div>
"""

st.components.v1.html(combined_html, height=600, scrolling=True)
