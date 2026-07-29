import streamlit as st
import sxtwl
from datetime import datetime, timedelta, timezone
import warnings

warnings.filterwarnings('ignore')

st.set_page_config(page_title="Kỳ Môn Độn Giáp", layout="wide", initial_sidebar_state="collapsed")

# ==========================================
# 1. DỮ LIỆU CƠ BẢN & HẰNG SỐ
# ==========================================
thien_can = "甲乙丙丁戊己庚辛壬癸"
dia_chi = "子丑寅卯辰巳午未申酉戌亥"

luc_nghi = ["戊", "己", "庚", "辛", "壬", "癸", "丁", "丙", "乙"]
ring_8 = [1, 8, 3, 4, 9, 2, 7, 6]
star_ring = ["天蓬", "天任", "天冲", "天辅", "天英", "天芮", "天柱", "天心"]
door_ring = ["休门", "生门", "伤门", "杜门", "景门", "死门", "惊门", "开门"]
shen_yang = ["值符", "螣蛇", "太阴", "六合", "勾陈", "朱雀", "九地", "九天"]
shen_yin = ["值符", "螣蛇", "太阴", "六合", "白虎", "玄武", "九地", "九天"]

# --- HẰNG SỐ CHO PHƯƠNG PHÁP 卧龙转盘 (WOLONG) ---
WOLONG_OUTER_PALACES = [4, 9, 2, 7, 6, 1, 8, 3] # Tốn, Ly, Khôn, Đoài, Càn, Khảm, Cấn, Chấn
WOLONG_FLYING_PATH = [5, 6, 7, 8, 9, 1, 2, 3, 4]
WOLONG_STEM_TO_NUM = {"癸": 1, "丁": 2, "丙": 3, "乙": 4, "戊": 5, "己": 6, "庚": 7, "辛": 8, "壬": 9, "甲": 0}
WOLONG_NUM_TO_STEM = {v: k for k, v in WOLONG_STEM_TO_NUM.items()}
WOLONG_ORIGINAL_GATES = {1: "休门", 8: "生门", 3: "伤门", 4: "杜门", 9: "景门", 2: "死门", 7: "惊门", 6: "开门"}
WOLONG_CLOCKWISE_GATES = ["景门", "死门", "惊门", "开门", "休门", "生门", "伤门", "杜门"]

element_colors = {"木": "#007A00", "火": "#D90000", "土": "#996600", "金": "#555555", "水": "#0000CC"}
stem_elements = {"甲": "木", "乙": "木", "丙": "火", "丁": "火", "戊": "土", "己": "土", "庚": "金", "辛": "金", "壬": "水", "癸": "水"}
door_elements = {"休门": "水", "生门": "土", "伤门": "木", "杜门": "木", "景门": "火", "死门": "土", "惊门": "金", "开门": "金"}
star_elements = {"天蓬": "水", "天任": "土", "天冲": "木", "天辅": "木", "天英": "火", "天芮": "土", "天禽": "土", "禽": "土", "天柱": "金", "天心": "金"}
deity_elements = {"值符": "木", "螣蛇": "火", "太阴": "金", "六合": "木", "勾陈": "土", "白虎": "金", "朱雀": "火", "玄武": "水", "九地": "土", "九天": "金"}
palace_elements = {1: "水", 2: "土", 3: "木", 4: "木", 5: "土", 6: "金", 7: "金", 8: "土", 9: "火"}

stem_punish = {"戊": 3, "己": 2, "庚": 8, "辛": 9, "壬": 4, "癸": 4}
stem_tomb = {"辛": [4], "壬": [4], "丁": [8], "己": [8], "庚": [8], "癸": [2], "乙": [2, 6], "丙": [6], "戊": [6]}
shijia_earth_branch_map = {"戊": "子", "己": "戌", "庚": "申", "辛": "午", "壬": "辰", "癸": "寅", "丁": "卯", "丙": "寅", "乙": "丑"}

solar_term_ju = {
    "冬至":[1,7,4], "小寒":[2,8,5], "大寒":[3,9,6], "立春":[8,5,2], "雨水":[9,6,3], "惊蛰":[1,7,4],
    "春分":[3,9,6], "清明":[4,1,7], "谷雨":[5,2,8], "立夏":[4,1,7], "小满":[5,2,8], "芒种":[6,3,9],
    "夏至":[9,3,6], "小暑":[8,2,5], "大暑":[7,1,4], "立秋":[2,5,8], "处暑":[1,4,7], "白露":[9,3,6],
    "秋分":[7,1,4], "寒露":[6,9,3], "霜降":[5,8,2], "立冬":[6,9,3], "小雪":[5,8,2], "大雪":[4,7,1]
}
yang_terms = ["冬至", "小寒", "大寒", "立春", "雨水", "惊蛰", "春分", "清明", "谷雨", "立夏", "小满", "芒种"]
jq_names = ["冬至", "小寒", "大寒", "立春", "雨水", "惊蛰", "春分", "清明", "谷雨", "立夏", "小满", "芒种", "夏至", "小暑", "大暑", "立秋", "处暑", "白露", "秋分", "寒露", "霜降", "立冬", "小雪", "大雪"]
wolong_jq_order = ["大雪", "冬至", "小寒", "大寒", "立春", "雨水", "惊蛰", "春分", "清明", "谷雨", "立夏", "小满", "芒种", "夏至", "小暑", "大暑", "立秋", "处暑", "白露", "秋分", "寒露", "霜降", "立冬", "小雪"]

cung_to_gua = {1: "坎", 2: "坤", 3: "震", 4: "巽", 5: "", 6: "乾", 7: "兑", 8: "艮", 9: "离"}
chi_to_cung = {"子":1, "丑":8, "寅":8, "卯":3, "辰":4, "巳":4, "午":9, "未":2, "申":2, "酉":7, "戌":6, "亥":6}

dun_ju_list = ["Mặc định"] + [f"阳{i}" for i in range(1, 10)] + [f"阴{i}" for i in range(1, 10)]
jiazi_grouped_list = ["Mặc định"]
for can in thien_can:
    for chi in dia_chi:
        if (thien_can.index(can) % 2) == (dia_chi.index(chi) % 2):
            jiazi_grouped_list.append(f"{can}{chi}")

# ==========================================
# 2. LOGIC TÍNH LỊCH & ĐỘN CỤC CHUẨN XÁC
# ==========================================
def get_exact_jieqi(user_dt):
    day_obj = sxtwl.fromSolar(user_dt.year, user_dt.month, user_dt.day)
    temp_day = day_obj
    while not temp_day.hasJieQi():
        temp_day = sxtwl.fromSolar(temp_day.getSolarYear(), temp_day.getSolarMonth(), temp_day.getSolarDay() - 1)
    return jq_names[temp_day.getJieQi()]

def get_standard_term_and_cuc(day_obj, exact_term):
    loai_don = "阳遁" if exact_term in yang_terms else "阴遁"
    d_gz = day_obj.getDayGZ()
    offset = d_gz.tg % 5
    phu_tou_chi_idx = (d_gz.dz - offset) % 12
    yuan = 0 if phu_tou_chi_idx in [0, 6, 3, 9] else 1 if phu_tou_chi_idx in [2, 8, 5, 11] else 2
    return loai_don, solar_term_ju[exact_term][yuan], exact_term

def get_wushu_dun(day_stem, hour_branch):
    """Tính Can Giờ dựa trên Can Ngày (Ngũ Thử Độn)"""
    day_idx = thien_can.index(day_stem) % 5
    hour_idx = dia_chi.index(hour_branch)
    start_stem_idx = (day_idx * 2) % 10
    target_stem_idx = (start_stem_idx + hour_idx) % 10
    return thien_can[target_stem_idx]

def get_xun_leader(can, chi):
    """Tìm Tuần Thủ (Giáp ◯) của một Can Chi"""
    idx_can, idx_chi = thien_can.index(can), dia_chi.index(chi)
    chi_tuan = dia_chi[(idx_chi - idx_can) % 12]
    return {"子":"戊", "戌":"己", "申":"庚", "午":"辛", "辰":"壬", "寅":"癸"}[chi_tuan]

# --- HÀM TÍNH LỊCH WOLONG CHÂN TRUYỀN TỰ ĐỘNG ---
def get_wolong_calendar_data(lunar_month, lunar_day):
    """Tự động nội suy Bảng 1 của tác giả (1 năm = 360 ngày chuẩn)"""
    # Tính số ngày tuyệt đối từ mốc 1/11 AL
    m_offset = (lunar_month - 11) % 12
    abs_day = m_offset * 30 + (lunar_day - 1)
    
    # 1. Tính Can Chi Ngày (Mốc 1/11 là 己酉 - index 45 trong mảng 60)
    can_chi_idx = (45 + abs_day) % 60
    wl_can = thien_can[can_chi_idx % 10]
    wl_chi = dia_chi[can_chi_idx % 12]
    
    # 2. Tính Tiết Khí (Mỗi tiết đúng 15 ngày)
    jq_idx = abs_day // 15
    wl_jieqi = wolong_jq_order[jq_idx % 24]
    
    # 3. Tính Tam Nguyên
    day_in_jq = abs_day % 15
    if day_in_jq < 5: wl_yuan = "上"
    elif day_in_jq < 10: wl_yuan = "中"
    else: wl_yuan = "下"
    
    # 4. Tính Âm/Dương Độn
    # Trong mảng wolong_jq_order: Từ 冬至(index 1) đến 芒种(index 12) là Dương Độn
    if 1 <= jq_idx % 24 <= 12:
        wl_dun = "阳遁"
    else:
        wl_dun = "阴遁"
        
    return wl_can, wl_chi, wl_jieqi, wl_yuan, wl_dun

# ==========================================
# 3. HỆ THỐNG LẬP QUẺ WOLONG (CHÂN TRUYỀN)
# ==========================================
def lap_que_wolong(can_ngay, hoa_giap_gio, dun_type, ju_num):
    can_gio, chi_gio = hoa_giap_gio[0], hoa_giap_gio[1]
    
    cung_data = {i: {'dia': '', 'sao': '', 'mon': '', 'than': '', 'thien': '', 'ngua': '', 'ancan': ''} for i in range(1, 10)}
    
    # --- BƯỚC 3: DỰNG ĐỊA BÀN ---
    if dun_type == "阳遁":
        trung_cung_val = 10 - ju_num
        step_dir = 1
    else:
        trung_cung_val = ju_num
        step_dir = -1

    dia_ban = {}
    current_val = trung_cung_val
    for cung in WOLONG_FLYING_PATH:
        # Chuyển số thành Can theo bảng mã hóa của tác giả
        can_tai_cung = WOLONG_NUM_TO_STEM.get(current_val, "")
        dia_ban[cung] = can_tai_cung
        cung_data[cung]['dia'] = can_tai_cung
        
        current_val += step_dir
        if current_val > 9: current_val = 1
        if current_val < 1: current_val = 9

    # Tìm vị trí Giáp ◯
    luc_nghi_gio = get_xun_leader(can_gio, chi_gio)
    p_circle = [c for c, can in dia_ban.items() if can == luc_nghi_gio][0]

    # --- BƯỚC 4: DỰNG THIÊN BÀN ---
    p_hour_stem = [c for c, can in dia_ban.items() if can == can_gio]
    p_hour_stem = p_hour_stem[0] if p_hour_stem else 5 # Fallback nếu ko tìm thấy

    if p_circle == 5:
        # Giáp kẹt ở Trung Cung -> Thiên Bàn = Địa Bàn
        for i in range(1, 10):
            cung_data[i]['thien'] = dia_ban[i]
    else:
        # Xoay vòng ngoài
        idx_source = WOLONG_OUTER_PALACES.index(p_circle)
        idx_target = WOLONG_OUTER_PALACES.index(p_hour_stem) if p_hour_stem != 5 else idx_source
        offset = (idx_target - idx_source) % 8
        
        for i in range(8):
            cung_hien_tai = WOLONG_OUTER_PALACES[i]
            cung_nguon = WOLONG_OUTER_PALACES[(i - offset) % 8]
            cung_data[cung_hien_tai]['thien'] = dia_ban[cung_nguon]
        cung_data[5]['thien'] = dia_ban[5]

    # Đánh dấu ◯ cho Thiên Can
    cung_data[p_hour_stem]['thien'] += "◯"
    cung_data[p_circle]['dia'] += "◯"

    # --- BƯỚC 5: AN BÁT MÔN ---
    if p_circle == 5:
        # Tướng kẹt ở trung cung -> Bát môn về nguyên vị trí
        for p, door in WOLONG_ORIGINAL_GATES.items():
            cung_data[p]['mon'] = door
    else:
        g_start = WOLONG_ORIGINAL_GATES[p_circle]
        s_steps = thien_can.index(can_gio) + 1 # 甲=1, 乙=2...
        
        # Đếm trên đường bay Cửu cung
        seq = [1,2,3,4,5,6,7,8,9] if dun_type == "阳遁" else [9,8,7,6,5,4,3,2,1]
        idx_start = seq.index(p_circle)
        p_land = seq[(idx_start + s_steps - 1) % 9]

        if p_land == 5:
            # Điểm hạ cánh ở trung cung -> Bát môn về nguyên vị trí
            for p, door in WOLONG_ORIGINAL_GATES.items():
                cung_data[p]['mon'] = door
        else:
            # Xoay vòng Bát Môn
            idx_land_palace = WOLONG_OUTER_PALACES.index(p_land)
            idx_gate_start = WOLONG_CLOCKWISE_GATES.index(g_start)
            
            for i in range(8):
                cung_dich = WOLONG_OUTER_PALACES[(idx_land_palace + i) % 8]
                cua_se_dat = WOLONG_CLOCKWISE_GATES[(idx_gate_start + i) % 8]
                cung_data[cung_dich]['mon'] = cua_se_dat

    return cung_data

# ==========================================
# 4. HỆ THỐNG LẬP QUẺ CHUẨN (CŨ)
# ==========================================
def lap_que_standard(hoa_giap_gio, loai_don, so_cuc, display_mode):
    can_gio, chi_gio = hoa_giap_gio[0], hoa_giap_gio[1]
    loai = "阳" if loai_don == "阳遁" else "阴"
    can_tuan = get_xun_leader(can_gio, chi_gio)

    dia_ban = {((so_cuc + i) % 9 or 9 if loai == "阳" else (so_cuc - i) % 9 or 9): can for i, can in enumerate(luc_nghi)}
    cung_goc = [c for c, can in dia_ban.items() if can == can_tuan][0]

    cg_ring = 2 if cung_goc == 5 else cung_goc
    cg_idx = ring_8.index(cg_ring)
    truc_su = door_ring[cg_idx]
    
    if display_mode == "十家转盘":
        yang_stems = ['甲', '乙', '丙', '丁', '戊']
        yin_stems = ['己', '庚', '辛', '壬', '癸']
        if can_gio in yang_stems:
            steps = yang_stems.index(can_gio)
            target_star = (so_cuc - steps) % 9 or 9 if loai == "阳" else (so_cuc + steps) % 9 or 9
        else:
            steps = yin_stems.index(can_gio)
            target_star = (so_cuc + steps) % 9 or 9 if loai == "阳" else (so_cuc - steps) % 9 or 9
    else:
        can_tim_kiem = can_tuan if can_gio == "甲" else can_gio
        target_star = [c for c, can in dia_ban.items() if can == can_tim_kiem][0]

    if target_star == 5: target_star = 2
    ts_idx = ring_8.index(target_star)

    steps = (dia_chi.index(chi_gio) - dia_chi.index(dia_chi[(dia_chi.index(chi_gio) - thien_can.index(can_gio)) % 12])) % 12
    target_door = (cung_goc + steps) % 9 or 9 if loai == "阳" else (cung_goc - steps) % 9 or 9
    cung_truc_su = target_door
    
    if target_door == 5: target_door = 2
    td_idx = ring_8.index(target_door)

    cung_data = {i: {'dia': '', 'sao': '', 'mon': '', 'than': '', 'thien': '', 'ngua': '', 'ancan': ''} for i in range(1, 10)}

    for i in range(1, 10):
        if i == 2: cung_data[i]['dia'] = f"{dia_ban.get(2, '')}/{dia_ban.get(5, '')}"
        else: cung_data[i]['dia'] = dia_ban.get(i, "")

    for i in range(8):
        p = ring_8[i]
        orig_star_idx = (cg_idx + (i - ts_idx)) % 8
        sao = star_ring[orig_star_idx]
        orig_palace = ring_8[orig_star_idx]

        cung_data[p]['sao'] = sao
        cung_data[p]['thien'] = dia_ban[orig_palace]
        if sao == "天芮":
            cung_data[p]['sao'] = "天芮/禽"
            cung_data[p]['thien'] = f"{dia_ban[orig_palace]}/{dia_ban.get(5, '')}"

        orig_door_idx = (cg_idx + (i - td_idx)) % 8
        cung_data[p]['mon'] = door_ring[orig_door_idx]
        if loai == "阳": deity_idx = (i - ts_idx) % 8
        else: deity_idx = (ts_idx - i) % 8
        cung_data[p]['than'] = shen_yang[deity_idx] if loai == "阳" else shen_yin[deity_idx]

    return cung_data, can_gio, truc_su

# ==========================================
# 5. GIAO DIỆN HTML RENDER
# ==========================================
def render_html_table(cung_data, display_mode):
    luoi_lac_thu = [[4, 9, 2], [3, 5, 7], [8, 1, 6]]
    
    html = f"""
    <style>
        .qmdj-table {{ border-collapse: collapse; width: 100%; max-width: 480px; min-width: 320px; height: 360px; table-layout: fixed; font-size: 15px; background-color: #fefefe; margin: 0 auto; }}
        .qmdj-td {{ border: 1px solid #bfbfbf; width: 33.33%; padding: 8px 4px 18px 4px; position: relative; vertical-align: top; overflow: visible; }}
        .row-top, .row-mid, .row-bot {{ display: flex; align-items: center; justify-content: flex-start; }}
        .item-left {{ width: 55px; text-align: left; margin-left: 2px; flex-shrink: 0; line-height: 1.2; font-weight: normal; color: #333; }}
        .item-right {{ display: flex; align-items: center; flex-wrap: wrap; flex-grow: 1; gap: 2px 3px; line-height: 1.2; margin-left: 10px; font-weight: bold; color: #b30000; font-size: 18px; }}
        .wolong-stem {{ display: inline-block; padding: 2px 4px; }}
        .circle-mark {{ font-size: 14px; margin-left: 2px; color: #000; }}
        .bagua-mark {{ position: absolute; bottom: 2px; right: 6px; color: #1a1a1a; font-size: 13px; cursor: pointer; z-index: 20; }}
        
        .default-top {{ margin-bottom: 8px; }}
        .default-mid {{ margin-bottom: 6px; }}
        .default-bot {{ margin-bottom: 0px; }}
        .wolong-spacing {{ margin-top: 15px; margin-bottom: 25px; }}
    </style>
    <table class="qmdj-table">
    """

    for row in luoi_lac_thu:
        html += "<tr>"
        for p in row:
            d = cung_data[p]
            gua_char = cung_to_gua[p]
            gua_html = f"<div class='bagua-mark'>{gua_char}</div>" if gua_char else ""

            if display_mode == "卧龙转盘":
                # Render riêng cho Wolong (Không sao, không thần)
                thien_html = d['thien'].replace("◯", "<span class='circle-mark'>◯</span>")
                dia_html = d['dia'].replace("◯", "<span class='circle-mark'>◯</span>")
                
                if p == 5:
                    html += f"""
                    <td class="qmdj-td">
                        <div style="position: absolute; bottom: 6px; right: 10px; font-size: 16px; font-weight: bold; color: #b30000;">{dia_html}</div>
                    </td>"""
                else:
                    html += f"""
                    <td class="qmdj-td">
                        {gua_html}
                        <div class="row-top wolong-spacing">
                            <div class="item-left"></div>
                            <div class="item-right"><span class="wolong-stem">{thien_html}</span></div>
                        </div>
                        <div class="row-bot">
                            <div class="item-left">{d['mon']}</div>
                            <div class="item-right"><span class="wolong-stem">{dia_html}</span></div>
                        </div>
                    </td>"""
            else:
                # Render cho các phái cũ
                if p == 5:
                    html += f"""<td class="qmdj-td"><div style="position: absolute; bottom: 6px; right: 10px; font-size: 16px; font-weight: bold; color: #b30000;">{d['dia']}</div></td>"""
                else:
                    html += f"""
                    <td class="qmdj-td">
                        {gua_html}
                        <div class="row-top default-top"><div class="item-left">{d['than']}</div></div>
                        <div class="row-mid default-mid">
                            <div class="item-left">{d['sao']}</div>
                            <div class="item-right">{d['thien']}</div>
                        </div>
                        <div class="row-bot default-bot">
                            <div class="item-left">{d['mon']}</div>
                            <div class="item-right">{d['dia']}</div>
                        </div>
                    </td>"""
        html += "</tr>"
        
    html += "</table>"
    return html

# ==========================================
# 6. APP MAIN LOOP
# ==========================================
def get_current_vn_time():
    return datetime.now(timezone(timedelta(hours=7)))

if "init_dt" not in st.session_state:
    st.session_state.init_dt = get_current_vn_time()

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    display_mode = st.selectbox("Hiển thị", ["拆补转盘", "十家转盘", "卧龙转盘"])
with col2:
    selected_date = st.date_input("Ngày", st.session_state.init_dt.date())
with col3:
    selected_time = st.time_input("Giờ Phút", st.session_state.init_dt.time(), step=60)
with col4:
    override_dun_ju = st.selectbox("Âm/Dương Cục", dun_ju_list)
with col5:
    override_jiazi = st.selectbox("Hoa Giáp", jiazi_grouped_list)

user_dt = datetime.combine(selected_date, selected_time)

if user_dt.hour >= 23:
    actual_date = user_dt.date() + timedelta(days=1)
    chi_gio_idx = 0 
else:
    actual_date = user_dt.date()
    chi_gio_idx = (user_dt.hour + 1) // 2 % 12

chi_gio = dia_chi[chi_gio_idx]

# Tính lịch âm 
day_obj = sxtwl.fromSolar(actual_date.year, actual_date.month, actual_date.day)

if display_mode == "卧龙转盘":
    # Lấy dữ liệu Chân Truyền Lịch
    lunar_m = day_obj.getLMo()
    lunar_d = day_obj.getLDi()
    
    wl_can, wl_chi, wl_jieqi, wl_yuan, wl_dun = get_wolong_calendar_data(lunar_m, lunar_d)
    
    # Tính Can Giờ
    if override_jiazi != "Mặc định":
        hoa_giap_hien_tai = override_jiazi[:2]
    else:
        can_gio = get_wushu_dun(wl_can, chi_gio)
        hoa_giap_hien_tai = can_gio + chi_gio
        
    # Tính Cục Số (Trích xuất Base Ju chuẩn kết hợp offset)
    yuan_idx = 0 if wl_yuan == "上" else 1 if wl_yuan == "中" else 2
    base_ju = solar_term_ju[wl_jieqi][yuan_idx]
    hour_stem_offset = {"甲":0, "己":0, "乙":1, "庚":1, "丙":2, "辛":2, "丁":3, "壬":3, "戊":4, "癸":4}[hoa_giap_hien_tai[0]]
    
    if wl_dun == "阳遁":
        wl_ju = (base_ju + hour_stem_offset - 1) % 9 + 1
    else:
        wl_ju = (base_ju - hour_stem_offset - 1) % 9 + 1
        if wl_ju <= 0: wl_ju += 9
        
    if override_dun_ju != "Mặc định":
        wl_dun = "阳遁" if "阳" in override_dun_ju else "阴遁"
        wl_ju = int(override_dun_ju[-1])

    # Lập Quẻ
    data = lap_que_wolong(wl_can, hoa_giap_hien_tai, wl_dun, wl_ju)
    
    chuoi_cuc = f"{wl_dun}{wl_ju}局 | {wl_jieqi}{wl_yuan}元"
    bazi_chuoi = f"农历 {lunar_m}月 {lunar_d}日 (日干支: {wl_can}{wl_chi})"
    hour_str = f"<b>{hoa_giap_hien_tai}</b>时"

else:
    # Logic cho các phái cũ
    can_ngay_idx = day_obj.getDayGZ().tg
    can_gio_idx = (can_ngay_idx % 5 * 2 + chi_gio_idx) % 10
    can_gio_str = thien_can[can_gio_idx]

    if override_jiazi != "Mặc định":
        hoa_giap_hien_tai = override_jiazi[:2]
    else:
        hoa_giap_hien_tai = can_gio_str + chi_gio

    bazi_dict = {
        'nam': thien_can[day_obj.getYearGZ().tg]+dia_chi[day_obj.getYearGZ().dz],
        'thang': thien_can[day_obj.getMonthGZ().tg]+dia_chi[day_obj.getMonthGZ().dz],
        'ngay': thien_can[day_obj.getDayGZ().tg]+dia_chi[day_obj.getDayGZ().dz]
    }

    exact_term = get_exact_jieqi(user_dt)
    if display_mode == "十家转盘":
        don, cuc, _ = get_standard_term_and_cuc(day_obj, exact_term) # Giả lập Shijia
    else:
        don, cuc, _ = get_standard_term_and_cuc(day_obj, exact_term)

    if override_dun_ju != "Mặc định":
        don = "阳遁" if "阳" in override_dun_ju else "阴遁"
        cuc = int(override_dun_ju[-1])

    data, _, _ = lap_que_standard(hoa_giap_hien_tai, don, cuc, display_mode)
    
    chuoi_cuc = f"{don}{cuc}局"
    bazi_chuoi = f"{bazi_dict['nam']}年 {bazi_dict['thang']}月 {bazi_dict['ngay']}日"
    hour_str = f"{hoa_giap_hien_tai}时"


# --- HTML RENDER ---
title = f"<h3 style='margin-bottom:8px; font-family:sans-serif; color: #1a1a1a; font-weight: normal; font-size: 18px; text-align: center;'>{bazi_chuoi} {hour_str}</h3>"
sub_title = f"<h4 style='margin-top:0px; margin-bottom:8px; font-family:sans-serif; color: #555; font-weight: normal; font-size: 16px; text-align: center;'>奇门遁甲 ({display_mode}) | {chuoi_cuc}</h4>"

qimen_board_html = render_html_table(data, display_mode)

combined_html = f"""
    <div style="display: flex; flex-direction: column; align-items: center; width: 100%; padding-top: 10px;">
        <div style="display: flex; flex-direction: column; align-items: center; width: 100%; max-width: 480px;">
            {title}
            {sub_title}
            {qimen_board_html}
        </div>
    </div>
"""
st.components.v1.html(combined_html, height=600, scrolling=True)
