import streamlit as st
import requests
import hashlib
import random
import time

# --- CẤU HÌNH HỆ THỐNG ---
URL_SERVER = "https://6a48cdd2a033dcb98d64f030.mockapi.io/bxh_game"
SECRET_SALT = "DaiCa_AntiCheat_2026"

CAU_HOI_MAC_DINH = [
    {"cau_hoi": "Cái gì đen khi bạn mua nó, đỏ khi dùng nó và xám xịt khi vứt nó đi?", "dap_an": ["Than đá", "Mực viết", "Quả bồ kết", "Chiếc lốp xe"], "dung": "Than đá"},
    {"cau_hoi": "Cái gì giữ cạnh bạn nhưng lại không bao giờ thuộc về bạn?", "dap_an": ["Tiền bạc", "Cái bóng", "Người yêu cũ", "Thời gian"], "dung": "Cái bóng"},
    {"cau_hoi": "Lịch nào dài nhất trong tất cả các loại lịch?", "dap_an": ["Lịch vạn niên", "Lịch sử", "Lịch treo tường", "Lịch mặt trăng"], "dung": "Lịch sử"},
    {"cau_hoi": "Con đường nào dài nhất thế giới?", "dap_an": ["Đường cao tốc", "Đường đời", "Đường xích đạo", "Đường đi đến thành công"], "dung": "Đường đời"}
]

# --- HÀM BỔ TRỢ LOGIC ---
def tao_ma_bao_mat(ten, diem, sotran):
    chuoi_goc = f"{ten}_{diem}_{sotran}_{SECRET_SALT}"
    return hashlib.md5(chuoi_goc.encode('utf-8')).hexdigest()

def doc_bxh_online():
    try:
        response = requests.get(URL_SERVER, timeout=6)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return []

def gui_du_lieu_server(ten, diem, so_tran, cheat_mode=False):
    try:
        bxh_hien_tai = doc_bxh_online()
        existing_user = None
        for item in bxh_hien_tai:
            if str(item.get("ten")).strip().lower() == ten.strip().lower():
                existing_user = item
                break
                
        if existing_user:
            id_user = existing_user["id"]
            diem_chot = int(diem) if cheat_mode else max(int(diem), int(existing_user.get("diem", 0)))
            sotran_chot = int(so_tran) if cheat_mode else (int(existing_user.get("sotran", 0)) + 1)
            
            payload = {
                "ten": str(ten),
                "diem": diem_chot,
                "sotran": sotran_chot,
                "checksum": tao_ma_bao_mat(ten, diem_chot, sotran_chot)
            }
            requests.put(f"{URL_SERVER}/{id_user}", json=payload, timeout=6)
        else:
            payload = {
                "ten": str(ten),
                "diem": int(diem),
                "sotran": int(so_tran),
                "checksum": tao_ma_bao_mat(ten, diem, so_tran)
            }
            requests.post(URL_SERVER, json=payload, timeout=6)
        return True
    except:
        return False

def lay_danh_hieu(diem):
    if diem < 20: return "👶 Tập sự"
    elif diem <= 40: return "🤓 Thông thái"
    else: return "👑 Thần đồng"

# --- KHỞI TẠO STATE CHO STREAMLIT ---
if 'game_state' not in st.session_state:
    st.session_state.game_state = 'MENU' # MENU, PLAYING, END_GAME, ADMIN
if 'ten_user' not in st.session_state:
    st.session_state.ten_user = ""
if 'cau_hoi_game' not in st.session_state:
    st.session_state.cau_hoi_game = []
if 'cau_hien_tai' not in st.session_state:
    st.session_state.cau_hien_tai = 0
if 'tong_diem' not in st.session_state:
    st.session_state.tong_diem = 0
if 'so_cau_sai' not in st.session_state:
    st.session_state.so_cau_sai = 0

# --- GIAO DIỆN CHÍNH ---
st.title("🛰️ LAPDPTZ QUIZ GAME ONLINE")
st.caption("Bản chạy trên nền tảng Web - Đồng bộ máy chủ Cloud")

# --- MÀN HÌNH MENU CHÍNH ---
if st.session_state.game_state == 'MENU':
    st.header("🎮 MENU CHÍNH")
    
    ten = st.text_input("👉 Nhập tên nhân vật của bạn:", value=st.session_state.ten_user).strip()
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🚀 VÀO TRẬN ĐẤU TRÍ", use_container_width=True):
            if not ten:
                st.error("Vui lòng nhập tên nhân vật trước khi chơi!")
            else:
                st.session_state.ten_user = ten
                # Tráo câu hỏi và đáp án
                st.session_state.cau_hoi_game = random.sample(CAU_HOI_MAC_DINH, len(CAU_HOI_MAC_DINH))
                for i in range(len(st.session_state.cau_hoi_game)):
                    random.shuffle(st.session_state.cau_hoi_game[i]['dap_an'])
                st.session_state.cau_hien_tai = 0
                st.session_state.tong_diem = 0
                st.session_state.so_cau_sai = 0
                st.session_state.game_state = 'PLAYING'
                st.rerun()
                
    with col2:
        # Nhập mã ẩn ngay tại ô chọn Menu
        admin_code = st.text_input("Nhập mã lệnh (Nếu có):", type="password")
        if admin_code == "lapdepzai":
            st.session_state.game_state = 'ADMIN'
            st.rerun()

    st.write("---")
    st.subheader("🏆 BẢNG XẾP HẠNG TOÀN MÁY CHỦ")
    
    with st.spinner("Đang đồng bộ dữ liệu với server..."):
        bxh = doc_bxh_online()
        if not bxh:
            st.info("Chưa có dữ liệu hoặc server bận.")
        else:
            danh_sach_hop_le = []
            for row in bxh:
                try:
                    t_name = str(row.get("ten", "Ẩn danh")).strip()
                    d_score = int(row.get("diem", 0))
                    s_match = int(row.get("sotran", 1))
                    c_sum = str(row.get("checksum", ""))
                    if c_sum == tao_ma_bao_mat(t_name, d_score, s_match):
                        danh_sach_hop_le.append({"Tên": t_name, "Danh Hiệu": lay_danh_hieu(d_score), "Điểm": d_score, "Số Trận": s_match})
                except: continue
            
            if danh_sach_hop_le:
                bxh_sap_xep = sorted(danh_sach_hop_le, key=lambda x: (-x['Điểm'], x['Số Trận']))[:10]
                st.table(bxh_sap_xep)
            else:
                st.warning("Dữ liệu BXH bị lỗi checksum bảo mật!")

# --- MÀN HÌNH CHƠI GAME ---
elif st.session_state.game_state == 'PLAYING':
    idx = st.session_state.cau_hien_tai
    total_q = len(st.session_state.cau_hoi_game)
    
    st.subheader(f"👤 Nhân vật: {st.session_state.ten_user} | 🏆 Điểm: {st.session_state.tong_diem} | ❌ Sai: {st.session_state.so_cau_sai}/5")
    st.progress(idx / total_q)
    
    if idx < total_q and st.session_state.so_cau_sai < 5:
        cau_hien_tai = st.session_state.cau_hoi_game[idx]
        st.info(f"**Câu hỏi {idx + 1}:** {cau_hien_tai['cau_hoi']}")
        
        # Tạo form để tránh việc người dùng click cái là bị nhảy câu hỏi ngay lập tức
        with st.form(key=f"quiz_form_{idx}"):
            lua_chon = st.radio("Chọn đáp án đúng:", cau_hien_tai['dap_an'])
            
            col_b1, col_b2 = st.columns(2)
            with col_b1:
                submit = st.form_submit_with_name("Trả lời")
            with col_b2:
                exit_game = st.form_submit_with_name("💾 Lưu điểm và Rút lui")

        if submit:
            if lua_chon == cau_hien_tai['dung']:
                st.success("🎉 ĐÚNG RỒI! +10 ĐIỂM!")
                st.session_state.tong_diem += 10
            else:
                st.error(f"❌ SAI RỒI! Đáp án đúng là: {cau_hien_tai['dung']}")
                st.session_state.so_cau_sai += 1
            
            time.sleep(1.2)
            st.session_state.cau_hien_tai += 1
            st.rerun()
            
        if exit_game:
            st.warning("Bạn đã chọn rút lui an toàn!")
            st.session_state.game_state = 'END_GAME'
            st.rerun()
    else:
        st.session_state.game_state = 'END_GAME'
        st.rerun()

# --- MÀN HÌNH KẾT THÚC GAME & ĐỒNG BỘ ĐIỂM ---
elif st.session_state.game_state == 'END_GAME':
    st.header("🏁 KẾT THÚC TRẬN ĐẤU")
    st.metric(label="Tổng điểm đạt được", value=f"{st.session_state.tong_diem} Điểm")
    st.write(f"Danh hiệu của bạn: **{lay_danh_hieu(st.session_state.tong_diem)}**")
    
    with st.spinner("📡 Đang đồng bộ hóa điểm số lên Server..."):
        thanh_cong = gui_du_lieu_server(st.session_state.ten_user, st.session_state.tong_diem, 1, cheat_mode=False)
        if thanh_cong:
            st.success("✅ Đã lưu kết quả thành công lên hệ thống Cloud!")
        else:
            st.error("❌ Đồng bộ thất bại! Lỗi kết nối mạng.")
            
    if st.button("Quay lại Menu chính"):
        st.session_state.game_state = 'MENU'
        st.rerun()

# --- MÀN HÌNH ADMIN BÍ MẬT ---
elif st.session_state.game_state == 'ADMIN':
    st.header("🕵️ MENU ADMIN BÍ MẬT")
    st.success("Xác nhận mật mã 'lapdepzai' chính xác!")
    
    with st.form("admin_form"):
        ten_sua = st.text_input("👉 Nhập TÊN tài khoản cần chỉnh sửa/tạo mới:")
        diem_sua = st.number_input("👉 Nhập ĐIỂM SỐ muốn thay đổi:", min_value=0, max_value=999999, value=999)
        sotran_sua = st.number_input("👉 Nhập SỐ TRẬN muốn thay đổi:", min_value=1, max_value=9999, value=50)
        
        btn_sub = st.form_submit_with_name("Thọc lệnh vào Server")
        
    if btn_sub:
        if ten_sua:
            if gui_du_lieu_server(ten_sua, diem_sua, sotran_sua, cheat_mode=True):
                st.success(f"✅ THÀNH CÔNG! Đã đổi {ten_sua} thành {diem_sua} Điểm / {sotran_sua} Trận!")
            else:
                st.error("❌ Thất bại! Vui lòng kiểm tra lại MockAPI.")
        else:
            st.warning("Vui lòng không để trống tên tài khoản!")
            
    if st.button("Thoát chế độ Admin"):
        st.session_state.game_state = 'MENU'
        st.rerun()
        