import streamlit as st
import pandas as pd

# ---------------------------------------------------------
# 1. CẤU HÌNH TRANG CHÍNH
# ---------------------------------------------------------
st.set_page_config(
    page_title="Hệ Thống Quản Lý BOM Dây Cáp Điện",
    page_icon="🔌",
    layout="wide"
)

st.title("🔌 HỆ THỐNG QUẢN LÝ BOM & ĐỊNH MỨC SẢN XUẤT CÁP")
st.write("---")

# Các công đoạn chuẩn trong nhà máy sản xuất cáp
DANH_SACH_CONG_DOAN = [
    "1. Đùn Lõi (Core Extrusion)",
    "2. Xoắn Đôi (Pairing)",
    "3. Xoắn Tổng (Cabling/Stranding)",
    "4. Dệt Lưới / Bọc Băng (Braiding/Shielding)",
    "5. Bọc Vỏ (Jacketing)",
    "6. Đóng Gói (Packaging)"
]

# ---------------------------------------------------------
# 2. KHỞI TẠO CƠ SỞ DỮ LIỆU BOM (SESSION STATE)
# ---------------------------------------------------------
if "bom_database" not in st.session_state:
    st.session_state.bom_database = {
        "CAT6_UTP_4P": {
            "ten_tp": "Cáp Mạng Cat6 UTP 4 Pairs",
            "quy_trinh": [
                "1. Đùn Lõi (Core Extrusion)",
                "2. Xoắn Đôi (Pairing)",
                "3. Xoắn Tổng (Cabling/Stranding)",
                "5. Bọc Vỏ (Jacketing)",
                "6. Đóng Gói (Packaging)"
            ],
            "dinh_muc": {
                "Đồng (kg/km)": 15.2,
                "Nhựa Lõi PE (kg/km)": 8.5,
                "Nhựa Vỏ PVC (kg/km)": 22.0,
                "Lõi chữ thập (m/m)": 1.02,
            },
            "he_so_phe": 3.5 # % phế tổng công đoạn
        },
        "DAY_DON_1.5": {
            "ten_tp": "Dây Điện Đơn CV 1.5 mm2",
            "quy_trinh": [
                "1. Đùn Lõi (Core Extrusion)",
                "5. Bọc Vỏ (Jacketing)",
                "6. Đóng Gói (Packaging)"
            ],
            "dinh_muc": {
                "Đồng (kg/km)": 13.5,
                "Nhựa Vỏ PVC (kg/km)": 12.0,
            },
            "he_so_phe": 1.5
        }
    }

# ---------------------------------------------------------
# 3. GIAO DIỆN QUẢN LÝ (GỒM 2 TAB)
# ---------------------------------------------------------
tab1, tab2 = st.tabs(["📝 Tạo / Cấu Hình Mã TP Mới", "🧮 Tính Toán Định Mức Sản Xuất"])

# =========================================================
# TAB 1: TẠO VÀ CẤU HÌNH MÃ THÀNH PHẨM DỰA TRÊN QUY TRÌNH
# =========================================================
with tab1:
    st.header("Khai Báo Mã Thành Phẩm & Quy Trình Công Đoạn")
    
    col_left, col_right = st.columns([1, 1])
    
    with col_left:
        ma_tp = st.text_input("Mã Thành Phẩm (VD: CAT6_SFTP, DAY_DOI_2X2.5):").strip().upper()
        ten_tp = st.text_input("Tên Mô Tả Chi Tiết:")
        he_so_phe = st.number_input("Tỷ Lệ Hao Hụt / Phế Công Đoạn (%):", min_value=0.0, max_value=20.0, value=2.5, step=0.1)

    with col_right:
        st.subheader("Chọn Quy Trình Công Đoạn Bắt Buộc:")
        quy_trinh_chon = []
        for cd in DANH_SACH_CONG_DOAN:
            if st.checkbox(cd, value=(cd in ["1. Đùn Lõi (Core Extrusion)", "5. Bọc Vỏ (Jacketing)", "6. Đóng Gói (Packaging)"]), key=f"chk_{cd}"):
                quy_trinh_chon.append(cd)

    st.write("---")
    st.subheader("Khai Báo Định Mức Tiêu Hao Tương Ứng (Đơn vị cho 1,000m / 1Km TP)")
    
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    with col_m1:
        dong_kg = st.number_input("Trọng Lượng Đồng (kg/km):", min_value=0.0, value=0.0, step=0.1)
    with col_m2:
        nhua_loi_kg = st.number_input("Nhựa Lõi PE/PVC (kg/km):", min_value=0.0, value=0.0, step=0.1)
    with col_m3:
        nhua_vo_kg = st.number_input("Nhựa Bọc Vỏ PVC/LSZH (kg/km):", min_value=0.0, value=0.0, step=0.1)
    with col_m4:
        vattu_khac_kg = st.number_input("Vật Tư Phụ / Lưới / Băng (kg/km):", min_value=0.0, value=0.0, step=0.1)

    if st.button("💾 Lưu Mã Thành Phẩm Vào Hệ Thống", type="primary"):
        if not ma_tp or not ten_tp:
            st.error("❌ Vui lòng nhập đầy đủ Mã và Tên Thành Phẩm!")
        elif not quy_trinh_chon:
            st.error("❌ Phải chọn ít nhất 1 công đoạn sản xuất!")
        else:
            st.session_state.bom_database[ma_tp] = {
                "ten_tp": ten_tp,
                "quy_trinh": quy_trinh_chon,
                "dinh_muc": {
                    "Đồng (kg/km)": dong_kg,
                    "Nhựa Lõi (kg/km)": nhua_loi_kg,
                    "Nhựa Vỏ (kg/km)": nhua_vo_kg,
                    "Vật Tư Phụ (kg/km)": vattu_khac_kg
                },
                "he_so_phe": he_so_phe
            }
            st.success(f"✅ Đã lưu thành công Mã TP: **{ma_tp}** vào cơ sở dữ liệu BOM!")

# =========================================================
# TAB 2: TÍNH TOÁN VẬT TƯ SẢN XUẤT THEO ĐƠN HÀNG
# =========================================================
with tab2:
    st.header("Tính Toán Nguyên Vật Liệu & Công Đoạn Chạy")
    
    danh_sach_ma = list(st.session_state.bom_database.keys())
    
    col_sel1, col_sel2 = st.columns([2, 1])
    with col_sel1:
        ma_duoc_chon = st.selectbox("Chọn Mã Thành Phẩm Cần Sản Xuất:", options=danh_sach_ma)
    with col_sel2:
        so_luong_met = st.number_input("Số Lượng Mét Cần Sản Xuất (m):", min_value=100, value=10000, step=500)

    if ma_duoc_chon:
        bom_info = st.session_state.bom_database[ma_duoc_chon]
        
        st.info(f"📌 **Tên Sản Phẩm:** {bom_info['ten_tp']} | **Tỷ Lệ Phế:** {bom_info['he_so_phe']}%")
        
        # 1. Hiển thị Quy trình công đoạn chạy
        st.subheader("1. Lộ Trình Công Đoạn Sản Xuất Của Mã Này:")
        qt_df = pd.DataFrame({"Thứ tự": range(1, len(bom_info["quy_trinh"]) + 1), "Tên Công Đoạn": bom_info["quy_trinh"]})
        st.table(qt_df)

        # 2. Tính toán tổng nguyên vật liệu bao gồm phế
        st.subheader("2. Nhu Cầu Nguyên Vật Liệu (Đã Cộng Phế Hao Hụt):")
        
        he_so_chuyen_doi = (so_luong_met / 1000.0) * (1 + bom_info["he_so_phe"] / 100.0)
        
        ket_qua_nvl = []
        for ten_nvl, dm_val in bom_info["dinh_muc"].items():
            if dm_val > 0:
                tong_nhu_cau = dm_val * he_so_chuyen_doi
                ket_qua_nvl.append({
                    "Tên Nguyên Vật Liệu": ten_nvl,
                    "Định Mức Chuẩn (kg/km)": dm_val,
                    "Cần Xuất Kho (kg)": round(tong_nhu_cau, 2)
                })
        
        if ket_qua_nvl:
            st.dataframe(pd.DataFrame(ket_qua_nvl), use_container_width=True)
        else:
            st.warning("Mã này chưa được cài đặt định mức trọng lượng nguyên vật liệu!")
