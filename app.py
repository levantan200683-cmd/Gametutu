import streamlit as st
import requests
import hashlib
import random
import time

# --- CẤU HÌNH HỆ THỐNG ---
URL_SERVER = "https://6a48cdd2a033dcb98d64f030.mockapi.io/bxh_game"
SECRET_SALT = "DaiCa_AntiCheat_2026"

# Định nghĩa câu hỏi cố định để tránh bị đổi thứ tự đáp án mỗi lần render
if 'danh_sach_cau_hoi' not in st.session_state:
    CAU_HOI_GOC = [
        {"cau_hoi": "Cái gì đen khi bạn mua nó, đỏ khi dùng nó và xám xịt khi vứt nó đi?", "dap_an": ["Than đá", "Mực viết", "Quả bồ kết", "Chiếc lốp xe"], "dung": "Than đá"},
        {"cau_hoi": "Cái gì giữ cạnh bạn nhưng lại không bao giờ thuộc về bạn?", "dap_an": ["Tiền bạc", "Cái bóng", "Người yêu cũ", "Thời gian"], "dung": "Cái bóng"},
        {"cau_hoi": "Lịch nào dài nhất trong tất cả các loại lịch?", "dap_an": ["Lịch vạn niên", "Lịch sử", "Lịch treo tường", "Lịch mặt trăng"], "dung": "Lịch sử"},
        {"cau_hoi": "Con đường nào dài nhất thế giới?", "dap_an": ["Đường cao tốc", "Đường đời", "Đường xích đạo", "Đường đi đến thành công"], "dung": "Đường đời"}
    ]
    # Tráo câu hỏi và tráo đáp án ngay từ đầu, lưu vào bộ nhớ state
    for q in CAU_HOI_GOC:
        random.shuffle(q['dap_an'])
    st.session_state.danh_sach_cau_hoi = random.sample(CAU_HOI_GOC, len(CAU_HOI_GOC))

# --- HÀM BỔ TRỢ LOGIC ---
def tao_ma_bao_mat(ten, diem, sotran):
    chuoi_goc = f"{ten}_{diem}_{sotran}_{SECRET_SALT}"
    return hashlib.md5(chuoi_goc.encode('utf-8')).hexdigest()

def ma_hoa_mat_khau(mk):
    return hashlib.md5(mk.encode('utf-8')).hexdigest()

def doc_bxh_online():
    try:
        response = requests.get(URL_SERVER, timeout=6)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return []

def gui_du_lieu_server(ten, diem, so_tran_cong_them, mat_khau_moi="", cheat_mode=False):
    try:
        bxh_hien_tai = doc_bxh_online()
        existing_user = None
        for item in bxh_hien_tai:
            if str(item.get("ten")).strip().lower() == ten.strip().lower():
                existing_user = item
                break
                
        if existing_user:
            id_user = existing_user["id"]
            # Nếu là Admin chỉnh (cheat_mode) thì lấy thẳng số trận nhập vào, nếu là người chơi chơi xong thì cộng thêm số trận mới vào số cũ trên server
            diem_chot = int(diem) if cheat_mode else max(int(diem), int(existing_user.get("diem", 0)))
            sotran_chot = int(so_tran_cong_them) if cheat_mode else (int(existing_user.get("sotran", 0)) + int(so_tran_cong_them))
            
            payload = {
                "ten": str(ten),
                "diem": diem_chot,
                "sotran": sotran_chot,
                "checksum": tao_ma_bao_mat(ten, diem_chot, sotran_chot)
            }
            if mat_khau_moi:
                payload["matkhau"] = ma_hoa_mat_khau(mat_khau_moi)
                
            requests.put(f"{URL_SERVER}/{id_user}", json=payload, timeout=6)
        else:
            # Tài khoản mới tinh đăng ký chơi trận đầu tiên
            payload = {
                "ten": str(ten),
                "diem": int(diem),
                "sotran": int(so_tran_cong_them),
                "matkhau": ma_hoa_mat_khau(mat_khau_moi) if mat_khau_moi else ma_hoa_mat_khau("123"),
                "checksum": tao_ma_bao_mat(ten, diem, so_tran_cong_them)
            }
            requests.post(URL_SERVER, json=payload, timeout=6)
        return True
    except:
        return False

def lay_danh_hieu(diem):
    if diem < 20: return "👶 Tập sự"
    elif diem <= 40: return "🤓 Thông thái"
    else: return "👑 Thần đồng"

# --- KHỞI TẠO STATE ---
if 'game_state' not in st.session_state:
    st.session_state.game_state = 'MENU'
if 'ten_user' not in st.session_state:
    st.session_state.ten_user = ""
if 'cau_hien_tai' not in st.session_state:
    st.session_state.cau_hien_tai = 0
if 'tong_diem' not in st.session_state:
    st.session_state.tong_diem = 0
if 'so_cau_sai' not in st.session_state:
    st.session_state.so_cau_sai = 0

# --- CẤU HÌNH STYLE DIỆN ĐẸP + CHỮ TO ĐẬM MÀU ĐỎ ---
st.markdown("""
    <style>
    .stButton>button {
        border-radius: 12px !important;
        background-color: #1E88E5 !important;
        color: white !important;
        font-weight: bold !important;
        border: none !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .stButton>button:hover {
        background-color: #1565C0 !important;
    }
    .chu-admin-xin {
        font-size: 42px !important;
        font-weight: 900 !important;
        color: #FF1744 !important;
        text-align: center;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        letter-spacing: 2px;
        margin-top: 10px;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# --- GIAO DIỆN CHÍNH ---
st.title("🛰️ LAPDPTZ QUIZ GAME ONLINE")
st.caption("Bản Web-App nâng cấp Admin bảo mật + Đếm số trận chuẩn")

# --- MÀN HÌNH MENU CHÍNH ---
if st.session_state.game_state == 'MENU':
    st.markdown('<div class="chu-admin-xin">LAPDEPZAI</div>', unsafe_allow_html=True)
    st.header("🎮 MENU CHÍNH")
    
    ten = st.text_input("👉 Nhập tên nhân vật của bạn:", value=st.session_state.ten_user).strip()
    
    if ten:
        with st.spinner("🔍 Đang kiểm tra tài khoản trên máy chủ..."):
            bxh_hien_tai = doc_bxh_online()
            user_he_thong = None
            for item in bxh_hien_tai:
                if str(item.get("ten")).strip().lower() == ten.lower():
                    user_he_thong = item
                    break
        
        # Tên ĐÃ TỒN TẠI (Đăng nhập)
        if user_he_thong:
            st.warning(f"🔒 Tài khoản **{ten}** đã tồn tại trên hệ thống!")
            mat_khau_nhap = st.text_input("🔑 Nhập mật khẩu của bạn để vào game:", type="password")
            
            col_u1, col_u2 = st.columns(2)
            with col_u1:
                if st.button("🚀 ĐĂNG NHẬP & CHƠI", use_container_width=True):
                    mk_ma_hoa = ma_hoa_mat_khau(mat_khau_nhap)
                    mk_server = user_he_thong.get("matkhau", "")
                    if mk_ma_hoa == mk_server or not mk_server:
                        st.session_state.ten_user = ten
                        st.session_state.cau_hien_tai = 0
                        st.session_state.tong_diem = 0
                        st.session_state.so_cau_sai = 0
                        st.session_state.game_state = 'PLAYING'
                        st.rerun()
                    else:
                        st.error("❌ Mật khẩu không chính xác! Vui lòng thử lại.")
            with col_u2:
                if st.button("🔙 QUAY VỀ SẢNH", use_container_width=True):
                    st.session_state.ten_user = ""
                    st.rerun()
                    
        # Tên CHƯA TỒN TẠI (Đăng ký mới)
        else:
            st.info(f"✨ Tên **{ten}** hợp lệ! Bạn có thể đăng ký tài khoản này.")
            mat_khau_moi = st.text_input("🆕 Đặt mật khẩu cho tài khoản mới của bạn:", type="password")
            
            col_n1, col_n2 = st.columns(2)
            with col_n1:
                if st.button("🆕 ĐĂNG KÝ & CHƠI LUÔN", use_container_width=True):
                    if len(mat_khau_moi) < 1:
                        st.error("Vui lòng đặt mật khẩu để bảo vệ tài khoản!")
                    else:
                        with st.spinner("Đang khởi tạo tài khoản..."):
                            # Tạo mới thì tính luôn là trận thứ 1
                            if gui_du_lieu_server(ten, 0, 1, mat_khau_moi=mat_khau_moi, cheat_mode=False):
                                st.session_state.ten_user = ten
                                st.session_state.cau_hien_tai = 0
                                st.session_state.tong_diem = 0
                                st.session_state.so_cau_sai = 0
                                st.session_state.game_state = 'PLAYING'
                                st.rerun()
                            else:
                                st.error("Lỗi kết nối Server đăng ký!")
            with col_n2:
                if st.button("🔙 QUAY VỀ SẢNH", use_container_width=True):
                    st.session_state.ten_user = ""
                    st.rerun()

    # Nhập mã Admin ẩn
    st.write("---")
    admin_code = st.text_input("🕵️ Nhập mã lệnh Admin (Nếu có):", type="password")
    if admin_code == "lapdepzai":
        admin_pass = st.text_input("🔑 Nhập mật khẩu xác thực Admin:", type="password", key="he_thong_ad_pass")
        if admin_pass == "14l8l2008":
            if st.button("KÍCH HOẠT MENU ADMIN", use_container_width=True):
                st.session_state.game_state = 'ADMIN'
                st.rerun()
        elif admin_pass:
            st.error("❌ Mật khẩu xác thực Admin không chính xác!")

    st.write("---")
    st.subheader("🏆 BẢNG XẾP HẠNG TOÀN MÁY CHỦ")
    
    with st.spinner("Đang đồng bộ dữ liệu..."):
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
                st.warning("Không có dữ liệu hợp lệ!")

# --- MÀN HÌNH CHƠI GAME ---
elif st.session_state.game_state == 'PLAYING':
    idx = st.session_state.cau_hien_tai
    total_q = len(st.session_state.danh_sach_cau_hoi)
    
    st.subheader(f"👤: {st.session_state.ten_user} | 🏆: {st.session_state.tong_diem} | ❌: {st.session_state.so_cau_sai}/5")
    
    if idx < total_q and st.session_state.so_cau_sai < 5:
        cau_hien_tai = st.session_state.danh_sach_cau_hoi[idx]
        st.info(f"**Câu hỏi {idx + 1}:** {cau_hien_tai['cau_hoi']}")
        
        lua_chon = st.radio("Chọn đáp án của bạn:", cau_hien_tai['dap_an'], key=f"q_{idx}")
        
        col_b1, col_b2 = st.columns(2)
        with col_b1:
            if st.button("Trả lời câu này", use_container_width=True):
                if lua_chon == cau_hien_tai['dung']:
                    st.success("🎉 ĐÚNG RỒI! +10 ĐIỂM!")
                    st.session_state.tong_diem += 10
                else:
                    st.error(f"❌ SAI RỒI! Đáp án đúng là: {cau_hien_tai['dung']}")
                    st.session_state.so_cau_sai += 1
                
                time.sleep(1.2)
                st.session_state.cau_hien_tai += 1
                st.rerun()
        with col_b2:
            if st.button("💾 Lưu điểm & Rút lui", use_container_width=True):
                st.session_state.game_state = 'END_GAME'
                st.rerun()
    else:
        st.session_state.game_state = 'END_GAME'
        st.rerun()

# --- MÀN HÌNH KẾT THÚC GAME ---
elif st.session_state.game_state == 'END_GAME':
    st.header("🏁 KẾT THÚC TRẬN ĐẤU")
    st.metric(label="Tổng điểm đạt được", value=f"{st.session_state.tong_diem} Điểm")
    st.write(f"Danh hiệu: **{lay_danh_hieu(st.session_state.tong_diem)}**")
    
    with st.spinner("📡 Đang đồng bộ hóa điểm lên Server..."):
        # Chơi xong lượt này, hệ thống truyền số 1 vào để server tự động lấy số trận cũ + thêm 1 trận vừa chơi
        gui_du_lieu_server(st.session_state.ten_user, st.session_state.tong_diem, 1, cheat_mode=False)
        st.success("✅ Đã đồng bộ điểm số và cộng dồn 1 trận chơi thành công!")
            
    if st.button("Quay lại Menu chính"):
        st.session_state.game_state = 'MENU'
        st.rerun()

# --- MÀN HÌNH ADMIN BÍ MẬT ---
elif st.session_state.game_state == 'ADMIN':
    st.header("🕵️ MENU ADMIN BÍ MẬT")
    
    ten_sua = st.text_input("👉 Nhập TÊN tài khoản cần tác động:")
    diem_sua = st.number_input("👉 Cài đặt ĐIỂM SỐ mới:", min_value=0, value=999)
    sotran_sua = st.number_input("👉 Cài đặt TỔNG SỐ TRẬN mới (Ghi đè thẳng số trận):", min_value=1, value=50)
    mk_sua = st.text_input("🔑 Đổi luôn MẬT KHẨU mới cho acc này (Để trống nếu giữ nguyên):", type="password")
    
    if st.button("Nạp lệnh thay đổi dữ liệu Server"):
        if ten_sua:
            if gui_du_lieu_server(ten_sua, diem_sua, sotran_sua, mat_khau_moi=mk_sua, cheat_mode=True):
                st.success(f"✅ Đã cập nhật trạng thái tài khoản {ten_sua} trên Server thành công!")
            else:
                st.error("❌ Thất bại! Lỗi kết nối MockAPI.")
            
    if st.button("Thoát chế độ Admin"):
        st.session_state.game_state = 'MENU'
        st.rerun()
        