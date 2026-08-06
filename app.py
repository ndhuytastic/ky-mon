import streamlit as st
import sxtwl
from datetime import datetime, timedelta, timezone
import warnings

warnings.filterwarnings('ignore')

st.set_page_config(page_title="Kỳ Môn Độn Giáp - Tiết Đặng Lâm", layout="wide", initial_sidebar_state="collapsed")

# ==========================================
# 1. HỆ THỐNG DỮ LIỆU CƠ BẢN
# ==========================================
thien_can = "甲乙丙丁戊己庚辛壬癸"
dia_chi = "子丑寅卯辰巳午未申酉戌亥"

luc_nghi = ["戊", "己", "庚", "辛", "壬", "癸", "丁", "丙", "乙"]
ring_8 = [1, 8, 3, 4, 9, 2, 7, 6]
star_ring = ["天蓬", "天任", "天冲", "天辅", "天英", "天芮", "天柱", "天心"]
door_ring = ["休门", "生门", "伤门", "杜门", "景门", "死门", "惊门", "开门"]
shen_yang = ["值符", "螣蛇", "太阴", "六合", "勾陈", "朱雀", "九地", "九天"]
shen_yin = ["值符", "螣蛇", "太阴", "六合", "白虎", "玄武", "九地", "九天"]

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

door_elements = {"休门": "水", "生门": "土", "伤门": "木", "杜门": "木", "景门": "火", "死门": "土", "惊门": "金", "开门": "金"}
palace_elements = {1: "水", 2: "土", 3: "木", 4: "木", 5: "土", 6: "金", 7: "金", 8: "土", 9: "火"}

stem_tomb = {"辛": [4], "壬": [4], "丁": [8], "己": [8], "庚": [8], "癸": [2], "乙": [2, 6], "丙": [6], "戊": [6]}
stem_punish = {"戊": 3, "己": 2, "庚": 8, "辛": 9, "壬": 4, "癸": 4}

# ==========================================
# 2. THUẬT TOÁN ĐỊNH CỤC TRÍ NHUẬN CHUẨN XÁC
# ==========================================
def get_zhirun_ju(actual_date):
    """
    Quét ngược về Đông Chí của năm trước để mô phỏng và ánh xạ vòng lặp Phù Đầu.
    Tự động tính diff_days, áp dụng Trí Nhuận 30 ngày (lặp lại Tiết Khí) 
    CHỈ tại Mang Chủng hoặc Đại Tuyết nếu diff_days >= 9.
    """
    # BẢN VÁ LỖI: Đồng bộ hóa actual_date (kiểu date) về actual_dt (kiểu datetime)
    actual_dt = datetime.combine(actual_date, datetime.min.time())
    start_date = datetime(actual_date.year - 1, 11, 1)
    
    jieqis = []
    curr = start_date
    # Dùng actual_dt thay vì actual_date để tránh ValueError/TypeError
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
    
    # Tìm Phù Đầu Thượng Nguyên gần Đông Chí nhất
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
                
    # Duyệt tiến theo chu kỳ 15 ngày để gán Tiết Khí
    current_tn_ft = best_tn_ft
    jq_idx = dz_idx
    periods = []
    
    while current_tn_ft <= actual_dt + timedelta(days=15):
        jq_name = jieqis[jq_idx]['name']
        jq_dt = jieqis[jq_idx]['dt']
        
        diff_days = (jq_dt - current_tn_ft).days
        
        periods.append({
            'start': current_tn_ft,
            'end': current_tn_ft + timedelta(days=15),
            'jq': jq_name
        })
        
        # LOGIC TRÍ NHUẬN CHUẨN: Chỉ Nhuận ở Mang Chủng / Đại Tuyết nếu Siêu Thần >= 9 ngày
        if diff_days >= 9 and jq_name in ["芒种", "大雪"]:
            current_tn_ft += timedelta(days=15)
            periods.append({
                'start': current_tn_ft,
                'end': current_tn_ft + timedelta(days=15),
                'jq': jq_name + " (Nhuận)"
            })
            jq_idx += 1 
            current_tn_ft += timedelta(days=15)
        else:
            jq_idx += 1
            current_tn_ft += timedelta(days=15)
            
    # Tra cứu ngày hiện tại nằm trong chu kỳ nào
    active_period = None
    for p in periods:
        if p['start'] <= actual_dt < p['end']:
            active_period = p
            break
            
    active_jq = active_period['jq'].replace(" (Nhuận)", "")
    
    # Tính Nguyên (Thượng/Trung/Hạ) cho ngày hiện tại
    d = sxtwl.fromSolar(actual_date.year, actual_date.month, actual_date.day)
    offset = d.getDayGZ().tg % 5
    ft_date = actual_date - timedelta(days=offset)
    ft_d = sxtwl.fromSolar(ft_date.year, ft_date.month, ft_date.day)
    
    if ft_d.getDayGZ().dz in [0, 6, 3, 9]: yuan = 0
    elif ft_d.getDayGZ().dz in [2, 8, 5, 11]: yuan = 1
    else: yuan = 2
    
    loai_don = "阳遁" if active_jq in yang_terms else "阴遁"
    so_cuc = solar_term_ju[active_jq][yuan]
    
    # Cung Ký Gửi theo Tiết Khí
    ji_palace = JIEQI_PALACE_MAP[active_jq]
    
    # Trả về cả cờ Nhuận để hiển thị UI nếu cần
    is_nhuan = " (Nhuận)" in active_period['jq']
    
    return loai_don, so_cuc, active_jq, ji_palace, is_nhuan

# ==========================================
# 3. THUẬT TOÁN KÝ CUNG & XOAY BÀN LỤC NHÂM
# ==========================================
def lap_que(hoa_giap_gio, loai_don, so_cuc, ji_palace):
    can_gio, chi_gio = hoa_giap_gio[0], hoa_giap_gio[1]
    loai = "阳" if loai_don == "阳遁" else "阴"
    
    idx_can, idx_chi = thien_can.index(can_gio), dia_chi.index(chi_gio)
    chi_tuan = dia_chi[(idx_chi - idx_can) % 12]
    can_tuan = {"子":"戊", "戌":"己", "申":"庚", "午":"辛", "辰":"壬", "寅":"癸"}[chi_tuan]

    # --- 1. ĐỊA BÀN ---
    dia_ban = {((so_cuc + i) % 9 or 9 if loai == "阳" else (so_cuc - i) % 9 or 9): can for i, can in enumerate(luc_nghi)}
    cung_goc_xun = [c for c, can in dia_ban.items() if can == can_tuan][0]
    
    # Xử lý Cung Khởi Trị Phù / Trị Sứ
    eff_base = ji_palace if cung_goc_xun == 5 else cung_goc_xun
    idx_base = ring_8.index(eff_base)

    # Nơi Trị Phù bay tới
    target_palace = [c for c, can in dia_ban.items() if can == (can_tuan if can_gio == "甲" else can_gio)][0]
    if target_palace == 5:
        target_palace = ji_palace
        
    idx_target = ring_8.index(target_palace)
    
    # Mã 
    map_ngua = {"子":"寅", "丑":"亥", "寅":"申", "卯":"巳", "辰":"寅", "巳":"亥", "午":"申", "未":"巳", "申":"寅", "酉":"亥", "戌":"申", "亥":"巳"}
    vi_tri_ngua = {"寅":8, "巳":4, "申":2, "亥":6}[map_ngua[chi_gio]]

    cung_data = {i: {'dia': '', 'sao': '', 'mon': '', 'than': '', 'thien': '', 'ngua': ''} for i in range(1, 10)}
    cung_data[vi_tri_ngua]['ngua'] = "马"
    
    for i in range(1, 10):
        if i == ji_palace:
            cung_data[i]['dia'] = f"{dia_ban[i]}/{dia_ban[5]}"
        else:
            cung_data[i]['dia'] = dia_ban.get(i, "")

    # --- 2. THIÊN BÀN (TINH & CAN) ---
    star_shift = (idx_target - idx_base) % 8
    
    for i in range(8):
        p = ring_8[i]
        orig_idx = (i - star_shift) % 8
        orig_p = ring_8[orig_idx]
        
        sao = star_ring[orig_idx]
        thien = dia_ban[orig_p]
        
        # Nếu đây là sao gốc của Ji_Palace, nó mang theo Thiên Cầm và Can Cung 5
        if orig_p == ji_palace:
            sao = f"{sao}/天禽"
            thien = f"{thien}/{dia_ban[5]}"
            
        cung_data[p]['sao'] = sao
        cung_data[p]['thien'] = thien

    # --- 3. MÔN BÀN (TRỊ SỨ) ---
    steps = (dia_chi.index(chi_gio) - dia_chi.index(chi_tuan)) % 12
    door_target = (eff_base + steps) % 9 or 9 if loai == "阳" else (eff_base - steps) % 9 or 9
    
    # Thuật toán chuyển hướng nếu Môn rơi vào Cung 5
    if door_target == 5:
        door_target = ji_palace
        
    idx_door_target = ring_8.index(door_target)
    door_shift = (idx_door_target - idx_base) % 8
    
    for i in range(8):
        p = ring_8[i]
        orig_idx = (i - door_shift) % 8
        cung_data[p]['mon'] = door_ring[orig_idx]

    # --- 4. THẦN BÀN ---
    for i in range(8):
        p = ring_8[i]
        if loai == "阳": deity_idx = (i - idx_target) % 8
        else: deity_idx = (idx_target - i) % 8
        cung_data[p]['than'] = shen_yang[deity_idx] if loai == "阳" else shen_yin[deity_idx]

    return cung_data

def tinh_tuan_khong_gio(hoa_giap):
    idx_can, idx_chi = thien_can.index(hoa_giap[0]), dia_chi.index(hoa_giap[1])
    idx_tuan_dau = (idx_chi - idx_can) % 12
    chi_to_cung = {"子":1, "丑":8, "寅":8, "卯":3, "辰":4, "巳":4, "午":9, "未":2, "申":2, "酉":7, "戌":6, "亥":6}
    return [chi_to_cung[dia_chi[(idx_tuan_dau - 2) % 12]], chi_to_cung[dia_chi[(idx_tuan_dau - 1) % 12]]]

# ==========================================
# 4. GIAO DIỆN & STYLE FORMATTER
# ==========================================
def format_stem(stem_str, p):
    if not stem_str: return ""
    parts = stem_str.split('/')
    res = []
    for can in parts:
        color = "#666"
        fw = "300"
        if p in stem_tomb.get(can, []): color = "#b8860b" # Nhập mộ - Vàng Nâu
        elif p == stem_punish.get(can, -1): color = "#800080" # Kích hình - Tím
        res.append(f"<span style='color: {color}; font-weight: {fw};'>{can}</span>")
    return "<span style='color:#ccc; font-weight: 300;'>/</span>".join(res)

def format_door(door_str, p):
    if not door_str: return ""
    khac = {"木":"土", "土":"水", "水":"火", "火":"金", "金":"木"}
    d_el = door_elements.get(door_str, "")
    p_el = palace_elements.get(p, "")
    if khac.get(d_el) == p_el: # Cửa khắc cung
        return f"<span style='color: #111; font-weight: bold;'>{door_str}</span>"
    return f"<span style='color: #666; font-weight: 300;'>{door_str}</span>"

def render_html_table(cung_data, tk_gio):
    luoi_lac_thu = [[4, 9, 2], [3, 5, 7], [8, 1, 6]]

    html = """
    <style>
        .qmdj-table { border-collapse: collapse; width: 100%; max-width: 480px; min-width: 320px; height: 380px; table-layout: fixed; font-size: 16px; font-family: sans-serif; margin: 0 auto; background: #fff;}
        .qmdj-td { border: 1px solid #ddd; width: 33.33%; position: relative; vertical-align: top; padding: 6px; }
        .cell-content { display: flex; flex-direction: column; justify-content: space-between; height: 100%; min-height: 95px; }
        .top-row { display: flex; justify-content: space-between; align-items: flex-start; }
        .bot-row { display: flex; justify-content: space-between; align-items: flex-end; }
        .light-text { color: #666; font-weight: 300; }
        .right-align { text-align: right; line-height: 1.3; }
        .horse { position: absolute; top: 3px; right: 40px; font-size: 12px; color: #666; }
        .void { position: absolute; top: 3px; right: 26px; font-size: 12px; font-weight: bold; color: #666;}
        .center-palace { position: absolute; bottom: 6px; right: 6px; font-size: 16px; }
    </style>
    <table class="qmdj-table">
    """

    for row in luoi_lac_thu:
        html += "<tr>"
        for p in row:
            d = cung_data[p]
            if p == 5:
                html += f"""<td class="qmdj-td"><div class="center-palace">{format_stem(d['dia'], p)}</div></td>"""
                continue
                
            horse_html = f'<div class="horse">{d["ngua"]}</div>' if d['ngua'] else ""
            void_html = '<div class="void">○</div>' if p in tk_gio else ""
            
            sao_thien_html = f"{d['sao']}<br>{format_stem(d['thien'], p)}" if d['sao'] else ""

            html += f"""
            <td class="qmdj-td">
                {horse_html}{void_html}
                <div class="cell-content">
                    <div class="top-row">
                        <span class="light-text">{d['than']}</span>
                        <span class="light-text right-align">{sao_thien_html}</span>
                    </div>
                    <div class="bot-row">
                        <span>{format_door(d['mon'], p)}</span>
                        <span>{format_stem(d['dia'], p)}</span>
                    </div>
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

# Lấy thông số từ Thuật toán Trí Nhuận & Ký Cung
don, cuc, jq_name, ji_palace, is_nhuan = get_zhirun_ju(actual_date)

nhuan_str = " - 闰奇" if is_nhuan else ""
chuoi_cuc = f"置闰 | {jq_name}{nhuan_str} - {don}{cuc}局 | 寄宫: {ji_palace}"
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
