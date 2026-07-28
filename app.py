import streamlit as st
import sxtwl
from datetime import datetime, timedelta, timezone
import warnings

warnings.filterwarnings('ignore')

st.set_page_config(page_title="Kỳ Môn Độn Giáp", layout="wide", initial_sidebar_state="collapsed")

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

element_colors = {
    "木": "#007A00", "火": "#D90000", "土": "#996600", "金": "#555555", "水": "#0000CC"
}

stem_elements = {"甲": "木", "乙": "木", "丙": "火", "丁": "火", "戊": "土", "己": "土", "庚": "金", "辛": "金", "壬": "水", "癸": "水"}
door_elements = {"休门": "水", "生门": "土", "伤门": "木", "杜门": "木", "景门": "火", "死门": "土", "惊门": "金", "开门": "金"}
star_elements = {"天蓬": "水", "天任": "土", "天冲": "木", "天辅": "木", "天英": "火", "天芮": "土", "天禽": "土", "禽": "土", "天柱": "金", "天心": "金"}
deity_elements = {
    "值符": "木", "螣蛇": "火", "太阴": "金", "六合": "木", "勾陈": "土",
    "白虎": "金", "朱雀": "火", "玄武": "水", "九地": "土", "九天": "金"
}
palace_elements = {1: "水", 2: "土", 3: "木", 4: "木", 5: "土", 6: "金", 7: "金", 8: "土", 9: "火"}
branch_elements = {"亥": "水", "子": "水", "寅": "木", "卯": "木", "巳": "火", "午": "火", "申": "金", "酉": "金", "辰": "土", "戌": "土", "丑": "土", "未": "土"}

stem_punish = {"戊": 3, "己": 2, "庚": 8, "辛": 9, "壬": 4, "癸": 4}
stem_tomb = {"辛": [4], "壬": [4], "丁": [8], "己": [8], "庚": [8], "癸": [2], "乙": [2, 6], "丙": [6], "戊": [6]}

shijia_earth_branch_map = {
    "戊": "子", "己": "戌", "庚": "申", "辛": "午", "壬": "辰", 
    "癸": "寅", "丁": "卯", "丙": "寅", "乙": "丑"
}

solar_term_ju = {
    "冬至":[1,7,4], "小寒":[2,8,5], "大寒":[3,9,6], "立春":[8,5,2], "雨水":[9,6,3], "惊蛰":[1,7,4],
    "春分":[3,9,6], "清明":[4,1,7], "谷雨":[5,2,8], "立夏":[4,1,7], "小满":[5,2,8], "芒种":[6,3,9],
    "夏至":[9,3,6], "小暑":[8,2,5], "大暑":[7,1,4], "立秋":[2,5,8], "处暑":[1,4,7], "白露":[9,3,6],
    "秋分":[7,1,4], "寒露":[6,9,3], "霜降":[5,8,2], "立冬":[6,9,3], "小雪":[5,8,2], "大雪":[4,7,1]
}
yang_terms = ["冬至", "小寒", "大寒", "立春", "雨水", "惊蛰", "春分", "清明", "谷雨", "立夏", "小满", "芒种"]
jq_names = ["冬至", "小寒", "大寒", "立春", "雨水", "惊蛰", "春分", "清明", "谷雨", "立夏", "小满", "芒种", "夏至", "小暑", "大暑", "立秋", "处暑", "白露", "秋分", "寒露", "霜降", "立冬", "小雪", "大雪"]

cung_to_gua = {1: "坎", 2: "坤", 3: "震", 4: "巽", 5: "", 6: "乾", 7: "兑", 8: "艮", 9: "离"}
chi_to_cung = {"子":1, "丑":8, "寅":8, "卯":3, "辰":4, "巳":4, "午":9, "未":2, "申":2, "酉":7, "戌":6, "亥":6}
chi_to_hour = {"子":0, "丑":2, "寅":4, "卯":6, "辰":8, "巳":10, "午":12, "未":14, "申":16, "酉":18, "戌":20, "亥":22}
hour_ranges = ["23-1", "1-3", "3-5", "5-7", "7-9", "9-11", "11-13", "13-15", "15-17", "17-19", "19-21", "21-23"]
danh_sach_12_gio = [f"{dia_chi[i]} - {i+1} ({hour_ranges[i]})" for i in range(12)]

dun_ju_list = ["Mặc định"] + [f"阳{i}" for i in range(1, 10)] + [f"阴{i}" for i in range(1, 10)]
jiazi_grouped_list = ["Mặc định"]
for can in thien_can:
    for chi in dia_chi:
        if (thien_can.index(can) % 2) == (dia_chi.index(chi) % 2):
            jiazi_grouped_list.append(f"{can}{chi}")

term_to_season = {
    "立春": "Xuân", "雨水": "Xuân", "惊蛰": "Xuân", "春分": "Xuân", "清明": "Xuân", "谷雨": "Xuân",
    "立夏": "Hạ", "小满": "Hạ", "芒种": "Hạ", "夏至": "Hạ",
    "小暑": "Trường Hạ", "大暑": "Trường Hạ",
    "立秋": "Thu", "处暑": "Thu", "白露": "Thu", "秋分": "Thu", "寒露": "Thu", "霜降": "Thu",
    "立冬": "Đông", "小雪": "Đông", "大雪": "Đông", "冬至": "Đông", "小寒": "Đông", "大寒": "Đông"
}

season_elements = {"Xuân": "木", "Hạ": "火", "Trường Hạ": "土", "Thu": "金", "Đông": "水"}
khac_map = {"木": "土", "火": "金", "土": "水", "金": "木", "水": "火"}

palace_to_terms = {
    8: ["立春", "雨水", "惊蛰"],
    3: ["春分", "清明", "谷雨"],
    4: ["立夏", "小满", "芒种"],
    9: ["夏至", "小暑", "大暑"],
    2: ["立秋", "处暑", "白露"],
    7: ["秋分", "寒露", "霜降"],
    6: ["立冬", "小雪", "大雪"],
    1: ["冬至", "小寒", "大寒"]
}

entity_to_terms = {
    "休门": palace_to_terms[1], "天蓬": palace_to_terms[1],
    "生门": palace_to_terms[8], "天任": palace_to_terms[8],
    "伤门": palace_to_terms[3], "天冲": palace_to_terms[3],
    "杜门": palace_to_terms[4], "天辅": palace_to_terms[4],
    "景门": palace_to_terms[9], "天英": palace_to_terms[9],
    "死门": palace_to_terms[2], "天芮": palace_to_terms[2], "天禽": palace_to_terms[2], "禽": palace_to_terms[2],
    "惊门": palace_to_terms[7], "天柱": palace_to_terms[7],
    "开门": palace_to_terms[6], "天心": palace_to_terms[6]
}

# ==========================================
# 2. LOGIC TÍNH THIÊN VĂN & ĐỘN CỤC CHUẨN XÁC
# ==========================================
def get_yearly_terms(year):
    term_dates = {}
    curr_date = datetime(year, 1, 1)
    end_date = datetime(year + 1, 1, 31)
    all_terms = []
    
    prev_dz = datetime(year - 1, 12, 1)
    while prev_dz.year == year - 1:
        day_obj = sxtwl.fromSolar(prev_dz.year, prev_dz.month, prev_dz.day)
        if day_obj.hasJieQi() and jq_names[day_obj.getJieQi()] == "冬至":
            all_terms.append(("冬至", f"{prev_dz.day}/{prev_dz.month}"))
            break
        prev_dz += timedelta(days=1)

    while curr_date <= end_date:
        day_obj = sxtwl.fromSolar(curr_date.year, curr_date.month, curr_date.day)
        if day_obj.hasJieQi():
            jq_idx = day_obj.getJieQi()
            jq_name = jq_names[jq_idx]
            all_terms.append((jq_name, f"{curr_date.day}/{curr_date.month}"))
        curr_date += timedelta(days=1)
        
    for i in range(len(all_terms) - 1):
        curr_name, curr_start = all_terms[i]
        _, next_start = all_terms[i+1]
        term_dates[curr_name] = {"start": curr_start, "end": next_start}
    return term_dates

def get_exact_jieqi(user_dt):
    day_obj = sxtwl.fromSolar(user_dt.year, user_dt.month, user_dt.day)
    temp_day = day_obj
    while not temp_day.hasJieQi():
        temp_day = sxtwl.fromSolar(temp_day.getSolarYear(), temp_day.getSolarMonth(), temp_day.getSolarDay() - 1)
    
    jq_jd = temp_day.getJieQiJD()
    t_obj = sxtwl.JD2DD(jq_jd)
    jq_dt = datetime(int(t_obj.Y), int(t_obj.M), int(t_obj.D), int(t_obj.h), int(t_obj.m), int(t_obj.s))
    
    if user_dt >= jq_dt:
        return jq_names[temp_day.getJieQi()]
    else:
        prev_day = sxtwl.fromSolar(temp_day.getSolarYear(), temp_day.getSolarMonth(), temp_day.getSolarDay() - 1)
        while not prev_day.hasJieQi():
            prev_day = sxtwl.fromSolar(prev_day.getSolarYear(), prev_day.getSolarMonth(), prev_day.getSolarDay() - 1)
        return jq_names[prev_day.getJieQi()]

def get_standard_term_and_cuc(day_obj, exact_term):
    loai_don = "阳遁" if exact_term in yang_terms else "阴遁"
    d_gz = day_obj.getDayGZ()
    offset = d_gz.tg % 5
    phu_tou_chi_idx = (d_gz.dz - offset) % 12
    yuan = 0 if phu_tou_chi_idx in [0, 6, 3, 9] else 1 if phu_tou_chi_idx in [2, 8, 5, 11] else 2
    return loai_don, solar_term_ju[exact_term][yuan], exact_term

def get_shijia_term_and_cuc(day_obj):
    d_gz = day_obj.getDayGZ()
    offset = d_gz.tg % 5
    ft_d = sxtwl.fromSolar(day_obj.getSolarYear(), day_obj.getSolarMonth(), day_obj.getSolarDay())
    for _ in range(offset):
        ft_d = sxtwl.fromSolar(ft_d.getSolarYear(), ft_d.getSolarMonth(), ft_d.getSolarDay() - 1)
    
    ft_dz = ft_d.getDayGZ().dz
    if ft_dz in [0, 6, 3, 9]: yuan = 0
    elif ft_dz in [2, 8, 5, 11]: yuan = 1
    else: yuan = 2

    search_ft = sxtwl.fromSolar(ft_d.getSolarYear(), ft_d.getSolarMonth(), ft_d.getSolarDay())
    active_term = None
    
    while True:
        term_found = False
        for i in range(-2, 3):
            check_d = sxtwl.fromSolar(search_ft.getSolarYear(), search_ft.getSolarMonth(), search_ft.getSolarDay() + i)
            if check_d.hasJieQi():
                jq_idx = check_d.getJieQi()
                active_term = jq_names[jq_idx]
                term_found = True
                break
        if term_found:
            break
        for _ in range(5):
            search_ft = sxtwl.fromSolar(search_ft.getSolarYear(), search_ft.getSolarMonth(), search_ft.getSolarDay() - 1)

    loai_don = "阳遁" if active_term in yang_terms else "阴遁"
    so_cuc = solar_term_ju[active_term][yuan]
    return loai_don, so_cuc, active_term

def is_ngu_bat_ngo_thoi(can_gio, can_ngay):
    if not can_gio or not can_ngay: return False
    idx_gio, idx_ngay = thien_can.index(can_gio), thien_can.index(can_ngay)
    if (idx_gio % 2) != (idx_ngay % 2): return False
    el_gio, el_ngay = stem_elements.get(can_gio), stem_elements.get(can_ngay)
    khac_map_std = {"木": "土", "土": "水", "水": "火", "火": "金", "金": "木"}
    return khac_map_std.get(el_gio) == el_ngay

def tinh_tuan_khong(hoa_giap):
    idx_can, idx_chi = thien_can.index(hoa_giap[0]), dia_chi.index(hoa_giap[1])
    idx_tuan_dau = (idx_chi - idx_can) % 12
    return f"{dia_chi[(idx_tuan_dau - 2) % 12]}{dia_chi[(idx_tuan_dau - 1) % 12]}"

def get_board_stem(hoa_giap):
    if not hoa_giap or len(hoa_giap) < 2: return ""
    can, chi = hoa_giap[0], hoa_giap[1]
    if can != "甲": return can
    idx_can, idx_chi = thien_can.index(can), dia_chi.index(chi)
    chi_tuan = dia_chi[(idx_chi - idx_can) % 12]
    return {"子":"戊", "戌":"己", "申":"庚", "午":"辛", "辰":"壬", "寅":"癸"}[chi_tuan]

def tinh_an_can(can_gio_goc, cuc_so, loai_don, dia_ban_dict, cung_truc_su):
    diem_xuat_phat = cung_truc_su
    if can_gio_goc == dia_ban_dict.get(cung_truc_su, ""):
        diem_xuat_phat = 2 if cung_truc_su == 5 else 5
    an_can_dict = {}
    can_idx = luc_nghi.index(can_gio_goc)
    tien = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    lui =  [9, 8, 7, 6, 5, 4, 3, 2, 1]
    duong_bay = tien if loai_don == "阳遁" else lui
    start_idx_in_duong_bay = duong_bay.index(diem_xuat_phat)
    for i in range(9):
        current_cung = duong_bay[(start_idx_in_duong_bay + i) % 9]
        current_can = luc_nghi[(can_idx + i) % 9]
        an_can_dict[current_cung] = current_can
    return an_can_dict

# ==========================================
# 3. HỆ THỐNG LẬP QUẺ
# ==========================================
def lap_que(hoa_giap_gio, loai_don, so_cuc, display_mode):
    can_gio, chi_gio = hoa_giap_gio[0], hoa_giap_gio[1]
    loai = "阳" if loai_don == "阳遁" else "阴"
    idx_can, idx_chi = thien_can.index(can_gio), dia_chi.index(chi_gio)
    chi_tuan = dia_chi[(idx_chi - idx_can) % 12]
    can_tuan = {"子":"戊", "戌":"己", "申":"庚", "午":"辛", "辰":"壬", "寅":"癸"}[chi_tuan]

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

    steps = (dia_chi.index(chi_gio) - dia_chi.index(chi_tuan)) % 12
    target_door = (cung_goc + steps) % 9 or 9 if loai == "阳" else (cung_goc - steps) % 9 or 9
    cung_truc_su = target_door
    
    if target_door == 5: target_door = 2
    td_idx = ring_8.index(target_door)

    map_ngua = {"子":"寅", "丑":"亥", "寅":"申", "卯":"巳", "辰":"寅", "巳":"亥", "午":"申", "未":"巳", "申":"寅", "酉":"亥", "戌":"申", "亥":"巳"}
    vi_tri_ngua = {"寅":8, "巳":4, "申":2, "亥":6}[map_ngua[chi_gio]]

    cung_data = {i: {'dia': '', 'sao': '', 'mon': '', 'than': '', 'thien': '', 'ngua': '', 'ancan': ''} for i in range(1, 10)}
    cung_data[vi_tri_ngua]['ngua'] = "马"

    for i in range(1, 10):
        if i == 2:
            cung_data[i]['dia'] = f"{dia_ban.get(2, '')}/{dia_ban.get(5, '')}"
        else:
            cung_data[i]['dia'] = dia_ban.get(i, "")

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

    can_gio_thuc_ban = get_board_stem(hoa_giap_gio)
    an_can_dict = tinh_an_can(can_gio_thuc_ban, so_cuc, loai_don, dia_ban, cung_truc_su)
    for p in range(1, 10):
        cung_data[p]['ancan'] = an_can_dict[p]

    return cung_data, can_gio, truc_su

# ==========================================
# 4. GIAO DIỆN & RENDER HTML
# ==========================================
def get_colored_span(text, el_dict):
    if not text: return ""
    el = el_dict.get(text, "")
    color = element_colors.get(el, "#1a1a1a")
    return f"<span style='color:{color}; font-style:normal; font-weight:normal;'>{text}</span>"

def format_shijia_star(star_str, current_term):
    if not star_str: return ""
    season = term_to_season.get(current_term, "")
    s_el = season_elements.get(season, "")
    
    def _fmt(s):
        el = star_elements.get(s, "")
        color = element_colors.get(el, "#1a1a1a")
        is_vuong = current_term in entity_to_terms.get(s, [])
        is_tuky = khac_map.get(s_el) == el
        
        fw = "bold" if is_vuong else "normal"
        fs = "italic" if is_tuky else "normal"
        return f"<span style='color:{color}; font-weight:{fw}; font-style:{fs};'>{s}</span>"

    if "/" in star_str:
        p1, p2 = star_str.split('/')
        return f"{_fmt(p1)}<span style='color:#1a1a1a; font-weight:normal; font-style:normal;'>/</span>{_fmt(p2)}"
    return _fmt(star_str)

def format_shijia_door(door, cung, truc_su, current_term):
    if not door: return ""
    season = term_to_season.get(current_term, "")
    s_el = season_elements.get(season, "")
    el = door_elements.get(door, "")
    color = element_colors.get(el, "#1a1a1a")
    
    is_vuong = current_term in entity_to_terms.get(door, [])
    is_tuky = khac_map.get(s_el) == el
    
    fw = "bold" if is_vuong else "normal"
    fs = "italic" if is_tuky else "normal"
    td = "underline" if door == "开门" and cung in [2, 8] else "none"
    uo = "4px" if td == "underline" else "auto"
    
    shape_style = "display: inline-block; border: 1px solid rgba(0,0,0,0.25); border-radius: 12px; padding: 1px 4px; margin-left: -5px; line-height: 1.1;" if door == truc_su else ""
    
    return f"<span style='color:{color}; font-weight:{fw}; font-style:{fs}; text-decoration:{td}; text-underline-offset:{uo}; {shape_style}'>{door}</span>"

def format_star_with_rules(star_str):
    if not star_str: return ""
    if "/" in star_str:
        p1, p2 = star_str.split('/')
        return f"{get_colored_span(p1, star_elements)}/{get_colored_span(p2, star_elements)}"
    else:
        return get_colored_span(star_str, star_elements)

def format_stem_with_rules(stem_str, cung, can_gio_ban, can_ngay_ban, is_heaven=True):
    if not stem_str: return ""
    parts = stem_str.split('/')
    formatted = []
    for p in parts:
        el = stem_elements.get(p, "")
        color = element_colors.get(el, "#1a1a1a")
        weight = "normal"
        text_decor = "none"
        if p in stem_punish and stem_punish[p] == cung:
            color = "#800080"
            weight = "bold"
        if p in stem_tomb and cung in stem_tomb[p]:
            text_decor = "underline"

        wrapper_start = "<span style='display: inline-block; width: 26px; text-align: center;'>"
        wrapper_end = "</span>"
        shape_style = "display: inline-block; padding: 2px 0; line-height: 1.1;"
        inner_text = p
        
        if is_heaven:
            if p == can_gio_ban and p == can_ngay_ban:
                inner_text = f"<span style='display: inline-block; border: 1px solid rgba(0,0,0,0.25); border-radius: 50%; padding: 1px 3px; line-height: 1;'>{p}</span>"
                shape_style = "display: inline-block; border: 1px solid rgba(0,0,0,0.25); border-radius: 2px; padding: 1px; line-height: 1;"
            elif p == can_gio_ban:
                shape_style = "display: inline-block; border: 1px solid rgba(0,0,0,0.25); border-radius: 50%; padding: 3px 5px; line-height: 1;"
            elif p == can_ngay_ban:
                shape_style = "display: inline-block; border: 1px solid rgba(0,0,0,0.25); border-radius: 2px; padding: 0px 2px; line-height: 1.1;"

        formatted.append(f"{wrapper_start}<span style='color:{color}; font-weight:{weight}; text-decoration:{text_decor}; text-underline-offset: 4px; {shape_style}'>{inner_text}</span>{wrapper_end}")
    return "<span style='color:#1a1a1a; font-weight:normal; margin: 0 1px;'>/</span>".join(formatted)

def format_stem_simple(stem_str):
    if not stem_str: return ""
    parts = stem_str.split('/')
    formatted = []
    for p in parts:
        el = stem_elements.get(p, "")
        color = element_colors.get(el, "#1a1a1a")
        formatted.append(f"<span style='color:{color}; display: inline-block; width: 26px; text-align: center; font-weight:normal;'>{p}</span>")
    return "<span style='color:#1a1a1a; font-weight:normal; margin: 0 1px;'>/</span>".join(formatted)

def format_stem_simple_with_chi(stem_str, cung):
    if not stem_str: return ""
    parts = stem_str.split('/')
    formatted = []
    for p in parts:
        el = stem_elements.get(p, "")
        color = element_colors.get(el, "#1a1a1a")
        chi_mo = shijia_earth_branch_map.get(p, "") if cung != 5 else ""
        chi_html = f"<div style='position: absolute; top: 100%; left: 50%; transform: translateX(-50%); font-size: 11px; color: #999; line-height: 1; padding-top: 8px;'>{chi_mo}</div>" if chi_mo else ""
        
        formatted.append(f"""
            <span style='position: relative; display: inline-flex; align-items: center; justify-content: center; width: 26px; height: 20px; text-align: center;'>
                <span style='color:{color}; font-weight:normal; line-height: 1;'>{p}</span>
                {chi_html}
            </span>
        """)
    return "<span style='color:#1a1a1a; font-weight:normal; margin: 0 1px; display: inline-flex; align-items: center;'>/</span>".join(formatted)

def format_door_with_rules(door, cung, truc_su):
    if not door: return ""
    el = door_elements.get(door, "")
    color = element_colors.get(el, "#1a1a1a")
    khac_map_std = {"木": "土", "土": "水", "水": "火", "火": "金", "金": "木"}
    is_khac = (khac_map_std.get(el) == palace_elements.get(cung))
    f_style = "italic" if is_khac else "normal"
    f_weight = "bold" if is_khac else "normal"
    shape_style = "display: inline-block; border: 1px solid rgba(0,0,0,0.25); border-radius: 12px; padding: 1px 4px; margin-left: -5px; line-height: 1.1;" if door == truc_su else ""
    return f"<span style='color:{color}; font-style:{f_style}; font-weight:{f_weight}; {shape_style}'>{door}</span>"

def format_door_simple_with_circle(door, truc_su):
    if not door: return ""
    el = door_elements.get(door, "")
    color = element_colors.get(el, "#1a1a1a")
    shape_style = "display: inline-block; border: 1px solid rgba(0,0,0,0.25); border-radius: 12px; padding: 1px 4px; margin-left: -5px; line-height: 1.1;" if door == truc_su else ""
    return f"<span style='color:{color}; font-style:normal; font-weight:normal; {shape_style}'>{door}</span>"

def get_ancan_html(can):
    if not can: return ""
    el = stem_elements.get(can, "")
    color = element_colors.get(el, "#1a1a1a")
    return f"<div style='position: absolute; bottom: 2px; left: 6px; font-size: 14px; color:{color}; font-weight: normal;'>{can}</div>"

def render_jiazi_table():
    xun_headers = ["甲子", "甲戌", "甲申", "甲午", "甲辰", "甲寅"]
    stems = "甲乙丙丁戊己庚辛壬癸"
    branches = "子丑寅卯辰巳午未申酉戌亥"

    html = """
    <style>
        .jiazi-table { border-collapse: collapse; width: 480px !important; max-width: 480px !important; min-width: 480px !important; height: 360px !important; max-height: 360px !important; font-family: "Microsoft YaHei", sans-serif; font-size: 13px; text-align: center; background-color: #fefefe; color: #000; margin: 0 auto; table-layout: fixed; box-sizing: border-box; }
        .jiazi-table th, .jiazi-table td { border: 1px solid #bfbfbf; padding: 2px; overflow: hidden; white-space: nowrap; }
        .jz-header { font-weight: normal; }
        .jz-footer { font-weight: normal; line-height: 1.2;}
        @media (max-width: 1000px) {
            .jiazi-table { width: 100% !important; min-width: 320px !important; height: auto !important; font-size: 13px; }
        }
    </style>
    <table class="jiazi-table"><tr class="jz-header">
    """
    for h in xun_headers: html += f"<th>{h}</th>"
    html += "</tr>"
    for i in range(10):
        html += "<tr>"
        for j in range(6):
            html += f"<td>{stems[i]}{branches[(12 - j * 2 + i) % 12]}</td>"
        html += "</tr>"
    html += "<tr class='jz-footer'>"
    for kw in ["戌 亥", "申 酉", "午 未", "辰 巳", "寅 卯", "子 丑"]: html += f"<td>{kw}</td>"
    html += "</tr></table>"
    return html

def render_html_table(cung_data, tk_ngay, tk_gio, bazi_dict, hoa_giap_hien_tai, truc_su, display_mode, term_dates, shijia_term):
    luoi_lac_thu = [[4, 9, 2], [3, 5, 7], [8, 1, 6]]
    cung_tk_ngay = [chi_to_cung[chi] for chi in tk_ngay]
    cung_tk_gio = [chi_to_cung[chi] for chi in tk_gio]
    month_branch = bazi_dict['thang'][1]
    can_gio_thuc = hoa_giap_hien_tai[0]
    can_ngay_thuc = bazi_dict['ngay'][0]
    
    can_gio_ban = get_board_stem(hoa_giap_hien_tai)
    can_ngay_ban = get_board_stem(bazi_dict['ngay'])

    is_star_fuyin = "天蓬" in cung_data[1]['sao']
    is_star_fanyin = "天英" in cung_data[1]['sao']
    is_door_fuyin = "休门" in cung_data[1]['mon']
    is_door_fanyin = "景门" in cung_data[1]['mon']
    is_wu_bu_yu_shi = is_ngu_bat_ngo_thoi(can_gio_thuc, can_ngay_thuc)

    inner_numbers = {4: "2, 3, 4, 5", 9: "2, 3, 7, 9", 2: "2, 5, 8, 10", 7: "2, 4, 7, 9", 6: "1, 4, 6, 9", 1: "1, 6", 8: "5, 7, 8, 10", 3: "3, 4, 8"}

    html = f"""
    <style>
        .qmdj-table {{ border-collapse: collapse; width: 100%; max-width: 480px; min-width: 320px; height: 360px; table-layout: fixed; font-size: 15px; background-color: #fefefe; margin: 0 auto; }}
        .qmdj-td {{ border: 1px solid #bfbfbf; width: 33.33%; padding: 8px 4px 18px 4px; position: relative; vertical-align: top; overflow: visible; transition: background-color 0.2s; }}
        
        .row-top, .row-mid, .row-bot {{ display: flex; align-items: center; justify-content: flex-start; }}
        .item-left {{ width: 55px; text-align: left; margin-left: 2px; flex-shrink: 0; line-height: 1.2; }}
        .item-right {{ display: flex; align-items: center; flex-wrap: wrap; flex-grow: 1; gap: 2px 3px; line-height: 1.2; margin-left: 10px; }}
        .stem {{ font-size: 16px; margin-right: 1px; font-weight: normal; display: flex; align-items: center; }}
        
        /* Default Spacing */
        .default-top {{ margin-bottom: 8px; }}
        .default-mid {{ margin-bottom: 6px; }}
        .default-bot {{ margin-bottom: 0px; }}

        /* Shijia Zhuanpan Spacing */
        .shijia-top {{ margin-top: 5px; margin-bottom: 22px; }}
        .shijia-mid {{ margin-bottom: 22px; }}
        .shijia-bot {{ margin-bottom: 0px; }}

        .horse {{ position: absolute; top: 4px; right: 6px; color: #1a1a1a; font-weight: normal; font-size: 13px; cursor: default; }}
        .bagua-mark {{ position: absolute; bottom: 2px; right: 6px; color: #1a1a1a; font-size: 13px; cursor: pointer; z-index: 20; }}
        .inner-numbers {{ position: absolute; bottom: 2px; left: 50%; transform: translateX(-50%); font-size: 11px; color: #000; font-weight: normal; letter-spacing: 0.5px; white-space: nowrap; }}
        .center-fuyin {{ position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); display: flex; flex-direction: column; align-items: center; z-index: 10; gap: 2px; }}
        .fuyin-badge {{ background-color: #FFD700; color: #000; padding: 2px 4px; border-radius: 3px; font-weight: bold; font-size: 12px; white-space: nowrap; box-shadow: 1px 1px 3px rgba(0,0,0,0.3); }}
        .wubu-badge {{ background-color: #FF4500; color: #FFF; padding: 2px 4px; border-radius: 3px; font-weight: bold; font-size: 12px; white-space: nowrap; box-shadow: 1px 1px 3px rgba(0,0,0,0.3); }}
        
        .toggle-btn {{ position: absolute; top: 2px; left: 2px; font-size: 10px; color: #999; cursor: pointer; user-select: none; border: 1px solid #ccc; padding: 1px 3px; border-radius: 2px; background: #fafafa; z-index: 30; }}
        .toggle-btn:hover {{ background: #eee; }}
        
        @media (max-width: 400px) {{
            .item-left {{ width: 45px; font-size: 13px; }}
            .item-right {{ margin-left: 5px; }}
            .stem {{ font-size: 14px; }}
        }}
    </style>
    <table class="qmdj-table">
    """

    for row in luoi_lac_thu:
        html += "<tr>"
        for p in row:
            d = cung_data[p]

            if display_mode == "十家转盘":
                class_top = "row-top shijia-top"
                class_mid = "row-mid shijia-mid"
                class_bot = "row-bot shijia-bot"

                than_html = get_colored_span(d['than'], deity_elements)
                sao_html = format_shijia_star(d['sao'], shijia_term)
                mon_html = format_shijia_door(d['mon'], p, truc_su, shijia_term)
                
                thien_parts = d['thien'].split('/')
                thien_res = []
                for tp in thien_parts:
                    el = stem_elements.get(tp, "")
                    color = element_colors.get(el, "#1a1a1a")
                    thien_res.append(f"<span style='color:{color}; display: inline-block; width: 26px; text-align: center; font-weight:normal;'>{tp}</span>")
                thien_display = "<span style='color:#1a1a1a; font-weight:normal; margin: 0 1px;'>/</span>".join(thien_res)

                dia_display = format_stem_simple_with_chi(d['dia'], p)
                
                horse_html = void_html = gua_html = inner_nums_html = center_alert_html = ancan_html = toggle_btn_html = ""
                
                if p in palace_to_terms and term_dates:
                    terms_list = palace_to_terms[p]
                    terms_html = "<div style='position: absolute; top: 3px; right: 3px; text-align: right; line-height: 1.25; font-size: 10px; color: #888;'>"
                    for t in terms_list:
                        if t in term_dates:
                            t_start = term_dates[t]['start']
                            t_end = term_dates[t]['end']
                            is_active = (t == shijia_term)
                            fw = "bold; color: #000;" if is_active else "normal;"
                            terms_html += f"<div style='font-weight: {fw}'>{t} ({t_start}-{t_end})</div>"
                    terms_html += "</div>"
                else:
                    terms_html = ""
            else:
                class_top = "row-top default-top"
                class_mid = "row-mid default-mid"
                class_bot = "row-bot default-bot"

                than_html = get_colored_span(d['than'], deity_elements)
                sao_html = format_star_with_rules(d['sao'])
                mon_html = format_door_with_rules(d['mon'], p, truc_su)
                thien_display = format_stem_with_rules(d['thien'], p, can_gio_ban, can_ngay_ban, is_heaven=True)
                dia_display = format_stem_with_rules(d['dia'], p, can_gio_ban, can_ngay_ban, is_heaven=False)
                ancan_html = get_ancan_html(d['ancan'])
                horse_html = f'<div class="horse">{d["ngua"]}</div>' if d['ngua'] else ""
                terms_html = ""

                void_html = ""
                if p in cung_tk_ngay or p in cung_tk_gio:
                    right_pos = "22px" if d['ngua'] else "6px"
                    if p in cung_tk_gio:
                        void_html = f'<div style="position: absolute; top: 6px; right: {right_pos}; width: 10px; height: 10px; border: 2px solid #000; border-radius: 50%; box-sizing: border-box;"></div>'
                    else:
                        void_html = f'<div style="position: absolute; top: 6px; right: {right_pos}; width: 10px; height: 10px; border: 1px solid #999; border-radius: 50%; box-sizing: border-box;"></div>'

                cung_el = palace_elements.get(p)
                month_el = branch_elements.get(month_branch)
                sinh_map_std = {"水": "木", "木": "火", "火": "土", "土": "金", "金": "水"}
                is_vuong_tuong = (month_el == cung_el) or (sinh_map_std.get(month_el) == cung_el)

                gua_char = cung_to_gua[p]
                gua_html = ""
                if gua_char:
                    w_style = "bold; font-size:14px;" if is_vuong_tuong else "normal;"
                    gua_html = f"<div class='bagua-mark' style='font-weight:{w_style}' onclick='toggleHighlight({p})'>{gua_char}</div>"

                nums_str = inner_numbers.get(p, "")
                inner_nums_html = f"<div class='inner-numbers'>{nums_str}</div>" if nums_str else ""

                center_alert_html = toggle_btn_html = ""
                if p == 5:
                    toggle_btn_html = "<div class='toggle-btn' onclick='toggleJiazi()'>六十</div>"
                    badges = []
                    if is_wu_bu_yu_shi: badges.append("<div class='wubu-badge'>五不遇时</div>")
                    if is_star_fuyin and is_door_fuyin: badges.append("<div class='fuyin-badge'>星门全伏吟</div>")
                    elif is_star_fanyin and is_door_fanyin: badges.append("<div class='fuyin-badge'>星门全反吟</div>")
                    else:
                        if is_star_fuyin: badges.append("<div class='fuyin-badge'>星伏吟</div>")
                        elif is_star_fanyin: badges.append("<div class='fuyin-badge'>星反吟</div>")
                        if is_door_fuyin: badges.append("<div class='fuyin-badge'>门伏吟</div>")
                        elif is_door_fanyin: badges.append("<div class='fuyin-badge'>门反吟</div>")
                    
                    if badges:
                        center_alert_html = f"<div class='center-fuyin'>{''.join(badges)}</div>"

            if p == 5:
                # XÓA HOÀN TOÀN TÊN TIẾT KHÍ VÀ MÙA TẠI TRUNG CUNG THEO YÊU CẦU MỚI
                center_term_html = ""

                html += f"""
                <td id="palace-{p}" class="qmdj-td">
                    {toggle_btn_html}
                    {center_term_html}
                    {center_alert_html}
                    <div style="position: absolute; bottom: 6px; right: 10px; font-size: 16px;">{dia_display}</div>
                    {ancan_html}
                </td>"""
            else:
                html += f"""
                <td id="palace-{p}" class="qmdj-td">
                    {horse_html}
                    {void_html}
                    {gua_html}
                    {inner_nums_html}
                    {ancan_html}
                    {terms_html}
                    <div class="{class_top}">
                        <div class="item-left">{than_html}</div><div class="item-right"></div>
                    </div>
                    <div class="{class_mid}">
                        <div class="item-left">{sao_html}</div>
                        <div class="item-right"><span class="stem">{thien_display}</span></div>
                    </div>
                    <div class="{class_bot}">
                        <div class="item-left">{mon_html}</div>
                        <div class="item-right"><span class="stem">{dia_display}</span></div>
                    </div>
                </td>"""
        html += "</tr>"
        
    html += "</table>"
    return html

# ==========================================
# 5. STREAMLIT APP
# ==========================================
def get_current_vn_time():
    return datetime.now(timezone(timedelta(hours=7)))

if "init_dt" not in st.session_state:
    st.session_state.init_dt = get_current_vn_time()

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    display_mode = st.selectbox("Hiển thị", ["拆补转盘", "十家转盘"])
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

day_obj = sxtwl.fromSolar(actual_date.year, actual_date.month, actual_date.day)
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

term_dates = get_yearly_terms(actual_date.year)
_, _, shijia_term = get_shijia_term_and_cuc(day_obj)
exact_term = get_exact_jieqi(user_dt)

if display_mode == "十家转盘":
    don_auto, cuc_auto, _ = get_shijia_term_and_cuc(day_obj)
else:
    don_auto, cuc_auto, _ = get_standard_term_and_cuc(day_obj, exact_term)

if override_dun_ju != "Mặc định":
    don = "阳遁" if "阳" in override_dun_ju else "阴遁"
    cuc = int(override_dun_ju[-1])
else:
    don = don_auto
    cuc = cuc_auto
    
chuoi_cuc = f"{don}{cuc}局"
bazi_chuoi = f"{bazi_dict['nam']}年 {bazi_dict['thang']}月 {bazi_dict['ngay']}日"

hour_str = f"{hoa_giap_hien_tai}时"
if hoa_giap_hien_tai[0] == "甲": hour_str = f"<b>{hour_str}</b>"

tk_ngay = tinh_tuan_khong(bazi_dict['ngay'])
tk_gio = tinh_tuan_khong(hoa_giap_hien_tai)

data, can_gio, truc_su = lap_que(hoa_giap_hien_tai, don, cuc, display_mode)

title = f"<h3 style='margin-bottom:8px; font-family:sans-serif; color: #1a1a1a; font-weight: normal; font-size: 18px; user-select: none; text-align: center;'>{bazi_chuoi} {hour_str}</h3>"
sub_title = f"<h4 style='margin-top:0px; margin-bottom:8px; font-family:sans-serif; color: #555; font-weight: normal; font-size: 16px; user-select: none; text-align: center;'>奇门遁甲 | {chuoi_cuc}</h4>"

qimen_board_html = render_html_table(data, tk_ngay, tk_gio, bazi_dict, hoa_giap_hien_tai, truc_su, display_mode, term_dates, shijia_term)
jiazi_board_html = render_jiazi_table()

js_script = """
<script>
    const relations = {
        1: [9, 2, 7], 2: [8, 4, 1], 3: [7, 9, 8], 4: [6, 7, 2],
        6: [4, 8, 9], 7: [3, 1, 4], 8: [2, 3, 6], 9: [1, 6, 3]
    };
    let currentActive = null;
    function toggleHighlight(palace) {
        if(palace === 5) return;
        for(let i=1; i<=9; i++) {
            if(i===5) continue;
            document.getElementById('palace-' + i).style.backgroundColor = '#fefefe';
        }
        if (currentActive === palace) {
            currentActive = null;
        } else {
            let targets = relations[palace];
            if(targets) {
                targets.forEach(t => {
                    let cell = document.getElementById('palace-' + t);
                    if(cell) cell.style.backgroundColor = '#e6e6e6';
                });
            }
            currentActive = palace;
        }
    }
    
    function toggleJiazi() {
        var jz = document.getElementById('jiazi-container');
        if (jz.style.display === "none" || jz.style.display === "") {
            jz.style.display = "flex";
        } else {
            jz.style.display = "none";
        }
    }
</script>
"""

combined_html = f"""
    <style>
        .main-wrapper {{ display: flex; flex-direction: row; align-items: flex-start; justify-content: center; gap: 40px; width: 100%; padding-top: 10px; }}
        .board-container {{ display: flex; flex-direction: column; align-items: center; width: 100%; max-width: 480px; }}
        #jiazi-container {{ display: none; flex-direction: column; align-items: center; width: 100%; max-width: 480px; }}
        
        @media (max-width: 1000px) {{
            .main-wrapper {{ flex-direction: column; align-items: center; gap: 20px; }}
        }}
    </style>
    <div class="main-wrapper">
        <div class="board-container">
            {title}
            {sub_title}
            {qimen_board_html}
        </div>
        <div id="jiazi-container">
            <div style="visibility: hidden; pointer-events: none;">
                {title}
                {sub_title}
            </div>
            {jiazi_board_html}
        </div>
    </div>
    {js_script}
"""

st.components.v1.html(combined_html, height=900, scrolling=True)
