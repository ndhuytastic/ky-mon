import streamlit as st
import sxtwl
from datetime import datetime, timedelta, timezone, date, time
import ephem
import warnings
import re

warnings.filterwarnings('ignore')
st.set_page_config(page_title="Ngọa Long Kỳ Môn", layout="wide", initial_sidebar_state="collapsed")

# ==========================================
# 1. DỮ LIỆU CƠ BẢN & HẰNG SỐ CHÂN TRUYỀN
# ==========================================
thien_can = "甲乙丙丁戊己庚辛壬癸"
dia_chi = "子丑寅卯辰巳午未申酉戌亥"
luc_nghi = ["戊", "己", "庚", "辛", "壬", "癸", "丁", "丙", "乙"]

WOLONG_OUTER_PALACES = [4, 9, 2, 7, 6, 1, 8, 3] 
WOLONG_FLYING_PATH = [5, 6, 7, 8, 9, 1, 2, 3, 4] 
WOLONG_NUM_TO_STEM = {1: "癸", 2: "丁", 3: "丙", 4: "乙", 5: "戊", 6: "己", 7: "庚", 8: "辛", 9: "壬", 0: "甲"}
WOLONG_ORIGINAL_GATES = {1: "休门", 8: "生门", 3: "伤门", 4: "杜门", 9: "景门", 2: "死门", 7: "惊门", 6: "开门"}
WOLONG_CLOCKWISE_GATES = ["景门", "死门", "惊门", "开门", "休门", "生门", "伤门", "杜门"]

ORIGINAL_STARS = {1: "天蓬", 2: "天芮", 3: "天冲", 4: "天辅", 5: "天禽", 6: "天心", 7: "天柱", 8: "天任", 9: "天英"}
DEITIES = ["值符", "螣蛇", "太阴", "六合", "勾陈", "朱雀", "九地", "九天"] 

wolong_jq_order = ["大雪", "冬至", "小寒", "大寒", "立春", "雨水", "惊蛰", "春分", "清明", "谷雨", "立夏", "小满", "芒种", "夏至", "小暑", "大暑", "立秋", "处暑", "白露", "秋分", "寒露", "霜降", "立冬", "小雪"]

GATE_TO_TRIGRAM = {"休门": "地", "生门": "雷", "伤门": "火", "杜门": "泽", "景门": "天", "死门": "风", "惊门": "水", "开门": "山"}
TIEN_THIEN_MAP = {9: "天", 1: "地", 3: "火", 7: "水", 6: "山", 2: "风", 8: "雷", 4: "泽"}

TRIGRAM_BIN = {"地": [0,0,0], "山": [0,0,1], "水": [0,1,0], "风": [0,1,1], "雷": [1,0,0], "火": [1,0,1], "泽": [1,1,0], "天": [1,1,1]}
BIN_TO_TRIGRAM = {tuple(v): k for k, v in TRIGRAM_BIN.items()}
TRIGRAM_UNICODE = {"天": "☰", "泽": "☱", "火": "☲", "雷": "☳", "风": "☴", "水": "☵", "山": "☶", "地": "☷"}

EVAL_DICT = {
    "风": {"泽":"〇", "天":"△", "风":"✕", "火":"〇", "水":"△", "雷":"〇", "地":"✕", "山":"〇"},
    "天": {"泽":"✕", "天":"△", "风":"✕", "火":"〇", "水":"✕", "雷":"△", "地":"✕", "山":"✕"},
    "水": {"泽":"✕", "天":"✕", "风":"✕", "火":"〇", "水":"✕", "雷":"✕", "地":"〇", "山":"✕"},
    "泽": {"泽":"△", "天":"✕", "风":"✕", "火":"✕", "水":"✕", "雷":"✕", "地":"〇", "山":"〇"},
    "山": {"泽":"△", "天":"〇", "风":"✕", "火":"✕", "水":"✕", "雷":"〇", "地":"✕", "山":"✕"},
    "火": {"泽":"✕", "天":"〇", "风":"〇", "火":"✕", "水":"✕", "雷":"△", "地":"〇", "山":"✕"},
    "地": {"泽":"〇", "天":"〇", "风":"〇", "火":"✕", "水":"✕", "雷":"〇", "地":"△", "山":"△"},
    "雷": {"泽":"✕", "天":"△", "风":"〇", "火":"〇", "水":"〇", "雷":"△", "地":"〇", "山":"✕"}
}

HEX_NAME_DICT = {
    ("天","天"): "Càn", ("地","地"): "Khôn", ("水","雷"): "Truân", ("山","水"): "Mông",
    ("水","天"): "Nhu", ("天","水"): "Tụng", ("地","水"): "Sư", ("水","地"): "Tỷ",
    ("风","天"): "Tiểu Súc", ("天","泽"): "Lý", ("地","天"): "Thái", ("天","地"): "Bĩ",
    ("天","火"): "Đồng Nhân", ("火","天"): "Đại Hữu", ("地","山"): "Khiêm", ("雷","地"): "Dự",
    ("泽","雷"): "Tùy", ("山","风"): "Cổ", ("地","泽"): "Lâm", ("风","地"): "Quan",
    ("火","雷"): "Phệ Hạp", ("山","火"): "Bí", ("山","地"): "Bác", ("地","雷"): "Phục",
    ("天","雷"): "Vô Vọng", ("山","天"): "Đại Súc", ("山","雷"): "Di", ("泽","风"): "Đại Quá",
    ("水","水"): "Khảm", ("火","火"): "Ly", ("泽","山"): "Hàm", ("雷","风"): "Hằng",
    ("天","山"): "Độn", ("雷","天"): "Đại Tráng", ("火","地"): "Tấn", ("地","火"): "Minh Di",
    ("风","火"): "Gia Nhân", ("火","泽"): "Khuê", ("水","山"): "Kiển", ("雷","水"): "Giải",
    ("山","泽"): "Tổn", ("风","雷"): "Ích", ("泽","天"): "Quải", ("天","风"): "Cấu",
    ("泽","地"): "Tụy", ("地","风"): "Thăng", ("泽","水"): "Khốn", ("水","风"): "Tỉnh",
    ("泽","火"): "Cách", ("火","风"): "Đỉnh", ("雷","雷"): "Chấn", ("山","山"): "Cấn",
    ("风","山"): "Tiệm", ("雷","泽"): "Quy Muội", ("雷","火"): "Phong", ("火","山"): "Lữ",
    ("风","风"): "Tốn", ("泽","泽"): "Đoài", ("风","水"): "Hoán", ("水","泽"): "Tiết",
    ("风","泽"): "Trung Phu", ("雷","山"): "Tiểu Quá", ("水","火"): "Ký Tế", ("火","水"): "Vị Tế"
}

KIGAKU_OPPOSITE = {1: 9, 2: 8, 3: 7, 4: 6, 6: 4, 7: 3, 8: 2, 9: 1, 5: 5}
KIGAKU_HOME = {1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7, 8: 8, 9: 9}
KIGAKU_COMPATIBILITY = {
    1: [3, 4, 6, 7], 2: [6, 7, 8, 9], 3: [1, 4, 9], 4: [1, 3, 9], 5: [2, 6, 7, 8, 9],
    6: [1, 2, 7, 8], 7: [1, 2, 6, 8], 8: [2, 6, 7, 9], 9: [2, 3, 4, 8]
}
BRANCH_TO_PALACE = {"子": 1, "丑": 8, "寅": 8, "卯": 3, "辰": 4, "巳": 4, "午": 9, "未": 2, "申": 2, "酉": 7, "戌": 6, "亥": 6}

# ==========================================
# 2. LOGIC LỊCH (NHẬT BÀN 360 NGÀY ÂM LỊCH)
# ==========================================
def get_xun_leader(can, chi):
    return {"子":"戊", "戌":"己", "申":"庚", "午":"辛", "辰":"壬", "寅":"癸"}[dia_chi[(dia_chi.index(chi) - thien_can.index(can)) % 12]]

def get_hour_nine_star(day_branch, hour_branch, dun_type):
    hb_idx = dia_chi.index(hour_branch) 
    start_star = 1 if day_branch in ["子","午","卯","酉"] else (4 if day_branch in ["辰","戌","丑","未"] else 7)
    if dun_type == "阴遁": start_star = 7 if day_branch in ["辰","戌","丑","未"] else (4 if day_branch in ["寅","申","巳","亥"] else 1)
    res = (start_star + hb_idx) % 9 if dun_type == "阳遁" else (start_star - hb_idx) % 9
    return 9 if res == 0 else res

def get_custom_lunar_day_data(solar_date):
    """ THUẬT TOÁN ĐỘC QUYỀN 360 NGÀY ÂM LỊCH TÍNH CẢ TIẾT KHÍ """
    day_obj = sxtwl.fromSolar(solar_date.year, solar_date.month, solar_date.day)
    l_month = day_obj.getLunarMonth()
    l_day = day_obj.getLunarDay()
    is_leap = day_obj.isLunarLeap()
    
    L = (l_month - 1) * 30 + l_day
    
    if 136 <= L <= 315:
        dun_type = "阴遁"
        offset = L - 136
        star = 9 - (offset % 9)
        if star == 0: star = 9
    else:
        dun_type = "阳遁"
        offset = L - 316 if L >= 316 else 44 + L 
        star = (offset % 9) + 1
        
    can = thien_can[offset % 10]
    chi = dia_chi[offset % 12]
    
    # --- TÍNH TIẾT KHÍ & TAM NGUYÊN (TOÁN HỌC) ---
    abs_day = ((l_month - 11) % 12) * 30 + (l_day - 1)
    wl_jieqi = wolong_jq_order[abs_day // 15 % 24]
    day_in_jq = abs_day % 15
    wl_yuan = "上" if day_in_jq < 5 else "中" if day_in_jq < 10 else "下"
    
    return l_month, l_day, is_leap, can, chi, dun_type, star, wl_jieqi, wl_yuan

# ==========================================
# 3. LẬP BÀN TOÁN HỌC
# ==========================================
def lap_que_wolong(can_ngay, chi_ngay, dun_type, ju_num, daily_star):
    cung_data = {i: {'dia': '', 'mon': '', 'thien': '', 'sao': '', 'than': '', 'day_star': ''} for i in range(1, 10)}
    
    current_val = (10 - ju_num) if dun_type == "阳遁" else ju_num
    step_dir = 1 if dun_type == "阳遁" else -1
    dia_ban = {}
    for cung in WOLONG_FLYING_PATH:
        can = WOLONG_NUM_TO_STEM.get(current_val, "")
        dia_ban[cung] = can
        cung_data[cung]['dia'] = can
        current_val += step_dir
        if current_val > 9: current_val = 1
        elif current_val < 1: current_val = 9

    luc_nghi_ngay = get_xun_leader(can_ngay, chi_ngay)
    
    p_circle_list = [c for c, can in dia_ban.items() if can == luc_nghi_ngay] 
    p_circle = p_circle_list[0] if p_circle_list else 5

    target_stem = luc_nghi_ngay if can_ngay == '甲' else can_ngay
    p_day_stem_list = [c for c, can in dia_ban.items() if can == target_stem]
    p_day_stem = p_day_stem_list[0] if p_day_stem_list else 5

    if p_circle == 5:
        for i in range(1, 10): 
            cung_data[i]['thien'] = dia_ban[i]
        
        if p_day_stem != 5:
            cung_data[p_day_stem]['thien'] = dia_ban[5]
            cung_data[5]['thien'] = dia_ban[p_day_stem]

    elif p_day_stem == 5:
        for i in WOLONG_OUTER_PALACES: cung_data[i]['thien'] = dia_ban[i] 
        cung_data[5]['thien'] = dia_ban[5] 
        
    else:
        idx_source = WOLONG_OUTER_PALACES.index(p_circle)
        idx_target = WOLONG_OUTER_PALACES.index(p_day_stem)
        offset = (idx_target - idx_source) % 8
        for i in range(8):
            cung_data[WOLONG_OUTER_PALACES[i]]['thien'] = dia_ban[WOLONG_OUTER_PALACES[(i - offset) % 8]]
        cung_data[5]['thien'] = dia_ban[5]

    s_steps = thien_can.index(can_ngay)
    p_land = 5
    if p_circle != 5:
        s_steps = thien_can.index(can_ngay) + 1
        seq = [1, 2, 3, 4, 5, 6, 7, 8, 9] if dun_type == "阳遁" else [9, 8, 7, 6, 5, 4, 3, 2, 1]
        p_land = seq[(seq.index(p_circle) + s_steps - 1) % 9]

    if p_circle == 5:
        for p, door in WOLONG_ORIGINAL_GATES.items(): cung_data[p]['mon'] = door
    else:
        g_start = WOLONG_ORIGINAL_GATES[p_circle]
        if p_land == 5:
            for p, door in WOLONG_ORIGINAL_GATES.items(): cung_data[p]['mon'] = door
        else:
            idx_land = WOLONG_OUTER_PALACES.index(p_land)
            idx_gate = WOLONG_CLOCKWISE_GATES.index(g_start)
            for i in range(8):
                cung_data[WOLONG_OUTER_PALACES[(idx_land + i) % 8]]['mon'] = WOLONG_CLOCKWISE_GATES[(idx_gate + i) % 8]

    cung_data[5]['mon'] = "惊门" if dun_type == "阳遁" else "生门"

    curr_star = daily_star 
    for cung in WOLONG_FLYING_PATH:
        cung_data[cung]['day_star'] = curr_star
        curr_star = 1 if curr_star == 9 else curr_star + 1

    luoshu_9 = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    idx_base_star = luoshu_9.index(p_circle)
    idx_target_star = luoshu_9.index(p_day_stem)
    shift_for_star = (idx_target_star - idx_base_star) % 9
    for i in range(1, 10):
        idx_new = (luoshu_9.index(i) + shift_for_star) % 9
        cung_data[luoshu_9[idx_new]]['sao'] = ORIGINAL_STARS[i]
    cung_data[5]['sao'] = "" 

    anchor_palace = p_day_stem
    if anchor_palace == 5: anchor_palace = 8 if dun_type == "阳遁" else 7
        
    idx_anchor = WOLONG_OUTER_PALACES.index(anchor_palace)
    for i in range(8):
        if dun_type == "阳遁": cung_data[WOLONG_OUTER_PALACES[(idx_anchor + i) % 8]]['than'] = DEITIES[i]
        else: cung_data[WOLONG_OUTER_PALACES[(idx_anchor - i) % 8]]['than'] = DEITIES[i]
    cung_data[5]['than'] = ""

    cung_phi_tinh = cung_data[5]['day_star']
    return cung_data, p_circle, cung_phi_tinh, p_land

# ==========================================
# 4. MODULE PHÂN TÍCH CÁCH CỤC
# ==========================================
def qimen_analyzer_hojo(cung_data, can_tuan, p_land):
    FORMATION_RANKS = {
        "天遁": 1, "地遁": 1, "人遁": 1, "神遁": 1, "鬼遁": 1,
        "大格": 1, "小格": 1, "刑格": 1, "戦格": 1, "飛宮格": 1, "伏宮格": 1, 
        "青竜逃走": 1, "白虎猖狂": 1, "熒惑入白": 1, "太白入熒": 1, "朱雀投江": 1, "螣蛇妖嬌": 1,
        "青竜返首": 2, "飛鳥跌穴": 2, "玉女守門": 2, "乙奇得使": 2, "丙奇得使": 2, "丁奇得使": 2, 
        "竜遁": 2, "虎遁": 2, "風遁": 2, "雲遁": 2, 
        "乙奇入墓": 2, "丙奇入墓": 2, "丁奇入墓": 2,
        "干伏吟": 2, "干反吟": 2, 
        "乙奇昇殿": 3, "丙奇昇殿": 3, "丁奇昇殿": 3,
        "星門伏吟": 3, "星門反吟": 3, "八門受制": 3, "六儀撃刑": 3
    }
    
    cung_status = {i: [] for i in range(1, 10)}
    can_can_data = {'甲':{'甲':'吉','乙':'凶','丙':'吉','丁':'吉','戊':'凶','己':'吉','庚':'大凶','辛':'凶','壬':'凶','癸':'吉'}, '乙':{'甲':'吉','乙':'凶','丙':'吉','丁':'吉','戊':'吉','己':'吉','庚':'凶','辛':'大凶','壬':'吉','癸':'凶'}, '丙':{'甲':'吉','乙':'吉','丙':'凶','丁':'吉','戊':'吉','己':'吉','庚':'大凶','辛':'吉','壬':'吉','癸':'凶'}, '丁':{'甲':'吉','乙':'吉','丙':'吉','丁':'吉','戊':'吉','己':'凶','庚':'吉','辛':'凶','壬':'吉','癸':'大凶'}, '戊':{'甲':'凶','乙':'吉','丙':'吉','丁':'吉','戊':'凶','己':'凶','庚':'凶','辛':'凶','壬':'吉','癸':'凶'}, '己':{'甲':'凶','乙':'吉','丙':'凶','丁':'凶','戊':'吉','己':'凶','庚':'凶','辛':'凶','壬':'凶','癸':'凶'}, '庚':{'甲':'大凶','乙':'凶','丙':'大凶','丁':'吉','戊':'凶','己':'大凶','庚':'大凶','辛':'凶','壬':'大凶','癸':'大凶'}, '辛':{'甲':'凶','乙':'大凶','丙':'凶','丁':'吉','戊':'凶','己':'凶','庚':'凶','辛':'凶','壬':'凶','癸':'凶'}, '壬':{'甲':'凶','乙':'凶','丙':'凶','丁':'吉','戊':'吉','己':'凶','庚':'凶','辛':'吉','壬':'凶','癸':'凶'}, '癸':{'甲':'吉','乙':'凶','丙':'吉','丁':'大凶','戊':'吉','己':'凶','庚':'大凶','辛':'凶','壬':'凶','癸':'凶'}}

    def get_actual(can): return '甲' if can == can_tuan else can

    for p, d in cung_data.items():
        if p == 5: continue 
        raw_t, raw_d = d['thien'], d['dia']
        if not raw_t or not raw_d: continue

        t_can, d_can = get_actual(raw_t), get_actual(raw_d)
        mon, sao, than = d['mon'], d['sao'], d['than']

        if t_can == '甲' and d_can == '丙': cung_status[p].append(("青竜返首", "#CC0000"))
        if t_can == '丙' and d_can == '甲': cung_status[p].append(("飛鳥跌穴", "#CC0000"))
        if t_can == '丁' and p == p_land: cung_status[p].append(("玉女守門", "#CC0000"))
        if t_can == '乙' and p == 3: cung_status[p].append(("乙奇昇殿", "#CC0000"))
        if t_can == '丙' and p == 9: cung_status[p].append(("丙奇昇殿", "#CC0000"))
        if t_can == '丁' and p == 7: cung_status[p].append(("丁奇昇殿", "#CC0000")) 
        if t_can == '乙' and d_can == '己': cung_status[p].append(("乙奇得使", "#CC0000"))
        if t_can == '丙' and d_can == '戊': cung_status[p].append(("丙奇得使", "#CC0000"))
        if t_can == '丁' and d_can == '壬': cung_status[p].append(("丁奇得使", "#CC0000"))
        
        if t_can == '丙' and d_can == '戊' and mon == "生门": cung_status[p].append(("天遁", "#CC0000"))
        if t_can == '乙' and d_can == '己' and mon == "开门": cung_status[p].append(("地遁", "#CC0000"))
        if t_can == '丁' and mon == "休门" and than == "太阴": cung_status[p].append(("人遁", "#CC0000"))
        if t_can == '丙' and mon == "生门" and than == "九天": cung_status[p].append(("神遁", "#CC0000"))
        if t_can == '丁' and mon == "开门" and than == "九地": cung_status[p].append(("鬼遁", "#CC0000"))
        if (t_can == '乙' and mon == "开门") or (t_can == '乙' and p == 6 and mon in ["休门", "生门"]): cung_status[p].append(("竜遁", "#CC0000"))
        if (t_can == '乙' and mon == "生门") or (t_can == '乙' and p == 8 and mon in ["休门", "开门"]): cung_status[p].append(("虎遁", "#CC0000"))
        if t_can == '乙' and p == 4 and mon in ["休门", "生门", "开门"]: cung_status[p].append(("風遁", "#CC0000"))
        if t_can == '乙' and p == 2 and mon in ["休门", "生门", "开门"]: cung_status[p].append(("雲遁", "#CC0000"))

        if (t_can == '己' and p == 2) or (t_can == '辛' and p == 9) or (t_can == '壬' and p == 4) or (t_can == '癸' and p == 4) or (t_can == '戊' and p == 3) or (t_can == '庚' and p == 8): 
            cung_status[p].append(("六儀撃刑", "#000000"))
            
        if t_can == '乙' and p == 2: cung_status[p].append(("乙奇入墓", "#000000"))
        if t_can == '丙' and p == 6: cung_status[p].append(("丙奇入墓", "#000000"))
        if t_can == '丁' and p == 6: cung_status[p].append(("丁奇入墓", "#000000"))
        if t_can == '庚' and d_can == '癸': cung_status[p].append(("大格", "#000000"))
        if t_can == '庚' and d_can == '壬': cung_status[p].append(("小格", "#000000"))
        if t_can == '庚' and d_can == '己': cung_status[p].append(("刑格", "#000000"))
        if t_can == '庚' and d_can == '庚': cung_status[p].append(("戦格", "#000000"))
        if t_can == '庚' and d_can == '甲': cung_status[p].append(("伏宮格", "#000000"))
        if t_can == '甲' and d_can == '庚': cung_status[p].append(("飛宮格", "#000000"))
        if t_can == '乙' and d_can == '辛': cung_status[p].append(("青竜逃走", "#000000"))
        if t_can == '辛' and d_can == '乙': cung_status[p].append(("白虎猖狂", "#000000"))
        if t_can == '丙' and d_can == '庚': cung_status[p].append(("熒惑入白", "#000000"))
        if t_can == '庚' and d_can == '丙': cung_status[p].append(("太白入熒", "#000000"))
        if t_can == '丁' and d_can == '癸': cung_status[p].append(("朱雀投江", "#000000"))
        if t_can == '癸' and d_can == '丁': cung_status[p].append(("螣蛇妖嬌", "#000000"))

        if (mon == "休门" and p == 9) or (mon == "景门" and p == 7) or (mon == "生门" and p == 1) or (mon == "开门" and p == 3):
            cung_status[p].append(("八門受制", "#000000"))

        if t_can == d_can and t_can not in ['甲', '丁']: cung_status[p].append(("干伏吟", "#000000"))
        if (t_can, d_can) in [('戊','辛'), ('辛','戊'), ('己','壬'), ('壬','己'), ('庚','癸'), ('癸','庚')]:
            cung_status[p].append(("干反吟", "#000000"))

        sao_mon_goc = {"天蓬":"休门", "天芮":"死门", "天冲":"伤门", "天辅":"杜门", "天心":"开门", "天柱":"惊门", "天任":"生门", "天英":"景门"}
        mon_doi_xung = {"休门":"景门", "死门":"生门", "伤门":"惊门", "杜门":"开门", "开门":"杜门", "惊门":"伤门", "生门":"死门", "景门":"休门"}
        
        if sao in sao_mon_goc:
            if mon == sao_mon_goc[sao]: cung_status[p].append(("星門伏吟", "#000000"))
            elif mon == mon_doi_xung[sao_mon_goc[sao]]: cung_status[p].append(("星門反吟", "#000000"))

    tinh_mon_cat = {
        "天蓬": ["生门", "开门"],
        "天芮": ["休门", "景门", "开门"],
        "天冲": ["休门", "生门", "景门", "开门"],
        "天辅": ["休门", "生门", "景门"],
        "天禽": [], 
        "天心": ["休门", "生门", "景门", "开门"],
        "天柱": ["休门", "生门", "景门", "开门"],
        "天任": ["休门", "景门", "开门"],
        "天英": ["生门", "开门"]
    }
    than_cat_chung = ["值符", "太阴", "六合", "九地", "九天"]

    stem_colors, mon_colors, than_colors = {i: "#000000" for i in range(1, 10)}, {i: "#000000" for i in range(1, 10)}, {i: "#000000" for i in range(1, 10)}
    
    for p in range(1, 10):
        if p == 5 or p not in cung_data: continue
        
        t_can = '甲' if cung_data[p]['thien'] == can_tuan else cung_data[p]['thien']
        d_can = '甲' if cung_data[p]['dia'] == can_tuan else cung_data[p]['dia']
        if t_can in can_can_data and d_can in can_can_data[t_can]:
            eval_res = can_can_data[t_can][d_can]
            stem_colors[p] = "#000000" if "凶" in eval_res else "#CC0000"
            
        sao_hien_tai, mon_hien_tai = cung_data[p]['sao'], cung_data[p]['mon']
        if sao_hien_tai in tinh_mon_cat and mon_hien_tai in tinh_mon_cat[sao_hien_tai]: mon_colors[p] = "#CC0000" 
        else: mon_colors[p] = "#000000" 
            
        than_hien_tai, phi_tinh_ngay = cung_data[p]['than'], cung_data[p]['day_star'] 
        if phi_tinh_ngay != 5 and than_hien_tai in than_cat_chung: than_colors[p] = "#CC0000"
        else: than_colors[p] = "#000000"

    for p in cung_status:
        cung_status[p].sort(key=lambda x: FORMATION_RANKS.get(x[0], 99))
        formatted_list = []
        for raw_name, color in cung_status[p]:
            rank = FORMATION_RANKS.get(raw_name)
            if rank == 3: continue 
            vert_text = "<br>".join(list(raw_name))
            if rank: display_name = f"<div style='text-align: center; line-height: 1.15;'>{vert_text}<div style='font-size: 0.9em; font-weight: normal; color: #666; margin-top: 3px;'>({rank})</div></div>"
            else: display_name = f"<div style='text-align: center; line-height: 1.15;'>{vert_text}</div>"
            formatted_list.append((display_name, color))
        cung_status[p] = formatted_list

    return cung_status, stem_colors, mon_colors, than_colors

def evaluate_kigaku_formations(birth_star, view_dt, qi_men_day_stars):
    d_stars = qi_men_day_stars 
    k_data = {i: {'d_forms': [], 'stars': {}} for i in range(1, 10)}
    
    cung_ngu_hoang_d = [p for p, s in d_stars.items() if s == 5][0]
    cung_ban_menh_d = [p for p, s in d_stars.items() if s == birth_star][0]
    
    _, _, _, _, d_chi, _, _ = get_custom_lunar_day_data(view_dt.date())
    
    def vert(text, color):
        chars = "<br>".join(list(text))
        return f"<div style='color:{color}; text-align:center; font-size: 10.5px; line-height: 1.15;'>{chars}</div>"
    
    for p in range(1, 10):
        s_val = d_stars[p]
        if s_val == 5: color = "#000000"
        elif s_val in KIGAKU_COMPATIBILITY.get(birth_star, []): color = "#CC0000"
        else: color = "#999999"
        
        k_data[p]['stars']['d'] = (s_val, color) 
            
        if p == 5: continue 
            
        if p == cung_ban_menh_d: k_data[p]['d_forms'].append(vert("本命殺", "#000000"))
        if cung_ban_menh_d != 5 and p == KIGAKU_OPPOSITE[cung_ban_menh_d]: k_data[p]['d_forms'].append(vert("的殺", "#000000"))
        if p == cung_ngu_hoang_d: k_data[p]['d_forms'].append(vert("五黄殺", "#000000"))
        if cung_ngu_hoang_d != 5 and p == KIGAKU_OPPOSITE[cung_ngu_hoang_d]: k_data[p]['d_forms'].append(vert("暗剣殺", "#000000"))
        if p == KIGAKU_OPPOSITE[BRANCH_TO_PALACE[d_chi]]: k_data[p]['d_forms'].append(vert("日破", "#000000"))
        if p in [1, 9] and d_stars[p] == KIGAKU_OPPOSITE[p]: k_data[p]['d_forms'].append(vert("対冲", "#000000"))
            
    return k_data

# ==========================================
# 5. GIAO DIỆN HTML RENDER 
# ==========================================
def render_html_table(cung_data, cung_status, stem_colors, can_tuan, cung_phi_tinh, kigaku_data, final_hex_data):
    luoi_lac_thu = [[4, 9, 2], [3, 5, 7], [8, 1, 6]]
    html = """
    <style>
        .qmdj-table { border-collapse: collapse; width: 100%; max-width: 480px; min-width: 380px; height: 460px; table-layout: fixed; font-family: sans-serif; margin: 0 auto; background: #fff;}
        .qmdj-td { border: 1px solid #aaa; width: 33.33%; position: relative; vertical-align: top; padding: 6px; }
        
        .top-right-panel { position: absolute; top: 4px; right: 5px; display: flex; flex-direction: row-reverse; gap: 6px; align-items: flex-start;}
        .formation-item { display: flex; flex-direction: column; align-items: center; justify-content: flex-start; font-weight: bold; letter-spacing: 0px; color: #000; font-size: 10.5px;}
        
        .bottom-right-group { position: absolute; bottom: 8px; right: 5px; display: flex; flex-direction: row; align-items: flex-end; gap: 10px; }
        .stem-col { display: flex; flex-direction: column; align-items: center; gap: 4px; }
        
        .kigaku-col { position: absolute; top: 4px; left: 4px; display: flex; flex-direction: column; width: 65px;}
        .k-row { display: flex; flex-direction: row; align-items: flex-start; gap: 4px; padding-top: 2px;}
        .k-star { font-size: 20px; font-weight: bold; width: 15px; text-align: center; line-height: 1;}
        .k-forms { display: flex; flex-direction: row; gap: 3px; font-weight: bold; padding-top: 1.5px;}
        
        /* CSS CHO HEXAGRAM GÓC TRÁI DƯỚI */
        .bottom-left-hex { position: absolute; bottom: 8px; left: 5px; display: flex; flex-direction: row; align-items: center; width: auto; gap: 4px; }
    </style>
    <table class="qmdj-table">
    """

    for row in luoi_lac_thu:
        html += "<tr>"
        for p in row:
            d = cung_data[p]
            k_d = kigaku_data[p]
            
            t_can, d_can = d.get('thien', ''), d.get('dia', '')
            base_color = stem_colors.get(p, "#000000") 
            t_decor = "underline" if t_can == can_tuan else "none"
            d_decor = "underline" if d_can == can_tuan else "none"
            
            t_style = f"font-weight: bold; color: {base_color}; font-size: 24px; text-decoration: {t_decor}; text-underline-offset: 3px; text-decoration-thickness: 2px; line-height: 1;"
            d_style = f"font-weight: bold; color: {base_color}; font-size: 24px; text-decoration: {d_decor}; text-underline-offset: 3px; text-decoration-thickness: 2px; line-height: 1;"

            ds_val, ds_col = k_d['stars']['d']
            ds_style = f"color:{ds_col};" 
            
            kigaku_html = f"""
            <div class="kigaku-col">
                <div class="k-row"><div class="k-star" style="{ds_style}">{ds_val}</div><div class="k-forms">{"".join(k_d['d_forms'])}</div></div>
            </div>
            """

            if p == 5:
                html += f"""
                <td class="qmdj-td">
                    {kigaku_html}
                    <div class="bottom-right-group">
                        <div class="stem-col"><div style="{t_style}">{t_can}</div><div style="{d_style}">{d_can}</div></div>
                    </div>
                </td>"""
            else:
                # TẠO MÃ HTML CHO QUẺ (KÝ HIỆU BÊN TRÁI, CHỮ HÁN BÊN PHẢI)
                outer_hex_html = ""
                global_lower_tri = final_hex_data.get(p)
                if global_lower_tri:
                    out_upper_tri = TIEN_THIEN_MAP[p]
                    out_eval = EVAL_DICT.get(out_upper_tri, {}).get(global_lower_tri, "△")
                    if out_eval == "〇": out_hex_color = "#CC0000"
                    elif out_eval == "△": out_hex_color = "#B8860B"
                    else: out_hex_color = "#000000"
                    
                    outer_hex_html = f"""
                    <div class="bottom-left-hex" style="z-index: 1; color:{out_hex_color};">
                        <!-- Cột Trái: Hình ảnh Hexagram -->
                        <div style="display: flex; flex-direction: column; font-size:28px; line-height:0.85; text-align: center;">
                            <div>{TRIGRAM_UNICODE[out_upper_tri]}</div>
                            <div>{TRIGRAM_UNICODE[global_lower_tri]}</div>
                        </div>
                        <!-- Cột Phải: Chữ Hán (Thiên, Trạch, Hỏa...) -->
                        <div style="display: flex; flex-direction: column; font-size:22px; font-weight:bold; line-height:1.1;">
                            <div>{out_upper_tri}</div>
                            <div>{global_lower_tri}</div>
                        </div>
                    </div>
                    """

                form_html = "".join([f"<div class='formation-item' style='color:{f_color};'>{f_name}</div>" for f_name, f_color in cung_status[p]])
                top_right_html = f"<div class='top-right-panel'>{form_html}</div>"
                
                html += f"""
                <td class="qmdj-td">
                    {kigaku_html}
                    {top_right_html}
                    {outer_hex_html}
                    <div class="bottom-right-group">
                        <div class="stem-col"><div style="{t_style}">{t_can}</div><div style="{d_style}">{d_can}</div></div>
                    </div>
                </td>"""
        html += "</tr>"
    html += "</table>"
    return html

# ==========================================
# 6. STREAMLIT APP MAIN
# ==========================================
def get_current_vn_time(): return datetime.now(timezone(timedelta(hours=7)))
if "init_dt" not in st.session_state: st.session_state.init_dt = get_current_vn_time()

col1, col2, col3, col4, col5, col6, col7 = st.columns([1.2, 0.8, 0.8, 1.2, 0.8, 0.8, 1])

with col1: selected_date = st.date_input("Ngày Xem", value=st.session_state.init_dt.date(), min_value=date(1901, 1, 1), max_value=date(2100, 12, 31))
with col2: selected_hour = st.selectbox("Giờ Xem", options=list(range(24)), index=st.session_state.init_dt.hour)
with col3: selected_minute = st.selectbox("Phút Xem", options=list(range(60)), index=st.session_state.init_dt.minute)

with col4: birth_date = st.date_input("Ngày Sinh", value=date(1993, 1, 7), min_value=date(1901, 1, 1), max_value=date(2100, 12, 31))
with col5: birth_hour = st.selectbox("Giờ Sinh", options=list(range(24)), index=8)
with col6: birth_minute = st.selectbox("Phút Sinh", options=list(range(60)), index=15)
with col7: selected_tz = st.selectbox("Múi Giờ", options=list(range(-12, 15)), index=19, format_func=lambda x: f"UTC{'+' if x>=0 else ''}{x}")

_, _, _, _, _, _, user_birth_star, _, _ = get_custom_lunar_day_data(birth_date)

hoa_giap_60 = [thien_can[i%10] + dia_chi[i%12] for i in range(60)]
cuc_so_list = [f"阳遁{i}局" for i in range(1, 10)] + [f"阴遁{i}局" for i in range(1, 10)]

st.markdown("<div style='height: 5px;'></div>", unsafe_allow_html=True)

_, col_opt1, col_opt2, col_opt3, _ = st.columns([1.5, 2, 2, 2, 1.5])
with col_opt1: manual_hoagiap = st.selectbox("Hoa Giáp", options=["Tùy Chọn"] + hoa_giap_60)
with col_opt2: manual_cucso = st.selectbox("Cục Số", options=["Tùy Chọn"] + cuc_so_list)
with col_opt3: manual_cuutinh = st.selectbox("Cửu Tinh", options=["Tùy Chọn"] + [str(i) for i in range(1, 10)])

user_dt = datetime.combine(selected_date, time(selected_hour, selected_minute))
actual_date = user_dt.date() + timedelta(days=1) if user_dt.hour >= 23 else user_dt.date()

l_month, l_day, is_leap, wl_can, wl_chi, wl_dun, wl_ju, wl_jieqi, wl_yuan = get_custom_lunar_day_data(actual_date)
actual_daily_star = wl_ju
ngay_can_chi = wl_can + wl_chi
is_nhuan_period = is_leap 

if manual_hoagiap != "Tùy Chọn":
    wl_can = manual_hoagiap[0]
    wl_chi = manual_hoagiap[1]
    ngay_can_chi = manual_hoagiap 

if manual_cucso != "Tùy Chọn":
    wl_dun = "阳遁" if "阳" in manual_cucso else "阴遁"
    wl_ju = int(manual_cucso.replace("阳遁", "").replace("阴遁", "").replace("局", ""))

if manual_cuutinh != "Tùy Chọn":
    actual_daily_star = int(manual_cuutinh) 

data, p_circle, cung_phi_tinh, p_land = lap_que_wolong(wl_can, wl_chi, wl_dun, wl_ju, actual_daily_star)

can_tuan = get_xun_leader(wl_can, wl_chi)
cung_st, stem_colors, mon_colors, than_colors = qimen_analyzer_hojo(data, can_tuan, p_land)

title = ""
title_color = "#D4AF37" if is_nhuan_period else "#555" 
font_weight = "bold" if is_nhuan_period else "normal"
nhuan_str = "Nhuận " if is_nhuan_period else ""

sub_title = f"<h4 style='margin-top:0px; margin-bottom:15px; font-family:sans-serif; color: {title_color}; font-weight: {font_weight}; font-size: 16px; text-align: center;'>阴历: {nhuan_str}{l_day}/{l_month} | {ngay_can_chi}日 | {wl_jieqi} {wl_yuan}元 | {wl_dun}{wl_ju}局</h4>"

cung_day_stars = {p: data[p]['day_star'] for p in range(1, 10)}
kigaku_data = evaluate_kigaku_formations(user_birth_star, user_dt, cung_day_stars)

# Lấy quẻ theo Phi Tinh Ngày
global_lower_gate_final = data[cung_phi_tinh]['mon']
global_lower_tri_final = GATE_TO_TRIGRAM.get(global_lower_gate_final, "天")
final_hex_data = {}
for p in range(1, 10):
    if p != 5: final_hex_data[p] = global_lower_tri_final

qimen_board_html = render_html_table(data, cung_st, stem_colors, can_tuan, cung_phi_tinh, kigaku_data, final_hex_data)

combined_html = f"""<div style="display: flex; flex-direction: column; align-items: center; width: 100%; padding-top: 10px;"><div style="display: flex; flex-direction: column; align-items: center; width: 100%; max-width: 510px;">{title}{sub_title}{qimen_board_html}</div></div>"""
st.components.v1.html(combined_html, height=550, scrolling=True)


# ==========================================
# 7. MODULE SCAN: DỤNG SỰ (TÌM KIẾM THEO NGÀY)
# ==========================================
st.markdown("---")
st.markdown("<h3 style='text-align: center; color: #333; font-family: sans-serif; margin-bottom: 20px;'>DỤNG SỰ</h3>", unsafe_allow_html=True)

FORMATION_RANKS_LOCAL = {
    "天遁": 1, "地遁": 1, "人遁": 1, "神遁": 1, "鬼遁": 1,
    "大格": 1, "小格": 1, "刑格": 1, "戦格": 1, "飛宮格": 1, "伏宮格": 1, 
    "青竜逃走": 1, "白虎猖狂": 1, "熒惑入白": 1, "太白入熒": 1, "朱雀投江": 1, "螣蛇妖嬌": 1,
    "青竜返首": 2, "飛鳥跌穴": 2, "玉女守門": 2, "乙奇得使": 2, "丙奇得使": 2, "丁奇得使": 2, 
    "竜遁": 2, "虎遁": 2, "風遁": 2, "雲遁": 2, 
    "乙奇入墓": 2, "丙奇入墓": 2, "丁奇入墓": 2,
    "干伏吟": 2, "干反吟": 2, 
    "乙奇昇殿": 3, "丙奇昇殿": 3, "丁奇昇殿": 3,
    "星門伏吟": 3, "星門反吟": 3, "八门受制": 3, "六儀撃刑": 3
}

def format_ui_list(raw_list):
    valid_items = [x for x in raw_list if x != ""]
    valid_items.sort(key=lambda x: (FORMATION_RANKS_LOCAL.get(x, 99), x))
    res = [""]
    for x in valid_items:
        rank = FORMATION_RANKS_LOCAL.get(x)
        if rank: res.append(f"({rank}) {x}")
        else: res.append(x)
    return res

def extract_raw_name(ui_name):
    if not ui_name: return ""
    return ui_name.split(") ")[1] if ") " in ui_name else ui_name

huong_list = {"": None, "坎 (345 - 15)": 1, "艮 (15 - 75)": 8, "震 (75 - 105)": 3, "巽 (105 - 165)": 4, "離 (165 - 195)": 9, "坤 (195 - 255)": 2, "兌 (255 - 285)": 7, "乾 (285 - 345)": 6}
can_list = ["", "甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
mon_list = ["", "休门", "生门", "伤门", "杜门", "景门", "死门", "惊门", "开门"]
tinh_list = ["", "天蓬", "天芮", "天冲", "天辅", "天禽", "天心", "天柱", "天任", "天英"]
than_list = ["", "值符", "螣蛇", "太阴", "六合", "勾陈", "朱雀", "九地", "九天"]
cat_cach_list = format_ui_list(["青竜返首", "飛鳥跌穴", "玉女守門", "乙奇昇殿", "丙奇昇殿", "丁奇昇殿", "天遁", "地遁", "人遁", "神遁", "鬼遁", "竜遁", "虎遁", "風遁", "雲遁"])

TRAN_HUNG_DICT = {
    "大格": (["地遁"], ["乙奇得使", "竜遁", "虎遁", "風遁", "雲遁"]),
    "小格": (["地遁"], ["乙奇得使", "竜遁", "虎遁", "風遁", "雲遁"]),
    "刑格": (["地遁"], ["乙奇得使", "竜遁", "虎遁", "風遁", "雲遁"]),
    "戦格": (["地遁"], ["乙奇得使", "竜遁", "虎遁", "風遁", "雲遁"]),
    "伏宮格": (["地遁"], ["乙奇得使", "竜遁", "虎遁", "風遁", "雲遁"]),
    "太白入熒": (["地遁"], ["乙奇得使", "竜遁", "虎遁", "風遁", "雲遁"]),
    "飛宮格": (["人遁", "鬼遁"], ["玉女守門", "天盤丙", "乙奇得使", "丁奇得使"]),
    "青竜逃走": (["人遁", "鬼遁"], ["玉女守門", "天盤丙", "乙奇得使", "丁奇得使"]),
    "白虎猖狂": (["天遁", "神遁"], ["飛鳥跌穴", "丙奇得使"]),
    "螣蛇妖嬌": (["天遁", "地遁", "神遁"], ["飛鳥跌穴", "乙奇得使", "丙奇得使", "竜遁", "虎遁", "風遁", "雲遁"]),
    "乙奇入墓": (["人遁", "鬼遁", "玉女守門", "丁奇得使"], ["丁奇昇殿"]),
    "干伏吟": (["青竜返首"], []), "干反吟": (["青竜返首"], []),
    "熒惑入白": ([], []), "朱雀投江": ([], []), "丙奇入墓": ([], []), "丁奇入墓": ([], [])
}

THOI_CAT_DICT = {
    "青竜返首": (["青竜返首"], []), "乙奇得使": (["青竜返首"], []),
    "地遁": (["青竜返首"], []), "竜遁": (["青竜返首"], []), "虎遁": (["青竜返首"], []),
    "風遁": (["青竜返首"], []), "雲遁": (["青竜返首"], []),
    "飛鳥跌穴": (["地遁", "乙奇得使", "竜遁", "虎遁", "風遁", "雲遁"], ["乙奇昇殿"]),
    "玉女守門": (["地遁", "青竜返首", "乙奇得使", "竜遁", "虎遁", "風遁", "雲遁"], ["乙奇昇殿"]),
    "丙奇得使": (["地遁", "乙奇得使", "竜遁", "虎遁", "風遁", "雲遁"], ["乙奇昇殿"]),
    "丁奇得使": (["地遁", "青竜返首", "乙奇得使", "竜遁", "虎遁", "風遁", "雲遁"], ["乙奇昇殿"]),
    "天遁": (["地遁"], ["乙奇得使", "竜遁", "虎遁", "風遁", "雲遁"]),
    "神遁": (["地遁"], ["乙奇得使", "竜遁", "虎遁", "風遁", "雲遁"]),
    "人遁": (["地遁"], ["青竜返首", "乙奇得使", "竜遁", "虎遁", "風遁", "雲遁"]),
    "鬼遁": (["地遁"], ["青竜返首", "乙奇得使", "竜遁", "虎遁", "風遁", "雲遁"])
}

tran_hung_list = format_ui_list(list(TRAN_HUNG_DICT.keys()))
thoi_cat_list = format_ui_list(list(THOI_CAT_DICT.keys()))

with st.container():
    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    _, c1, c2, c3, c4, c5, c6, _ = st.columns([0.5, 1, 1, 1, 1, 1, 1, 0.5])
    loc_huong = c1.selectbox("方向 (Hướng)", options=list(huong_list.keys()))
    loc_thien_can = c2.selectbox("天盤 (Thiên Bàn)", options=can_list)
    loc_dia_can = c3.selectbox("地盤 (Địa Bàn)", options=can_list)
    loc_mon = c4.selectbox("八门 (Bát Môn)", options=mon_list)
    loc_tinh = c5.selectbox("九星 (Cửu Tinh)", options=tinh_list)
    loc_than = c6.selectbox("八神 (Bát Thần)", options=than_list)
    
    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    _, c9, c10, c11, c12, _ = st.columns([1.5, 1, 1, 1, 1, 1.5])
    loc_tran_hung = c9.selectbox("鎮凶 (Trấn Hung)", options=tran_hung_list)
    loc_thoi_cat = c10.selectbox("催吉 (Thôi Cát)", options=thoi_cat_list)
    loc_thien_thoi = c11.selectbox("天时 (Thiên Thời)", options=["", "Có"])
    loc_cat_cach = c12.selectbox("吉格 (Cát Cách)", options=cat_cach_list)

def find_fulfilled_plan(plan_list, d_cung, status_cung, can_tuan_scan):
    clean_status = [re.sub(r"<[^>]+>", "", item[0]) for item in status_cung]
    for req in plan_list:
        if req == "天盤丙":
            t_chk = '甲' if d_cung['thien'] == can_tuan_scan else d_cung['thien']
            if t_chk == '丙': return "Thiên Bàn Bính"
        else:
            if any(req in clean_name for clean_name in clean_status): return req
    return None

if st.button("TÌM KIẾM", use_container_width=True):
    val_tran_hung = extract_raw_name(loc_tran_hung)
    val_thoi_cat = extract_raw_name(loc_thoi_cat)
    
    if val_tran_hung and val_thoi_cat:
        st.error("Vui lòng không chọn cùng lúc Trấn Hung và Thôi Cát.")
    else:
        with st.spinner('Đang quét dữ liệu tương lai (Quét từng ngày một)...'):
            results = []
            max_limit = 365 
            current_scan_dt = datetime.combine(selected_date, time(selected_hour, selected_minute))
            
            loops = 0
            while loops < max_limit: 
                if len(results) >= 10: break 
                
                loops += 1
                current_scan_dt += timedelta(days=1)
                s_date = current_scan_dt.date()
                
                l_month_s, l_day_s, is_leap_s, can_ngay_scan, chi_ngay_scan, wl_dun_s, wl_ju_s, wl_jieqi_s, wl_yuan_s = get_custom_lunar_day_data(s_date)
                
                scan_data, p_circle_scan, cung_phi_tinh_scan, p_land_scan = lap_que_wolong(can_ngay_scan, chi_ngay_scan, wl_dun_s, wl_ju_s, wl_ju_s)
                can_tuan_scan = get_xun_leader(can_ngay_scan, chi_ngay_scan)
                cung_st_scan, stem_colors_scan, mon_colors_scan, than_colors_scan = qimen_analyzer_hojo(scan_data, can_tuan_scan, p_land_scan)
                
                cung_day_stars_scan = {p: scan_data[p]['day_star'] for p in range(1, 10)}
                kigaku_data_scan = evaluate_kigaku_formations(user_birth_star, current_scan_dt, cung_day_stars_scan)
                
                time_str = f"{current_scan_dt.strftime('%d/%m/%Y')}"
                nhuan_s_str = "Nhuận " if is_leap_s else ""
                c_str = f"阴历: {nhuan_s_str}{l_day_s}/{l_month_s} | {can_ngay_scan}{chi_ngay_scan}日 | {wl_dun_s}{wl_ju_s}局"
                val_cat_cach = extract_raw_name(loc_cat_cach)

                target_palace = huong_list[loc_huong] 

                def check_match(p):
                    d = scan_data[p]
                    t_chk = '甲' if d['thien'] == can_tuan_scan else d['thien']
                    d_chk = '甲' if d['dia'] == can_tuan_scan else d['dia']
                    
                    if loc_thien_can and t_chk != loc_thien_can: return False, ""
                    if loc_dia_can and d_chk != loc_dia_can: return False, ""
                    if loc_mon and d['mon'] != loc_mon: return False, ""
                    if loc_tinh and d['sao'] != loc_tinh: return False, ""
                    if loc_than and d['than'] != loc_than: return False, ""
                    
                    if val_cat_cach:
                        clean_status_scan = [re.sub(r"<[^>]+>", "", item[0]) for item in cung_st_scan[p]]
                        if not any(val_cat_cach in clean_name for clean_name in clean_status_scan): return False, ""
                        
                    if loc_thien_thoi == "Có":
                        if stem_colors_scan.get(p, "#000000") == "#000000": return False, ""
                        
                    dung_cach = ""
                    if val_tran_hung or val_thoi_cat:
                        pa1_reqs, pa2_reqs = TRAN_HUNG_DICT[val_tran_hung] if val_tran_hung else THOI_CAT_DICT[val_thoi_cat]
                        f1 = find_fulfilled_plan(pa1_reqs, d, cung_st_scan[p], can_tuan_scan) if pa1_reqs else None
                        f2 = find_fulfilled_plan(pa2_reqs, d, cung_st_scan[p], can_tuan_scan) if pa2_reqs else None
                        if not f1 and not f2: return False, "" 
                        dung_cach = f1 if f1 else f2 
                        
                    return True, dung_cach

                is_match = False
                matched_cach = ""
                
                if target_palace:
                    if target_palace != 5: 
                        is_match, matched_cach = check_match(target_palace)
                else:
                    for p in range(1, 10):
                        if p == 5: continue
                        is_match, matched_cach = check_match(p)
                        if is_match:
                            target_palace = p
                            break
                            
                if is_match:
                    ten_cung = [k for k, v in huong_list.items() if v == target_palace][0]
                    cach_cuc_cua_cung = cung_st_scan[target_palace]

                    global_lower_gate_scan = scan_data[cung_phi_tinh_scan]['mon']
                    global_lower_tri_scan = GATE_TO_TRIGRAM.get(global_lower_gate_scan, "天")
                    
                    out_upper_tri = TIEN_THIEN_MAP.get(target_palace, "天")
                    out_eval = EVAL_DICT.get(out_upper_tri, {}).get(global_lower_tri_scan, "△")
                    if out_eval == "〇": out_hex_color = "#CC0000"
                    elif out_eval == "△": out_hex_color = "#B8860B"
                    else: out_hex_color = "#000000"
                    out_hex_name = HEX_NAME_DICT.get((out_upper_tri, global_lower_tri_scan), "Không rõ")
                    
                    hex_html = f" | <span style='color:{out_hex_color}; font-weight:bold;'> {TRIGRAM_UNICODE[out_upper_tri]}/{TRIGRAM_UNICODE[global_lower_tri_scan]} {out_hex_name}</span>"
                    
                    d_star_val, d_star_col = kigaku_data_scan[target_palace]['stars']['d']
                    raw_d_forms = kigaku_data_scan[target_palace]['d_forms']
                    
                    flat_d_forms = []
                    for form_html in raw_d_forms:
                        color_match = re.search(r"color:(#[0-9a-fA-F]{6})", form_html)
                        color = color_match.group(1) if color_match else "#000000"
                        text = re.sub(r"<[^>]+>", "", form_html) 
                        flat_d_forms.append(f"<span style='color:{color}; font-weight:bold;'>{text}</span>")
                    
                    d_style = f"color:{d_star_col}; font-weight:bold; font-size:16px;"
                    
                    kigaku_result_html = f"<br>↳ <i>Khí Học Nhật Tinh:</i> <span style='{d_style}'>{d_star_val}</span>"
                    if flat_d_forms:
                        kigaku_result_html += " (" + ", ".join(flat_d_forms) + ")"
                    
                    results.append((time_str, c_str, ten_cung, matched_cach, cach_cuc_cua_cung, kigaku_result_html, hex_html))

            if results:
                st.success(f"**TÌM THẤY {len(results)} KẾT QUẢ:**")
                for idx, (t_str, canchi_str, cung_str, d_cach, cach_cuc_cua_cung, kigaku_html, hex_html) in enumerate(results):
                    h_text = f" | Hướng: {cung_str}" if cung_str else ""
                    cach_text = f" | Dùng: **{d_cach}**" if d_cach else ""
                    
                    cach_cuc_html = ""
                    if cach_cuc_cua_cung:
                        list_html = []
                        for name, color in cach_cuc_cua_cung:
                            clean_name = re.sub(r"<[^>]+>", "", name)
                            list_html.append(f"<span style='color:{color}; font-weight:bold;'>{clean_name}</span>")
                        cach_cuc_html = " ➔ " + ", ".join(list_html)
                        
                    st.markdown(f"{idx+1}. {t_str} | {canchi_str}{h_text}{hex_html}{cach_text}{cach_cuc_html}{kigaku_html}", unsafe_allow_html=True)
                    st.markdown("<div style='height: 5px;'></div>", unsafe_allow_html=True)
            else:
                st.warning("Không tìm thấy ngày nào thỏa mãn TẤT CẢ các điều kiện trong 1 năm tới.")
