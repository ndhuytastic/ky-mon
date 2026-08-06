import streamlit as st
import sxtwl
from datetime import datetime, timedelta, timezone
import warnings

warnings.filterwarnings('ignore')

st.set_page_config(page_title="Kỳ Môn Độn Giáp - Trí Nhuận", layout="wide", initial_sidebar_state="collapsed")

# ==========================================
# 1. DỮ LIỆU CƠ BẢN
# ==========================================
thien_can = "甲乙丙丁戊己庚辛壬癸"
dia_chi = "子丑寅卯辰巳午未申酉戌亥"

luc_nghi = ["戊", "己", "庚", "辛", "壬", "癸", "丁", "丙", "乙"]
ring_8 = [1, 8, 3, 4, 9, 2, 7, 6]
star_ring = ["天蓬", "天任", "天冲", "天辅", "天英", "天芮", "天柱", "天心"]
door_ring = ["休门", "生门", "伤门", "杜门", "景门", "死门", "惊门", "开门"]
shen_yang = ["值符", "螣蛇", "太阴", "六合", "勾陈", "朱雀", "九地", "九天"]
shen_yin = ["值符", "螣蛇", "太阴", "六合", "白虎", "玄武", "九地", "九天"]

solar_term_ju = {
    "冬至":[1,7,4], "小寒":[2,8,5], "大寒":[3,9,6], "立春":[8,5,2], "雨水":[9,6,3], "惊蛰":[1,7,4],
    "春分":[3,9,6], "清明":[4,1,7], "谷雨":[5,2,8], "立夏":[4,1,7], "小满":[5,2,8], "芒种":[6,3,9],
    "夏至":[9,3,6], "小暑":[8,2,5], "大暑":[7,1,4], "立秋":[2,5,8], "处暑":[1,4,7], "白露":[9,3,6],
    "秋分":[7,1,4], "寒露":[6,9,3], "霜降":[5,8,2], "立冬":[6,9,3], "小雪":[5,8,2], "大雪":[4,7,1]
}
yang_terms = ["冬至", "小寒", "大寒", "立春", "雨水", "惊蛰", "春分", "清明", "谷雨", "立夏", "小满", "芒种"]
jq_names = ["冬至", "小寒", "大寒", "立春", "雨水", "惊蛰", "春分", "清明", "谷雨", "立夏", "小满", "芒种", "夏至", "小暑", "大暑", "立秋", "处暑", "白露", "秋分", "寒露", "霜降", "立冬", "小雪", "大雪"]

chi_to_cung = {"子":1, "丑":8, "寅":8, "卯":3, "辰":4, "巳":4, "午":9, "未":2, "申":2, "酉":7, "戌":6, "亥":6}

# ==========================================
# 2. LOGIC TÍNH TOÁN TRÍ NHUẬN
# ==========================================
def get_zhirun_term_and_cuc(actual_date):
    """
    Thuật toán Trí Nhuận:
    1. Tìm ngày Phù Đầu (chứa can Giáp hoặc Kỷ).
    2. Xác định Thượng/Trung/Hạ Nguyên dựa vào Chi của ngày Phù Đầu.
    3. Tìm Tiết Khí gần với ngày Phù Đầu nhất để định Cục.
    """
    day_obj = sxtwl.fromSolar(actual_date.year, actual_date.month, actual_date.day)
    offset = day_obj.getDayGZ().tg % 5
    
    # Tìm ngày Phù Đầu
    ft_date = actual_date - timedelta(days=offset)
    ft_day_obj = sxtwl.fromSolar(ft_date.year, ft_date.month, ft_date.day)
    ft_dz = ft_day_obj.getDayGZ().dz
    
    # Xác định Nguyên (Thượng, Trung, Hạ)
    if ft_dz in [0, 6, 3, 9]: yuan = 0    # Tý, Ngọ, Mão, Dậu -> Thượng
    elif ft_dz in [2, 8, 5, 11]: yuan = 1 # Dần, Thân, Tỵ, Hợi -> Trung
    else: yuan = 2                        # Thìn, Tuất, Sửu, Mùi -> Hạ
    
    # Tìm Tiết Khí gần Phù Đầu nhất (Quét trong khoảng ±9 ngày)
    best_jq = None
    min_diff = 999
    
    for i in range(-9, 10):
        check_date = ft_date + timedelta(days=i)
        check_obj = sxtwl.fromSolar(check_date.year, check_date.month, check_date.day)
        if check_obj.hasJieQi():
            dist = abs(i)
            if dist < min_diff:
                min_diff = dist
                best_jq = jq_names[check_obj.getJieQi()]
                
    loai_don = "阳遁" if best_jq in yang_terms else "阴遁"
    so_cuc = solar_term_ju[best_jq][yuan]
    return loai_don, so_cuc, best_jq

def tinh_tuan_khong(hoa_giap):
    idx_can, idx_chi = thien_can.index(hoa_giap[0]), dia_chi.index(hoa_giap[1])
    idx_tuan_dau = (idx_chi - idx_can) % 12
    return [dia_chi[(idx_tuan_dau - 2) % 12], dia_chi[(idx_tuan_dau - 1) % 12]]

# ==========================================
# 3. LẬP QUẺ KỲ MÔN
# ==========================================
def lap_que(hoa_giap_gio, loai_don, so_cuc):
    can_gio, chi_gio = hoa_giap_gio[0], hoa_giap_gio[1]
    loai = "阳" if loai_don == "阳遁" else "阴"
    
    idx_can, idx_chi = thien_can.index(can_gio), dia_chi.index(chi_gio)
    chi_tuan = dia_chi[(idx_chi - idx_can) % 12]
    can_tuan = {"子":"戊", "戌":"己", "申":"庚", "午":"辛", "辰":"壬", "寅":"癸"}[chi_tuan]

    # Địa bàn
    dia_ban = {((so_cuc + i) % 9 or 9 if loai == "阳" else (so_cuc - i) % 9 or 9): can for i, can in enumerate(luc_nghi)}
    cung_goc = [c for c, can in dia_ban.items() if can == can_tuan][0]

    cg_ring = 2 if cung_goc == 5 else cung_goc
    cg_idx = ring_8.index(cg_ring)
    
    # Tìm Trực Phù, Trực Sử
    can_tim_kiem = can_tuan if can_gio == "甲" else can_gio
    target_star = [c for c, can in dia_ban.items() if can == can_tim_kiem][0]
    if target_star == 5: target_star = 2
    ts_idx = ring_8.index(target_star)

    steps = (dia_chi.index(chi_gio) - dia_chi.index(chi_tuan)) % 12
    target_door = (cung_goc + steps) % 9 or 9 if loai == "阳" else (cung_goc - steps) % 9 or 9
    if target_door == 5: target_door = 2
    td_idx = ring_8.index(target_door)

    # Tìm Mã
    map_ngua = {"子":"寅", "丑":"亥", "寅":"申", "卯":"巳", "辰":"寅", "巳":"亥", "午":"申", "未":"巳", "申":"寅", "酉":"亥", "戌":"申", "亥":"巳"}
    vi_tri_ngua = {"寅":8, "巳":4, "申":2, "亥":6}[map_ngua[chi_gio]]

    # Khởi tạo data
    cung_data = {i: {'dia': '', 'sao': '', 'mon': '', 'than': '', 'thien': '', 'ngua': ''} for i in range(1, 10)}
    cung_data[vi_tri_ngua]['ngua'] = "马"

    for i in range(1, 10):
        if i == 2:
            cung_data[i]['dia'] = f"{dia_ban.get(2, '')}/{dia_ban.get(5, '')}"
        else:
            cung_data[i]['dia'] = dia_ban.get(i, "")

    # Xếp Thiên Bàn, Tinh, Môn, Thần
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

    return cung_data

# ==========================================
# 4. RENDER BẢNG GIAO DIỆN SẠCH
# ==========================================
def render_html_table(cung_data, tk_gio):
    luoi_lac_thu = [[4, 9, 2], [3, 5, 7], [8, 1, 6]]
    cung_tk_gio = [chi_to_cung[chi] for chi in tk_gio]

    html = """
    <style>
        .qmdj-table { border-collapse: collapse; width: 100%; max-width: 450px; min-width: 320px; height: 360px; table-layout: fixed; font-size: 16px; background-color: #ffffff; margin: 0 auto; font-family: sans-serif; color: #000; }
        .qmdj-td { border: 1px solid #333; width: 33.33%; padding: 10px 8px; position: relative; vertical-align: top; }
        .row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; line-height: 1.2; }
        .row-last { margin-bottom: 0; }
        .horse { position: absolute; top: 4px; right: 4px; font-size: 14px; }
        .void { position: absolute; top: 4px; right: 24px; font-size: 14px; font-weight: bold; }
        .center-palace { position: absolute; bottom: 10px; right: 10px; font-size: 18px; }
    </style>
    <table class="qmdj-table">
    """

    for row in luoi_lac_thu:
        html += "<tr>"
        for p in row:
            d = cung_data[p]
            horse_html = f'<div class="horse">{d["ngua"]}</div>' if d['ngua'] else ""
            void_html = '<div class="void">○</div>' if p in cung_tk_gio else ""

            if p == 5:
                html += f"""
                <td class="qmdj-td">
                    <div class="center-palace">{d['dia']}</div>
                </td>"""
            else:
                html += f"""
                <td class="qmdj-td">
                    {horse_html}
                    {void_html}
                    <div class="row">
                        <div>{d['than']}</div>
                    </div>
                    <div class="row">
                        <div>{d['sao']}</div>
                        <div>{d['thien']}</div>
                    </div>
                    <div class="row row-last">
                        <div>{d['mon']}</div>
                        <div>{d['dia']}</div>
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

# Chỉ chọn Thời gian
col1, col2 = st.columns(2)
with col1:
    selected_date = st.date_input("Ngày", st.session_state.init_dt.date())
with col2:
    selected_time = st.time_input("Giờ Phút", st.session_state.init_dt.time(), step=60)

user_dt = datetime.combine(selected_date, selected_time)

# Bù qua ngày mới nếu >= 23h (giờ Tý)
if user_dt.hour >= 23:
    actual_date = user_dt.date() + timedelta(days=1)
    chi_gio_idx = 0 
else:
    actual_date = user_dt.date()
    chi_gio_idx = (user_dt.hour + 1) // 2 % 12

chi_gio = dia_chi[chi_gio_idx]
day_obj = sxtwl.fromSolar(actual_date.year, actual_date.month, actual_date.day)

# Tính Bát tự
can_ngay_idx = day_obj.getDayGZ().tg
can_gio_idx = (can_ngay_idx % 5 * 2 + chi_gio_idx) % 10
can_gio_str = thien_can[can_gio_idx]
hoa_giap_hien_tai = can_gio_str + chi_gio

bazi_dict = {
    'nam': thien_can[day_obj.getYearGZ().tg] + dia_chi[day_obj.getYearGZ().dz],
    'thang': thien_can[day_obj.getMonthGZ().tg] + dia_chi[day_obj.getMonthGZ().dz],
    'ngay': thien_can[day_obj.getDayGZ().tg] + dia_chi[day_obj.getDayGZ().dz]
}

# Lấy Cục theo Trí Nhuận
don, cuc, jq_name = get_zhirun_term_and_cuc(actual_date)

chuoi_cuc = f"置闰 | {jq_name} - {don}{cuc}局"
bazi_chuoi = f"{bazi_dict['nam']}年 {bazi_dict['thang']}月 {bazi_dict['ngay']}日 {hoa_giap_hien_tai}时"

# Lập Quẻ
tk_gio = tinh_tuan_khong(hoa_giap_hien_tai)
data = lap_que(hoa_giap_hien_tai, don, cuc)

title = f"<h3 style='margin-bottom:6px; font-family:sans-serif; color: #000; font-weight: normal; font-size: 18px; text-align: center;'>{bazi_chuoi}</h3>"
sub_title = f"<h4 style='margin-top:0px; margin-bottom:15px; font-family:sans-serif; color: #333; font-weight: normal; font-size: 16px; text-align: center;'>{chuoi_cuc}</h4>"

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
