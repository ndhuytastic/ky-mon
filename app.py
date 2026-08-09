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
# 2. THUẬT TOÁN ĐỊNH CỤC TRÍ NHUẬN CHUẨN XÁC (PHIÊN BẢN TOÁN HỌC PHÙ ĐẦU)
# ==========================================
def get_zhirun_ju(actual_date):
    actual_dt = datetime.combine(actual_date, datetime.min.time())
    d = sxtwl.fromSolar(actual_date.year, actual_date.month, actual_date.day)
    
    # 1. Định vị ngày Phù Đầu Thượng Nguyên (Giáp/Kỷ + Tý/Ngọ/Mão/Dậu)
    curr_d = d
    offset = 0
    while True:
        tg = curr_d.getDayGZ().tg
        dz = curr_d.getDayGZ().dz
        if tg in [0, 5] and dz in [0, 6, 3, 9]:
            break
        offset += 1
        prev_date = actual_dt - timedelta(days=offset)
        curr_d = sxtwl.fromSolar(prev_date.year, prev_date.month, prev_date.day)
        
    futou_date = actual_dt - timedelta(days=offset)
    yuan = offset // 5  # 0: Thượng Ngươn, 1: Trung Ngươn, 2: Hạ Ngươn
    
    # 2. Quét các Tiết Khí thiên văn xung quanh Phù Đầu
    jieqis = []
    start_scan = futou_date - timedelta(days=25)
    for i in range(50):
        check_dt = start_scan + timedelta(days=i)
        cd = sxtwl.fromSolar(check_dt.year, check_dt.month, check_dt.day)
        if cd.hasJieQi():
            jieqis.append({
                'name': jq_names[cd.getJieQi()],
                'dt': check_dt
            })
            
    # Lọc tiết khí gần nhất với Phù Đầu theo tự nhiên
    active_jq = None
    is_nhuan = False
    min_diff = 999
    
    for jq in jieqis:
        diff = (jq['dt'] - futou_date).days
        if abs(diff) < min_diff:
            min_diff = abs(diff)
            active_jq = jq['name']
            
    # 3. Kích hoạt Trí Nhuận (Chao Shen >= 9 ngày tại Mang Chủng / Đại Tuyết)
    next_jqs = [jq for jq in jieqis if jq['dt'] >= futou_date]
    if next_jqs:
        closest_next_jq = next_jqs[0]
        chao_shen_days = (closest_next_jq['dt'] - futou_date).days
        
        # Nếu Siêu Thần chạm mốc >= 9 ngày trước thềm Hạ Chí hoặc Đông Chí
        if chao_shen_days >= 9 and closest_next_jq['name'] in ["夏至", "冬至"]:
            is_nhuan = True
            # Ép Nhuận: Lặp lại Mang Chủng (trước Hạ Chí) hoặc Đại Tuyết (trước Đông Chí)
            active_jq = "芒种" if closest_next_jq['name'] == "夏至" else "大雪"
                
    # 4. Trích xuất Cục Số
    loai_don = "阳遁" if active_jq in yang_terms else "阴遁"
    so_cuc = solar_term_ju[active_jq][yuan]
    ji_palace = JIEQI_PALACE_MAP[active_jq]
    
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

    # --- 2. THIÊN BÀN TÌNH & CAN (Bay 9 cung) ---
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

    # --- 3. BÁT MÔN PHI BÀN  ---
    door_native_dict = {1: "休门", 2: "死门", 3: "伤门", 4: "杜门", 6: "开门", 7: "惊门", 8: "生门", 9: "景门"}
    doors_cycle = ["休门", "死门", "伤门", "杜门", "开门", "惊门", "生门", "景门"]
    luoshu_8 = [1, 2, 3, 4, 6, 7, 8, 9]

    # Tìm Cửa Trực Sử gốc
    if base_star_p == 5:
        truc_su_door = door_native_dict[ji_palace]
    else:
        truc_su_door = door_native_dict[base_star_p]

    # Tính cung đích của Trực Sử (Bắt đầu từ Cục số)
    steps = (dia_chi.index(chi_gio) - dia_chi.index(chi_tuan)) % 12
    if loai == "阳":
        target_door_p = (so_cuc + steps - 1) % 9 + 1
    else:
        target_door_p = (so_cuc - steps - 1) % 9 + 1
        
    # Ngoại lệ: Nếu bay đụng 5 -> Hạ cánh xuống Cung Ký Gửi
    if target_door_p == 5:
        target_door_p = ji_palace
        
    # Rải 8 cửa bám theo Lạc Thư
    idx_target_in_path8 = luoshu_8.index(target_door_p)
    shifted_palaces = luoshu_8[idx_target_in_path8:] + luoshu_8[:idx_target_in_path8]
    
    idx_truc_su = doors_cycle.index(truc_su_door)
    shifted_doors = doors_cycle[idx_truc_su:] + doors_cycle[:idx_truc_su]
    
    for p, door in zip(shifted_palaces, shifted_doors):
        cung_data[p]['mon'] = door

    # --- 4. CỬU THẦN (9 Thần Phi Cung) ---
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
# 4. GIAO DIỆN LƯỚI CSS SẠCH SẼ (CHỪA KHOẢNG TRỐNG)
# ==========================================
def format_stem(stem_str):
    if not stem_str: return ""
    return stem_str.replace('/', "<span style='margin: 0 4px;'>/</span>")

def format_sao(sao_str):
    if not sao_str: return ""
    return sao_str.replace('/', "<span style='margin: 0 4px;'>/</span>")

def render_html_table(cung_data, tk_gio):
    luoi_lac_thu = [[4, 9, 2], [3, 5, 7], [8, 1, 6]]

    html = """
    <style>
        .qmdj-table { border-collapse: collapse; width: 100%; max-width: 550px; min-width: 320px; height: 380px; table-layout: fixed; font-family: sans-serif; margin: 0 auto; background: #fff;}
        .qmdj-td { border: 1px solid #aaa; width: 33.33%; position: relative; vertical-align: top; padding: 10px; }
        
        /* Cấu trúc Grid 2 cột: Cột trái chứa nội dung, Cột phải để trống cho Cát Hung Cách */
        .cell-main {
            display: grid;
            grid-template-columns: auto auto 1fr; /* 3 Cột: Tinh/Môn | Can | Trống */
            grid-template-rows: 22px 22px 22px;   /* 3 Dòng cố định chiều cao */
            column-gap: 15px; /* Cột Can lùi ra một chút để phân biệt */
            row-gap: 6px;
            height: 100%;
            min-height: 85px;
            align-content: start;
            margin-top: 5px;
            margin-left: 5px; /* Đẩy hơi lùi vào một chút */
        }
        
        /* Căn ngang hàng chính xác */
        .item-than  { grid-column: 1 / span 2; grid-row: 1; font-size: 15px; color: #222; text-align: left; }
        .item-tinh  { grid-column: 1; grid-row: 2; font-size: 15px; color: #222; text-align: left; }
        .item-mon   { grid-column: 1; grid-row: 3; font-size: 15px; color: #222; text-align: left; }
        
        .item-thien { grid-column: 2; grid-row: 2; font-size: 15px; color: #222; text-align: left; }
        .item-dia   { grid-column: 2; grid-row: 3; font-size: 15px; color: #222; text-align: left; }

        /* Trung Cung 5 chỉ hiển thị 2 Can */
        .center-5 {
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            height: 100%;
            min-height: 85px;
            font-size: 16px;
            color: #222;
            gap: 6px;
        }

        .top-right-indicators { position: absolute; top: 3px; right: 4px; display: flex; flex-direction: row; align-items: center; justify-content: flex-end; gap: 4px; color: #444; }
        .horse-icon { font-size: 14px; font-weight: bold; }
        .void-icon { font-size: 20px; font-weight: normal; line-height: 0.8; margin-top: -2px; }
    </style>
    <table class="qmdj-table">
    """

    for row in luoi_lac_thu:
        html += "<tr>"
        for p in row:
            d = cung_data[p]
            
            if p == 5:
                html += f"""
                <td class="qmdj-td">
                    <div class="center-5">
                        <span>{format_stem(d['thien'])}</span>
                        <span>{format_stem(d['dia'])}</span>
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
                <div class="cell-main">
                    <div class="item-than">{d['than']}</div>
                    <div class="item-tinh">{format_sao(d['sao'])}</div>
                    <div class="item-mon"><span>{d['mon']}</span></div>
                    
                    <div class="item-thien">{format_stem(d['thien'])}</div>
                    <div class="item-dia">{format_stem(d['dia'])}</div>
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

bazi_dict = {
    'nam': thien_can[day_obj.getYearGZ().tg] + dia_chi[day_obj.getYearGZ().dz],
    'thang': thien_can[day_obj.getMonthGZ().tg] + dia_chi[day_obj.getMonthGZ().dz],
    'ngay': thien_can[day_obj.getDayGZ().tg] + dia_chi[day_obj.getDayGZ().dz]
}

don, cuc, jq_name, ji_palace, is_nhuan = get_zhirun_ju(actual_date)

nhuan_str = " - 闰奇" if is_nhuan else ""
chuoi_cuc = f"飞盘 | {jq_name}{nhuan_str} - {don}{cuc}局 | 寄宫: {ji_palace}"
bazi_chuoi = f"{bazi_dict['nam']}年 {bazi_dict['thang']}月 {bazi_dict['ngay']}日 {hoa_giap_hien_tai}时"

tk_gio = tinh_tuan_khong_gio(hoa_giap_hien_tai)
data = lap_que(hoa_giap_hien_tai, don, cuc, ji_palace)

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
