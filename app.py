import streamlit as st
import sxtwl
from datetime import datetime, timedelta, timezone
import warnings

warnings.filterwarnings('ignore')

st.set_page_config(page_title="Kỳ Môn Độn Giáp - Phi Bàn Trí Nhuận", layout="wide", initial_sidebar_state="collapsed")

# ==========================================
# 1. HỆ THỐNG DỮ LIỆU CƠ BẢN (PHI BÀN)
# ==========================================
thien_can = "甲乙丙丁戊己庚辛壬癸"
dia_chi = "子丑寅卯辰巳午未申酉戌亥"
luc_nghi = ["戊", "己", "庚", "辛", "壬", "癸", "丁", "丙", "乙"]

# Quỹ đạo Lạc Thư (Phi Bàn)
luoshu_9 = [1, 2, 3, 4, 5, 6, 7, 8, 9]
luoshu_8 = [1, 2, 3, 4, 6, 7, 8, 9] # Quỹ đạo Môn (Bỏ 5)

# Dữ liệu Gốc theo Lạc Thư (1 đến 9)
star_native = ["天蓬", "天芮", "天冲", "天辅", "天禽", "天心", "天柱", "天任", "天英"]
gate_native = ["休门", "死门", "伤门", "杜门", "开门", "惊门", "生门", "景门"] # Bỏ 5
deity_9 = ["值符", "螣蛇", "太阴", "六合", "勾陈", "太常", "朱雀", "九地", "九天"] # Cửu Thần

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

# Lưu giữ logic ẩn để dùng cho tương lai
door_elements = {"休门": "水", "生门": "土", "伤门": "木", "杜门": "木", "景门": "火", "死门": "土", "惊门": "金", "开门": "金"}
palace_elements = {1: "水", 2: "土", 3: "木", 4: "木", 5: "土", 6: "金", 7: "金", 8: "土", 9: "火"}
stem_tomb = {"辛": [4], "壬": [4], "丁": [8], "己": [8], "庚": [8], "癸": [2], "乙": [2, 6], "丙": [6], "戊": [6]}
stem_punish = {"戊": 3, "己": 2, "庚": 8, "辛": 9, "壬": 4, "癸": 4}

# ==========================================
# 2. THUẬT TOÁN ĐỊNH CỤC TRÍ NHUẬN CHUẨN XÁC
# ==========================================
def get_zhirun_ju(actual_date):
    actual_dt = datetime.combine(actual_date, datetime.min.time())
    start_date = datetime(actual_date.year - 1, 11, 1)
    
    jieqis = []
    curr = start_date
    while curr <= actual_dt + timedelta(days=40):
        d = sxtwl.fromSolar(curr.year, curr.month, curr.day)
        if d.hasJieQi():
            jq_name = jq_names[d.getJieQi()]
            t = sxtwl.JD2DD(d.getJieQiJD())
            dt = datetime(int(t.Y), int(t.M), int(t.D), int(t.h), int(t.m), int(t.s))
            jieqis.append({'name': jq_name, 'dt': dt})
        curr += timedelta(days=1)
        
    dz_idx = next(i for i, jq in enumerate(jieqis) if jq['name'] == '冬至')
    dz_dt = jieqis[dz_idx]['dt']
    
    best_tn_ft = None
    min_diff = 999
    for i in range(-20, 20):
        check_date = dz_dt + timedelta(days=i)
        d = sxtwl.fromSolar(check_date.year, check_date.month, check_date.day)
        gz = d.getDayGZ()
        if gz.tg in [0, 5] and gz.dz in [0, 6, 3, 9]:
            diff = abs(i)
            if diff < min_diff:
                min_diff = diff
                best_tn_ft = check_date.replace(hour=0, minute=0, second=0)
                
    current_tn_ft = best_tn_ft
    jq_idx = dz_idx
    periods = []
    
    while current_tn_ft <= actual_dt + timedelta(days=15):
        jq_name = jieqis[jq_idx]['name']
        jq_dt = jieqis[jq_idx]['dt']
        diff_days = (jq_dt - current_tn_ft).days
        
        periods.append({'start': current_tn_ft, 'end': current_tn_ft + timedelta(days=15), 'jq': jq_name})
        
        if diff_days >= 8 and jq_name in ["芒种", "大雪"]:
            current_tn_ft += timedelta(days=15)
            periods.append({'start': current_tn_ft, 'end': current_tn_ft + timedelta(days=15), 'jq': jq_name + " (Nhuận)"})
            jq_idx += 1 
            current_tn_ft += timedelta(days=15)
        else:
            jq_idx += 1
            current_tn_ft += timedelta(days=15)
            
    active_period = None
    for p in periods:
        if p['start'] <= actual_dt < p['end']:
            active_period = p
            break
            
    active_jq = active_period['jq'].replace(" (Nhuận)", "")
    
    d = sxtwl.fromSolar(actual_date.year, actual_date.month, actual_date.day)
    offset = d.getDayGZ().tg % 5
    ft_date = actual_date - timedelta(days=offset)
    ft_d = sxtwl.fromSolar(ft_date.year, ft_date.month, ft_date.day)
    
    if ft_d.getDayGZ().dz in [0, 6, 3, 9]: yuan = 0
    elif ft_d.getDayGZ().dz in [2, 8, 5, 11]: yuan = 1
    else: yuan = 2
    
    loai_don = "阳遁" if active_jq in yang_terms else "阴遁"
    so_cuc = solar_term_ju[active_jq][yuan]
    
    ji_palace = JIEQI_PALACE_MAP[active_jq]
    is_nhuan = " (Nhuận)" in active_period['jq']
    
    return loai_don, so_cuc, active_jq, ji_palace, is_nhuan

# ==========================================
# 3. THUẬT TOÁN PHI BÀN (TINH - MÔN - THẦN)
# ==========================================
def lap_que(hoa_giap_gio, loai_don, so_cuc, ji_palace):
    can_gio, chi_gio = hoa_giap_gio[0], hoa_giap_gio[1]
    loai = "阳" if loai_don == "阳遁" else "阴"
    
    idx_can, idx_chi = thien_can.index(can_gio), dia_chi.index(chi_gio)
    chi_tuan = dia_chi[(idx_chi - idx_can) % 12]
    can_tuan = {"子":"戊", "戌":"己", "申":"庚", "午":"辛", "辰":"壬", "寅":"癸"}[chi_tuan]

    cung_data = {i: {'dia': '', 'sao': '', 'mon': '', 'than': '', 'thien': '', 'ngua': ''} for i in range(1, 10)}

    # --- 1. ĐỊA BÀN (Phi Lạc Thư 9 cung) ---
    dia_ban = {}
    for i, can in enumerate(luc_nghi):
        p = (so_cuc + i - 1) % 9 + 1 if loai == "阳" else (so_cuc - i - 1) % 9 + 1
        dia_ban[p] = can
    
    for i in range(1, 10): cung_data[i]['dia'] = dia_ban[i]

    # --- TÌM MÃ ---
    map_ngua = {"子":"寅", "丑":"亥", "寅":"申", "卯":"巳", "辰":"寅", "巳":"亥", "午":"申", "未":"巳", "申":"寅", "酉":"亥", "戌":"申", "亥":"巳"}
    cung_data[{"寅":8, "巳":4, "申":2, "亥":6}[map_ngua[chi_gio]]]['ngua'] = "马"

    # --- 2. THIÊN BÀN TÌNH & CAN (Phi Cung Lạc Thư Tiến/Lùi theo Âm Dương) ---
    base_star_p = [k for k, v in dia_ban.items() if v == can_tuan][0]
    target_star_p = [k for k, v in dia_ban.items() if v == (can_tuan if can_gio == "甲" else can_gio)][0]
    
    path_9 = luoshu_9 if loai == "阳" else list(reversed(luoshu_9))
    idx_base = path_9.index(base_star_p)
    idx_target = path_9.index(target_star_p)
    star_shift = (idx_target - idx_base) % 9
    
    for i in range(9):
        p = path_9[i]
        orig_idx = (i - star_shift) % 9
        orig_p = path_9[orig_idx]
        
        cung_data[p]['sao'] = star_native[orig_p - 1]
        cung_data[p]['thien'] = dia_ban[orig_p]

    # --- 3. MÔN BÀN (Bát Môn Phi Cung - Nhảy số 5) ---
    eff_base_door = ji_palace if base_star_p == 5 else base_star_p
    steps = (dia_chi.index(chi_gio) - dia_chi.index(chi_tuan)) % 12
    
    path_9_door = luoshu_9 if loai == "阳" else list(reversed(luoshu_9))
    idx_eff_base = path_9_door.index(eff_base_door)
    idx_door_target = (idx_eff_base + steps) % 9
    door_target_p = path_9_door[idx_door_target]
    
    # Bẻ lái Trực Sử nếu rơi vào Cung 5
    if door_target_p == 5:
        door_target_p = ji_palace

    idx_truc_su_mon = luoshu_8.index(eff_base_door)
    path_8 = luoshu_8 if loai == "阳" else list(reversed(luoshu_8))
    idx_target_in_path8 = path_8.index(door_target_p)
    
    for i in range(8):
        p = path_8[i]
        offset = (i - idx_target_in_path8) % 8
        orig_gate_idx = (idx_truc_su_mon + offset) % 8 if loai == "阳" else (idx_truc_su_mon - offset) % 8
        cung_data[p]['mon'] = gate_native[orig_gate_idx]

    # --- 4. CỬU THẦN BÀN (9 Thần Phi Cung Tiến/Lùi theo Âm Dương) ---
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
# 4. GIAO DIỆN LƯỚI & FORMAT CSS SẠCH SẼ
# ==========================================
def format_stem(stem_str, p):
    if not stem_str: return ""
    parts = stem_str.split('/')
    res = []
    for can in parts:
        # Vẫn giữ logic ngầm ở đây để nếu sau này cần bắt sự kiện thì có sẵn
        is_tomb = p in stem_tomb.get(can, [])
        is_punish = p == stem_punish.get(can, -1)
        # Chỉ in ra text thuần, màu cơ bản
        res.append(f"<span>{can}</span>")
    return "<span style='margin: 0 2px;'>/</span>".join(res)

def format_door(door_str, p):
    if not door_str: return ""
    # Giữ logic ngầm môn bức
    khac = {"木":"土", "土":"水", "水":"火", "火":"金", "金":"木"}
    is_buc = khac.get(door_elements.get(door_str, "")) == palace_elements.get(p, "")
    # Text thuần
    return f"<span>{door_str}</span>"

def format_sao(sao_str):
    if not sao_str: return ""
    return sao_str.replace('/', "<span style='margin: 0 2px;'>/</span>")

def render_html_table(cung_data, tk_gio):
    luoi_lac_thu = [[4, 9, 2], [3, 5, 7], [8, 1, 6]]

    html = """
    <style>
        .qmdj-table { border-collapse: collapse; width: 100%; max-width: 480px; min-width: 320px; height: 380px; table-layout: fixed; font-family: sans-serif; margin: 0 auto; background: #fff;}
        .qmdj-td { border: 1px solid #aaa; width: 33.33%; position: relative; vertical-align: top; padding: 6px; }
        
        /* Cấu trúc Lưới 2 cột để căn lề tuyệt đối */
        .cell-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            grid-template-rows: 1fr 1fr 1fr;
            height: 100%;
            min-height: 85px;
            align-items: center;
            color: #222;
        }
        
        /* Cột trái (Thần, Tinh, Môn) căn giữa nội bộ cột */
        .item-than { grid-column: 1; grid-row: 1; font-size: 15px; font-weight: 300; text-align: center; }
        .item-sao  { grid-column: 1; grid-row: 2; font-size: 15px; font-weight: 300; text-align: center; }
        .item-mon  { grid-column: 1; grid-row: 3; font-size: 15px; font-weight: 300; text-align: center; }
        
        /* Cột phải (Can Thiên, Can Địa) căn giữa nội bộ cột, nhường Row 1 cho Mã/Không Vong */
        .item-thien { grid-column: 2; grid-row: 2; font-size: 15px; font-weight: 300; text-align: center; }
        .item-dia   { grid-column: 2; grid-row: 3; font-size: 15px; font-weight: 300; text-align: center; }
        
        /* Ký hiệu Mã và Không Vong giữ nguyên trên cùng góc phải */
        .top-right-indicators { position: absolute; top: 4px; right: 4px; display: flex; flex-direction: row; align-items: center; justify-content: flex-end; gap: 4px; color: #555; }
        .horse-icon { font-size: 14px; font-weight: 600; }
        .void-icon { font-size: 22px; font-weight: normal; line-height: 0.8; margin-top: -2px; }
    </style>
    <table class="qmdj-table">
    """

    for row in luoi_lac_thu:
        html += "<tr>"
        for p in row:
            d = cung_data[p]
            
            indicators = []
            if d.get('ngua'): indicators.append("<span class='horse-icon'>马</span>")
            if p in tk_gio: indicators.append("<span class='void-icon'>○</span>")
            indicator_html = f"<div class='top-right-indicators'>{''.join(indicators)}</div>" if indicators else ""
            
            # Nếu là Cung 5 thì Môn bỏ trống (Phi Bàn)
            mon_html = format_door(d['mon'], p) if p != 5 else ""
            
            html += f"""
            <td class="qmdj-td">
                {indicator_html}
                <div class="cell-grid">
                    <div class="item-than">{d['than']}</div>
                    <div class="item-sao">{format_sao(d['sao'])}</div>
                    <div class="item-mon">{mon_html}</div>
                    
                    <div class="item-thien">{format_stem(d['thien'], p)}</div>
                    <div class="item-dia">{format_stem(d['dia'], p)}</div>
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
    selected_date = st.date_input("Ngày", st.session_state.init_dt.date())
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

bazi_dict = {
    'nam': thien_can[day_obj.getYearGZ().tg] + dia_chi[day_obj.getYearGZ().dz],
    'thang': thien_can[day_obj.getMonthGZ().tg] + dia_chi[day_obj.getMonthGZ().dz],
    'ngay': thien_can[day_obj.getDayGZ().tg] + dia_chi[day_obj.getDayGZ().dz]
}

don, cuc, jq_name, ji_palace, is_nhuan = get_zhirun_ju(actual_date)

nhuan_str = " - 闰奇" if is_nhuan else ""
chuoi_cuc = f"飞盘 (Phi Bàn) | {jq_name}{nhuan_str} - {don}{cuc}局 | 寄宫: {ji_palace}"
bazi_chuoi = f"{bazi_dict['nam']}年 {bazi_dict['thang']}月 {bazi_dict['ngay']}日 {hoa_giap_hien_tai}时"

tk_gio = tinh_tuan_khong_gio(hoa_giap_hien_tai)
data = lap_que(hoa_giap_hien_tai, don, cuc, ji_palace)

title = f"<h3 style='margin-bottom:6px; font-family:sans-serif; color: #111; font-weight: 400; font-size: 18px; text-align: center;'>{bazi_chuoi}</h3>"
sub_title = f"<h4 style='margin-top:0px; margin-bottom:15px; font-family:sans-serif; color: #555; font-weight: 300; font-size: 15px; text-align: center;'>{chuoi_cuc}</h4>"

qimen_board_html = render_html_table(data, tk_gio)

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
