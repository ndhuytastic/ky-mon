import streamlit as st
import sxtwl
from datetime import datetime, timedelta, timezone
import warnings

warnings.filterwarnings('ignore')

st.set_page_config(page_title="Kỳ Môn Chuyển Bàn", layout="wide", initial_sidebar_state="collapsed")

# ==========================================
# 1. HỆ THỐNG DỮ LIỆU CƠ BẢN
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

# --- CÁC HẰNG SỐ MỚI (CHUYỂN BÀN - 10 CAN) ---
THIEN_CAN = "甲乙丙丁戊己庚辛壬癸"
DIA_CHI = "子丑寅卯辰巳午未申酉戌亥"
OUTER_PALACES = [4, 9, 2, 7, 6, 1, 8, 3]
FLYING_PATH = [5, 6, 7, 8, 9, 1, 2, 3, 4]
NUM_TO_STEM = {1: "癸", 2: "丁", 3: "丙", 4: "乙", 5: "戊", 6: "己", 7: "庚", 8: "辛", 9: "壬", 0: "甲"}
ORIGINAL_GATES = {1: "休门", 8: "生门", 3: "伤门", 4: "杜门", 9: "景门", 2: "死门", 7: "惊门", 6: "开门"}
CLOCKWISE_GATES = ["景门", "死门", "惊门", "开门", "休门", "生门", "伤门", "杜门"]

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
    # Đã bỏ điều kiện ["芒种", "大雪"], giờ sẽ lấy bất kỳ tiết khí nào gần nhất
    start_offset = 0 if include_start else 1
    for i in range(start_offset, 250): 
        check_date = start_date - timedelta(days=i)
        day_obj = sxtwl.fromSolar(check_date.year, check_date.month, check_date.day)
        if day_obj.hasJieQi():
            jq_idx = day_obj.getJieQi()
            return check_date, jq_names[jq_idx]
    return None, None

def run_trinhuan_algorithm(D, T_tram_date, T_tram_name, T_prev_tram_date):
    # 1. Tìm Phù Đầu và tính khoảng cách Siêu Thần (Chao Shen)
    F_past = get_phu_dau(T_tram_date)
    chao_shen = (T_tram_date - F_past).days
    
    is_leap = False
    is_fake_tie_qi = False

    # 2. Xét điều kiện Nhuận (Siêu Thần >= 9)
    if chao_shen >= 9:
        F_prev_past = get_phu_dau(T_prev_tram_date)
        chao_shen_prev = (T_prev_tram_date - F_prev_past).days
        if chao_shen_prev >= 9: 
            is_fake_tie_qi = True  # Bỏ qua nhuận ảo (Tiếp Khí)
        else: 
            is_leap = True         # Kích hoạt NHUẬN THẬT

    Start_Line = F_past + timedelta(days=15) if is_fake_tie_qi else F_past

    # 3. Xử lý đệ quy nếu ngày xem nằm trước mốc Start_Line
    if D < Start_Line:
        T_prev2_tram_date, _ = get_station(T_prev_tram_date, include_start=False)
        day_prev_obj = sxtwl.fromSolar(T_prev_tram_date.year, T_prev_tram_date.month, T_prev_tram_date.day)
        T_prev_tram_name = jq_names[day_prev_obj.getJieQi()]
        return run_trinhuan_algorithm(D, T_prev_tram_date, T_prev_tram_name, T_prev2_tram_date)

    # =========================================================
    # 4. LOGIC MỚI: TÍNH CỤC VÀ NGUYÊN DỰA TRÊN KHỐI 5 NGÀY
    # =========================================================
    delta_days = (D - Start_Line).days
    
    # Chia thời gian thành các khối 5 ngày (chunk)
    chunk_5d = delta_days // 5 
    station_idx = jq_names.index(T_tram_name)
    
    is_nhuan_hien_tai = False

    if is_leap:
        # NẾU CÓ NHUẬN
        if chunk_5d == 0:
            # --- KHÚC NHUẬN (5 ngày đầu tiên) ---
            # Lùi lại Tiết Khí trước đó
            final_idx = (station_idx - 1) % 24
            # Mặc định khúc Nhuận là Thượng Nguyên (0)
            nguyen_index = 0
            
            is_nhuan_hien_tai = True
        else:
            # --- SAU KHI HẾT NHUẬN (Từ ngày thứ 6 trở đi) ---
            # Trừ đi 1 chunk (đã dùng cho Nhuận) để bắt đầu tính Tiết Khí mới
            adjusted_chunk = chunk_5d - 1
            
            # 3 chunk (15 ngày) tạo thành 1 Tiết Khí
            final_idx = (station_idx + (adjusted_chunk // 3)) % 24
            
            # Luân phiên Thượng(0) -> Trung(1) -> Hạ(2) cho Tiết Khí mới
            nguyen_index = adjusted_chunk % 3
            
            is_nhuan_hien_tai = False
    else:
        # NẾU KHÔNG CÓ NHUẬN
        # Chạy lịch bình thường, cứ 3 chunk đổi 1 Tiết
        final_idx = (station_idx + (chunk_5d // 3)) % 24
        nguyen_index = chunk_5d % 3

    final_term = jq_names[final_idx]
    
    return final_term, nguyen_index, is_nhuan_hien_tai


# ==========================================
# 2B. CÁC HÀM TÍNH TOÁN BỔ SUNG ĐỘC LẬP 
# ==========================================
def get_cung_phi_tinh(nhat_chi, thoi_chi, loai_don):
    col_map = {"子":0, "午":0, "卯":0, "酉":0, "丑":1, "未":1, "辰":1, "戌":1, "寅":2, "申":2, "巳":2, "亥":2}
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


# ==========================================
# 3. THUẬT TOÁN HỖN HỢP PHI - CHUYỂN
# ==========================================
def get_xun_leader(can_gio, chi_gio):
    idx_can, idx_chi = THIEN_CAN.index(can_gio), DIA_CHI.index(chi_gio)
    return {"子":"戊", "戌":"己", "申":"庚", "午":"辛", "辰":"壬", "寅":"癸"}[DIA_CHI[(idx_chi - idx_can) % 12]]

def an_dia_ban(dun_type, ju_num):
    dia_ban = {}
    if dun_type == "阳遁":
        current_val = (10 - ju_num) 
        step_dir = 1
    else:
        current_val = ju_num
        step_dir = -1

    for cung in FLYING_PATH:
        stem_val = current_val % 10 if current_val % 10 != 0 else 0
        dia_ban[cung] = NUM_TO_STEM.get(stem_val, "")
        current_val += step_dir
        if current_val > 9: current_val = 1
        if current_val < 1: current_val = 9
    return dia_ban

def an_thien_ban(dia_ban, can_gio, chi_gio):
    thien_ban = {i: "" for i in range(1, 10)}
    luc_nghi_gio = get_xun_leader(can_gio, chi_gio)
    
    p_circle_list = [c for c, can in dia_ban.items() if can == luc_nghi_gio]
    p_circle = p_circle_list[0] if p_circle_list else 5
    
    p_hour_stem_list = [c for c, can in dia_ban.items() if can == can_gio]
    p_hour_stem = p_hour_stem_list[0] if p_hour_stem_list else 5

    if p_circle == 5:
        for i in OUTER_PALACES: 
            thien_ban[i] = dia_ban[i]
        if p_hour_stem != 5: 
            thien_ban[p_hour_stem] = luc_nghi_gio
    else:
        idx_source = OUTER_PALACES.index(p_circle)
        idx_target = OUTER_PALACES.index(p_hour_stem) if p_hour_stem != 5 else idx_source
        offset = (idx_target - idx_source) % 8
        
        for i in range(8):
            target_palace = OUTER_PALACES[i]
            source_palace = OUTER_PALACES[(i - offset) % 8]
            thien_ban[target_palace] = dia_ban[source_palace]

    thien_ban[5] = ""
    return thien_ban, p_circle, p_hour_stem

def an_bat_mon(p_circle, can_gio, dun_type):
    bat_mon = {i: "" for i in range(1, 10)}
    
    if p_circle == 5:
        for p, door in ORIGINAL_GATES.items(): 
            bat_mon[p] = door
        return bat_mon

    g_start = ORIGINAL_GATES[p_circle]
    s_steps = THIEN_CAN.index(can_gio) + 1
    seq = [1,2,3,4,5,6,7,8,9] if dun_type == "阳遁" else [9,8,7,6,5,4,3,2,1]
    
    start_idx_in_seq = seq.index(p_circle)
    p_land = seq[(start_idx_in_seq + s_steps - 1) % 9]

    if p_land == 5:
        for p, door in ORIGINAL_GATES.items(): 
            bat_mon[p] = door
    else:
        idx_land = OUTER_PALACES.index(p_land)
        idx_gate = CLOCKWISE_GATES.index(g_start)
        
        for i in range(8):
            target_palace = OUTER_PALACES[(idx_land + i) % 8]
            door_to_place = CLOCKWISE_GATES[(idx_gate + i) % 8]
            bat_mon[target_palace] = door_to_place

    return bat_mon

def lap_que(hoa_giap_gio, nhat_chi, loai_don, so_cuc, can_thang, can_ngay, chi_thang):
    can_gio, chi_gio = hoa_giap_gio[0], hoa_giap_gio[1]

    cung_data = {i: {'dia': '', 'sao': '', 'mon': '', 'than': '', 'thien': '', 'phi_tinh': 0} for i in range(1, 10)}

    # PHI TINH TRUNG CUNG
    center_num = get_cung_phi_tinh(nhat_chi, chi_gio, loai_don)
    quydo_luoshu = [5, 6, 7, 8, 9, 1, 2, 3, 4]
    curr_num = center_num
    for p in quydo_luoshu:
        cung_data[p]['phi_tinh'] = curr_num
        curr_num = (curr_num % 9) + 1  

    # 1. ĐỊA BÀN
    dia_ban = an_dia_ban(loai_don, so_cuc)
    for i in range(1, 10): 
        cung_data[i]['dia'] = dia_ban[i]

    # 2. THIÊN BÀN CAN
    thien_ban, p_circle, p_hour_stem = an_thien_ban(dia_ban, can_gio, chi_gio)
    for i in range(1, 10):
        cung_data[i]['thien'] = thien_ban[i]

    # 3. BÁT MÔN
    bat_mon = an_bat_mon(p_circle, can_gio, loai_don)
    for i in range(1, 10):
        cung_data[i]['mon'] = bat_mon[i]

    # 4. THIÊN BÀN TINH (Phi Bàn)
    base_star_p = p_circle
    target_star_p = p_hour_stem
    
    star_path_forward = luoshu_9  
    idx_base_star_fwd = star_path_forward.index(base_star_p)
    idx_target_star_fwd = star_path_forward.index(target_star_p)
    shift_for_star = (idx_target_star_fwd - idx_base_star_fwd) % 9
    
    for i in range(9):
        p_star = star_path_forward[i]
        orig_idx_star = (i - shift_for_star) % 9
        orig_p_star = star_path_forward[orig_idx_star]
        cung_data[p_star]['sao'] = star_native[orig_p_star - 1]

    # 5. BÁT THẦN (Chuyển Bàn - dùng Câu Trần, Chu Tước cho cả 2)
    deity_target = p_hour_stem
    if deity_target == 5:
        deity_target = p_circle
        if deity_target == 5:
            deity_target = 2 
            
    idx_deity_target = OUTER_PALACES.index(deity_target)
    
    deities = ["值符", "螣蛇", "太阴", "六合", "勾陈", "朱雀", "九地", "九天"]
    
    if loai_don == "阳遁":
        for i in range(8):
            palace = OUTER_PALACES[(idx_deity_target + i) % 8]
            cung_data[palace]['than'] = deities[i]
    else:
        for i in range(8):
            palace = OUTER_PALACES[(idx_deity_target - i) % 8]
            cung_data[palace]['than'] = deities[i]
            
    cung_data[5]['than'] = ""

    return cung_data


# ==========================================
# 4. MODULE ĐỘC LẬP: PHÂN TÍCH CÁCH CỤC
# ==========================================
def qimen_analyzer(cung_data, can_ngay, can_gio, can_tuan, truc_su_door=None):
    toan_ban_status = []
    cung_status = {i: [] for i in range(1, 10)}
    cung_3_elements = {i: [] for i in range(1, 10)} 

    # --- TỪ ĐIỂN CÁT HUNG ---
    than_cung_data = {
        '值符':{1:'吉',2:'吉',3:'吉',4:'吉',5:'凶',6:'吉',7:'吉',8:'吉',9:'吉'}, 
        '螣蛇':{1:'凶',2:'凶',3:'凶',4:'凶',5:'凶',6:'凶',7:'凶',8:'凶',9:'凶'}, 
        '太阴':{1:'吉',2:'吉',3:'吉',4:'吉',5:'凶',6:'吉',7:'吉',8:'吉',9:'吉'}, 
        '六合':{1:'吉',2:'吉',3:'吉',4:'吉',5:'凶',6:'吉',7:'吉',8:'吉',9:'吉'}, 
        '勾陈':{1:'凶',2:'凶',3:'凶',4:'凶',5:'凶',6:'凶',7:'凶',8:'凶',9:'凶'}, 
        '朱雀':{1:'凶',2:'凶',3:'凶',4:'凶',5:'凶',6:'凶',7:'凶',8:'凶',9:'凶'}, 
        '九地':{1:'吉',2:'吉',3:'吉',4:'吉',5:'凶',6:'吉',7:'吉',8:'吉',9:'吉'}, 
        '九天':{1:'吉',2:'吉',3:'吉',4:'吉',5:'凶',6:'吉',7:'吉',8:'吉',9:'吉'}
    }
    mon_sao_data = {'休门':{'天蓬':'凶','天芮':'吉','天冲':'吉','天辅':'吉','天禽':'凶','天心':'吉','天柱':'吉','天任':'吉','天英':'凶'}, '生门':{'天蓬':'吉','天芮':'凶','天冲':'吉','天辅':'吉','天禽':'凶','天心':'吉','天柱':'吉','天任':'凶','天英':'吉'}, '伤门':{'天蓬':'凶','天芮':'凶','天冲':'凶','天辅':'凶','天禽':'凶','天心':'凶','天柱':'凶','天任':'凶','天英':'凶'}, '杜门':{'天蓬':'凶','天芮':'凶','天冲':'凶','天辅':'凶','天禽':'凶','天心':'凶','天柱':'凶','天任':'凶','天英':'凶'}, '景门':{'天蓬':'凶','天芮':'吉','天冲':'吉','天辅':'吉','天禽':'凶','天心':'吉','天柱':'吉','天任':'吉','天英':'凶'}, '死门':{'天蓬':'凶','天芮':'凶','天冲':'凶','天辅':'凶','天禽':'凶','天心':'凶','天柱':'凶','天任':'凶','天英':'凶'}, '惊门':{'天蓬':'凶','天芮':'凶','天冲':'凶','天辅':'凶','天禽':'凶','天心':'凶','天柱':'凶','天任':'凶','天英':'凶'}, '开门':{'天蓬':'吉','天芮':'吉','天冲':'吉','天辅':'凶','天禽':'凶','天心':'凶','天柱':'吉','天任':'吉','天英':'吉'}}
    can_can_data = {'甲':{'甲':'吉','乙':'吉','丙':'吉','丁':'吉','戊':'凶','己':'吉','庚':'大凶','辛':'凶','壬':'凶','癸':'吉'}, '乙':{'甲':'吉','乙':'凶','丙':'吉','丁':'吉','戊':'吉','己':'吉','庚':'凶','辛':'大凶','壬':'吉','癸':'凶'}, '丙':{'甲':'吉','乙':'吉','丙':'凶','丁':'吉','戊':'吉','己':'吉','庚':'大凶','辛':'吉','壬':'吉','癸':'凶'}, '丁':{'甲':'吉','乙':'吉','丙':'吉','丁':'吉','戊':'吉','己':'凶','庚':'吉','辛':'凶','壬':'吉','癸':'大凶'}, '戊':{'甲':'凶','乙':'吉','丙':'吉','丁':'吉','戊':'凶','己':'凶','庚':'凶','辛':'凶','壬':'吉','癸':'凶'}, '己':{'甲':'凶','乙':'吉','丙':'凶','丁':'凶','戊':'吉','己':'凶','庚':'凶','辛':'凶','壬':'凶','癸':'凶'}, '庚':{'甲':'大凶','乙':'凶','丙':'大凶','丁':'吉','戊':'凶','己':'大凶','庚':'大凶','辛':'凶','壬':'大凶','癸':'大凶'}, '辛':{'甲':'凶','乙':'大凶','丙':'凶','丁':'吉','戊':'凶','己':'凶','庚':'凶','辛':'凶','壬':'凶','癸':'凶'}, '壬':{'甲':'凶','乙':'凶','丙':'凶','丁':'吉','戊':'吉','己':'凶','庚':'凶','辛':'吉','壬':'凶','癸':'凶'}, '癸':{'甲':'吉','乙':'凶','丙':'吉','丁':'大凶','戊':'吉','己':'凶','庚':'大凶','辛':'凶','壬':'凶','癸':'凶'}}

    # --- ĐỊNH NGHĨA TINH MÔN PHỤC / PHẢN THEO ẢNH ---
    xing_men_fuyin = {
        '天蓬': '休门', '天芮': '死门', '天冲': '伤门', '天辅': '杜门', 
        '天心': '开门', '天柱': '惊门', '天任': '生门', '天英': '景门'
    }
    xing_men_fanyin = {
        '天蓬': '景门', '天任': '死门', '天冲': '惊门', '天辅': '开门', 
        '天英': '休门', '天芮': '生门', '天柱': '伤门', '天心': '杜门'
    }

    # --- A. TOÀN BÀN & THỜI GIAN (Trung Cung) ---
    ngu_bat_ngo = {'甲':'庚', '乙':'辛', '丙':'壬', '丁':'癸', '戊':'甲', '己':'乙', '庚':'丙', '辛':'丁', '壬':'戊', '癸':'己'}
    if ngu_bat_ngo.get(can_ngay) == can_gio: toan_ban_status.append("五不遇时")

    # --- B. XÉT TỪNG CUNG ---
    for p, d in cung_data.items():
        if p == 5: continue 
        
        t_can = d['thien']
        d_can = d['dia']
        mon, sao, than, phi_tinh = d['mon'], d['sao'], d['than'], d['phi_tinh']

        # 1. KIỂM TRA TINH MÔN PHỤC NGÂM / PHẢN NGÂM
        if xing_men_fuyin.get(sao) == mon:
            cung_status[p].append(("星門伏吟", "#000000"))
        if xing_men_fanyin.get(sao) == mon:
            cung_status[p].append(("星門反吟", "#000000"))

        # 2. XÉT CÁC CÁCH CỤC
        if t_can == '甲' and d_can == '丙': cung_status[p].append(("青竜返首", "#CC0000"))
        if t_can == '丙' and d_can == '甲': cung_status[p].append(("飛鳥跌穴", "#CC0000"))
        if truc_su_door and t_can == '丁' and mon == truc_su_door: cung_status[p].append(("玉女守門", "#CC0000"))
        if t_can == '乙' and p == 3: cung_status[p].append(("乙奇昇殿", "#CC0000"))
        if t_can == '丙' and p == 9: cung_status[p].append(("丙奇昇殿", "#CC0000"))
        if t_can == '丁' and p == 9: cung_status[p].append(("丁奇昇殿", "#CC0000"))
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

        if (t_can == '戊' and p == 3) or (t_can == '己' and p == 2) or \
           (t_can == '庚' and p == 8) or (t_can == '辛' and p == 9) or \
           (t_can == '壬' and p == 4) or (t_can == '癸' and p == 4): cung_status[p].append(("六儀擊刑", "#000000"))
        
        if (t_can == '丙' and d_can == can_ngay) or (t_can == can_ngay and d_can == '丙'): cung_status[p].append(("悖格", "#000000"))
        if t_can == can_ngay and d_can == '庚': cung_status[p].append(("飛干", "#000000"))
        if t_can == '庚' and d_can == can_ngay: cung_status[p].append(("伏干", "#000000"))
        
        if t_can and d_can and t_can == d_can and t_can not in ['甲', '丁']: cung_status[p].append(("干伏吟", "#000000"))
        if (t_can, d_can) in [('戊','辛'), ('辛','戊'), ('己','壬'), ('壬','己'), ('庚','癸'), ('癸','庚')]: cung_status[p].append(("干反吟", "#000000"))
        
        # MÔN BỨC / MÔN THỤ CHẾ (Chỉ áp dụng cho 4 cửa: Hưu, Cảnh, Sinh, Khai)
        mon_bach_rules = {"休门": [9], "景门": [6, 7], "生门": [1], "开门": [3, 4]}
        if p in mon_bach_rules.get(mon, []): cung_status[p].append(("门迫", "#000000"))

        # 3. BA TỔ HỢP CÁT HUNG
        if t_can in can_can_data and d_can in can_can_data[t_can]:
            kq_can_can = can_can_data[t_can][d_can]
            cung_3_elements[p].append(kq_can_can)
            
        if mon in mon_sao_data and sao in mon_sao_data[mon]:
            cung_3_elements[p].append(mon_sao_data[mon][sao])
            
        if than in than_cung_data and phi_tinh in than_cung_data[than]:
            cung_3_elements[p].append(than_cung_data[than][phi_tinh])

    return toan_ban_status, cung_status, cung_3_elements

# ==========================================
# 5. GIAO DIỆN HTML RENDER
# ==========================================
def format_stem(stem_str): return stem_str if stem_str else ""
def format_sao(sao_str): return sao_str if sao_str else ""

def render_html_table(cung_data, toan_ban_status, cung_status, cung_3_elements):
    luoi_lac_thu = [[4, 9, 2], [3, 5, 7], [8, 1, 6]]

    html = """
    <style>
        .qmdj-table { border-collapse: collapse; width: 100%; max-width: 510px; min-width: 400px; height: 420px; table-layout: fixed; font-family: sans-serif; margin: 0 auto; background: #fff;}
        .qmdj-td { border: 1px solid #aaa; width: 33.33%; position: relative; vertical-align: top; padding: 10px; }
        
        .cell-main {
            display: grid; grid-template-columns: auto auto 1fr; grid-template-rows: 22px 22px 22px;   
            column-gap: 15px; row-gap: 6px; height: 100%; min-height: 85px; align-content: start;
            margin-top: 5px; margin-left: 5px; 
        }

        .cell-center-left { display: flex; flex-direction: column; justify-content: flex-start; align-items: flex-start; margin-top: 33px; margin-left: 5px; gap: 6px; }
        
        .item-than  { grid-column: 1 / span 2; grid-row: 1; font-size: 15px; color: #222; text-align: left; }
        .item-tinh  { grid-column: 1; grid-row: 2; font-size: 15px; color: #222; text-align: left; }
        .item-mon   { grid-column: 1; grid-row: 3; font-size: 15px; color: #222; text-align: left; }
        .item-thien { grid-column: 2; grid-row: 2; font-size: 15px; color: #222; text-align: left; display: flex; align-items: center;}
        .item-dia   { grid-column: 2; grid-row: 3; font-size: 15px; color: #222; text-align: left; display: flex; align-items: center;}

        .bottom-left-phitinh { position: absolute; bottom: 3px; left: 5px; font-size: 15px; color: #555; font-weight: bold; }

        .right-panel { position: absolute; right: 5px; top: 22px; display: flex; flex-direction: column; align-items: flex-end; text-align: right; font-size: 11px; font-family: sans-serif; }
        .combo-item { color: #555; font-weight: 500; margin-bottom: 2px; }
        .spacer { height: 8px; }
        .formation-item { margin-bottom: 2px; font-weight: bold; letter-spacing: 1px; color: #000; }
    </style>
    <table class="qmdj-table">
    """

    for row in luoi_lac_thu:
        html += "<tr>"
        for p in row:
            d = cung_data[p]
            phi_tinh_html = f"<div class='bottom-left-phitinh'>{d['phi_tinh']}</div>"
            
            # Đã xóa phần gạch chân và đổi màu Thiên Bàn
            thien_full = f"<span>{format_stem(d['thien'])}</span>"
            dia_full = f"<span>{format_stem(d['dia'])}</span>"
            
            if p == 5:
                toan_ban_html = "".join([f"<div class='formation-item'>{c}</div>" for c in toan_ban_status])
                mock_combos = "".join(["<div class='combo-item' style='visibility:hidden;'>吉</div>" for _ in range(3)])
                right_panel_html = f"<div class='right-panel'>{mock_combos}<div class='spacer'></div>{toan_ban_html}</div>"
                html += f"""
                <td class="qmdj-td">
                    {phi_tinh_html}
                    {right_panel_html}
                    <div class="cell-center-left">
                        <div class="item-thien">{thien_full}</div>
                        <div class="item-dia">{dia_full}</div>
                    </div>
                </td>"""
                continue
                
            combos_html = "".join([f"<div class='combo-item'>{c}</div>" for c in cung_3_elements[p]])
            form_html = "".join([f"<div class='formation-item' style='color:{f_color};'>{f_name}</div>" for f_name, f_color in cung_status[p]])
            right_panel_html = f"<div class='right-panel'>{combos_html}<div class='spacer'></div>{form_html}</div>"
            
            html += f"""
            <td class="qmdj-td">
                {phi_tinh_html}
                {right_panel_html}
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
# 6. GIAO DIỆN STREAMLIT
# ==========================================
def get_current_vn_time(): return datetime.now(timezone(timedelta(hours=7)))

if "init_dt" not in st.session_state: st.session_state.init_dt = get_current_vn_time()

col1, col2 = st.columns(2)
with col1: selected_date = st.date_input("Ngày", value=st.session_state.init_dt.date(), min_value=datetime(1900, 1, 1).date(), max_value=datetime(2100, 12, 31).date())
with col2: selected_time = st.time_input("Giờ Phút", st.session_state.init_dt.time(), step=60)

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

bazi_dict = {'nam': thien_can[day_obj.getYearGZ().tg] + dia_chi[day_obj.getYearGZ().dz], 'thang': can_thang_hien_tai + chi_thang_hien_tai, 'ngay': can_ngay_hien_tai + nhat_chi_hien_tai}

# Lấy thông tin cục
don, cuc, jq_name, nguyen_index, is_nhuan = get_zhirun_ju(actual_date)
nhuan_str = " - 闰奇" if is_nhuan else ""

# Map Nguyên (Thượng, Trung, Hạ)
nguyen_map = {0: "上元", 1: "中元", 2: "下元"}
nguyen_str = nguyen_map.get(nguyen_index, "")

# Format Chuỗi tiêu đề mới
chuoi_cuc = f"{jq_name}{nhuan_str} - {nguyen_str} - {don}{cuc}局"
bazi_chuoi = f"{bazi_dict['nam']}年 {bazi_dict['thang']}月 {bazi_dict['ngay']}日 {hoa_giap_hien_tai}时"

data = lap_que(hoa_giap_hien_tai, nhat_chi_hien_tai, don, cuc, can_thang_hien_tai, can_ngay_hien_tai, chi_thang_hien_tai)

# --- KHỐI TÍNH TOÁN CÁCH CỤC ---
can_gio_phai, chi_gio_phai = hoa_giap_hien_tai[0], hoa_giap_hien_tai[1]
can_tuan = get_xun_leader(can_gio_phai, chi_gio_phai)

p_circle_list = [c for c, d in data.items() if d['dia'] == can_tuan]
p_circle = p_circle_list[0] if p_circle_list else 5
truc_su_door = ORIGINAL_GATES.get(p_circle, "死门")

toan_ban_st, cung_st, cung_3_el = qimen_analyzer(data, can_ngay_hien_tai, can_gio_phai, can_tuan, truc_su_door)
# -----------------------------------

title = f"<h3 style='margin-bottom:6px; font-family:sans-serif; color: #111; font-weight: 400; font-size: 18px; text-align: center;'>{bazi_chuoi}</h3>"
sub_title = f"<h4 style='margin-top:0px; margin-bottom:15px; font-family:sans-serif; color: #555; font-weight: 300; font-size: 15px; text-align: center;'>{chuoi_cuc}</h4>"

qimen_board_html = render_html_table(data, toan_ban_st, cung_st, cung_3_el)

combined_html = f"""
    <div style="display: flex; flex-direction: column; align-items: center; width: 100%; padding-top: 10px;">
        <div style="display: flex; flex-direction: column; align-items: center; width: 100%; max-width: 510px;">
            {title}
            {sub_title}
            {qimen_board_html}
        </div>
    </div>
"""

st.components.v1.html(combined_html, height=700, scrolling=True)
