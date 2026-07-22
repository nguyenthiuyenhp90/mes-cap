import streamlit as st
import pandas as pd
from datetime import datetime

# ---------------------------------------------------------
# 1. CẤU HÌNH TRANG & MENU BÊN (SIDEBAR)
# ---------------------------------------------------------
st.set_page_config(
    page_title="Hệ Thống MES - Sản Xuất Cáp Điện",
    page_icon="🏭",
    layout="wide"
)

# Danh sách công đoạn chuẩn trong nhà máy cáp
DANH_SACH_CONG_DOAN = [
    "1. Đùn Lõi (Core Extrusion)",
    "2. Xoắn Đôi (Pairing)",
    "3. Xoắn Tổng (Cabling/Stranding)",
    "4. Dệt Lưới / Bọc Băng (Braiding/Shielding)",
    "5. Bọc Vỏ (Jacketing)",
    "6. Đóng Gói (Packaging)"
]

# Khởi tạo cơ sở dữ liệu dùng chung (Session State)
if "bom_db" not in st.session_state:
    st.session_state.bom_db = {
        "CAT6_UTP": {
            "ten_tp": "Cáp Mạng Cat6 UTP 4P",
            "quy_trinh": ["1. Đùn Lõi (Core Extrusion)", "2. Xoắn Đôi (Pairing)", "3. Xoắn Tổng (Cabling/Stranding)", "5. Bọc Vỏ (Jacketing)", "6. Đóng Gói (Packaging)"],
            "dm_dong": 15.2, "dm_nhua_loi": 8.5, "dm_nhua_vo": 22.0, "he_so_phe": 3.0
        }
    }

if "lsx_db" not in st.session_state:
    st.session_state.lsx_db = []

if "bao_cong_db" not in st.session_state:
    st.session_state.bao_cong_db = []

# Sidebar điều hướng ứng dụng
st.sidebar.title("🏭 MES CÁP ĐIỆN v2.0")
chuc_nang = st.sidebar.radio(
    "Chọn Phân Hệ Quản Lý:",
    [
        "1. Quản Lý BOM & Định Mức",
        "2. Lập Lệnh Sản Xuất (LSX)",
        "3. Báo Công & Báo Phế Công Đoạn",
        "4. Báo Cáo Quyết Toán & Vật Tư"
    ]
)

# ---------------------------------------------------------
# PHẦN 1: QUẢN LÝ BOM & ĐỊNH MỨC (TẠO MÃ LINH HOẠT)
# ---------------------------------------------------------
if chuc_nang == "1. Quản Lý BOM & Định Mức":
    st.header("📋 Khai Báo Mã Thành Phẩm & Quy Trình Công Đoạn")
    
    col1, col2 = st.columns([1, 1])
    with col1:
        ma_tp = st.text_input("Mã Thành Phẩm (VD: CAT6_SFTP, DAY_CV_1.5):").strip().upper()
        ten_tp = st.text_input("Tên Chi Tiết Sản Phẩm:")
        he_so_phe = st.number_input("Tỷ lệ phế định mức toàn quy trình (%):", value=2.5, step=0.1)
    
    with col2:
        st.subheader("Chọn Các Công Đoạn Cáp Phải Đi Qua:")
        qt_da_chon = []
        for cd in DANH_SACH_CONG_DOAN:
            if st.checkbox(cd, key=f"bom_{cd}"):
                qt_da_chon.append(cd)

    st.write("---")
    st.subheader("Định Mức Nguyên Vật Liệu (cho 1,000m / 1Km Cáp)")
    c1, c2, c3 = st.columns(3)
    with c1:
        dm_dong = st.number_input("Đồng (kg/km):", value=0.0)
    with c2:
        dm_nhua_loi = st.number_input("Nhựa Lõi PE/PVC (kg/km):", value=0.0)
    with c3:
        dm_nhua_vo = st.number_input("Nhựa Vỏ PVC/LSZH (kg/km):", value=0.0)

    if st.button("💾 Lưu BOM Mã Sản Phẩm", type="primary"):
        if ma_tp and ten_tp and qt_da_chon:
            st.session_state.bom_db[ma_tp] = {
                "ten_tp": ten_tp,
                "quy_trinh": qt_da_chon,
                "dm_dong": dm_dong,
                "dm_nhua_loi": dm_nhua_loi,
                "dm_nhua_vo": dm_nhua_vo,
                "he_so_phe": he_so_phe
            }
            st.success(f"✅ Đã lưu BOM thành công cho mã **{ma_tp}**!")
        else:
            st.error("❌ Vui lòng điền đủ Mã TP, Tên TP và chọn ít nhất 1 công đoạn!")

    # Hiển thị danh sách BOM hiện có
    st.write("---")
    st.subheader("📚 Danh Sách Mã BOM Đã Khai Báo")
    st.json(st.session_state.bom_db)

# ---------------------------------------------------------
# PHẦN 2: LẬP LỆNH SẢN XUẤT (PO / LSX)
# ---------------------------------------------------------
elif chuc_nang == "2. Lập Lệnh Sản Xuất (LSX)":
    st.header("📝 Lập Lệnh Sản Xuất Theo Đơn Hàng")
    
    danh_sach_ma = list(st.session_state.bom_db.keys())
    if not danh_sach_ma:
        st.warning("Chưa có mã BOM nào. Hãy qua phân hệ 1 để tạo mã trước!")
    else:
        col1, col2, col3 = st.columns(3)
        with col1:
            ma_lsx = st.text_input("Mã Lệnh Sản Xuất (VD: LSX-2026-001):").upper()
        with col2:
            ma_tp_chon = st.selectbox("Chọn Mã Thành Phẩm:", options=danh_sach_ma)
        with col3:
            met_ke_hoach = st.number_input("Số Mét Sản Xuất (m):", min_value=100, value=10000, step=500)

        if st.button("🚀 Phát Hành Lệnh Sản Xuất"):
            bom = st.session_state.bom_db[ma_tp_chon]
            # Tính nhu cầu NVL dự kiến
            he_so = (met_ke_hoach / 1000.0) * (1 + bom["he_so_phe"] / 100.0)
            
            lsx_new = {
                "ma_lsx": ma_lsx,
                "ma_tp": ma_tp_chon,
                "ten_tp": bom["ten_tp"],
                "met_ke_hoach": met_ke_hoach,
                "nhu_cau_dong": round(bom["dm_dong"] * he_so, 2),
                "nhu_cau_nhua_loi": round(bom["dm_nhua_loi"] * he_so, 2),
                "nhu_cau_nhua_vo": round(bom["dm_nhua_vo"] * he_so, 2),
                "trang_thai": "Đang chạy"
            }
            st.session_state.lsx_db.append(lsx_new)
            st.success(f"✅ Đã phát hành lệnh sản xuất **{ma_lsx}**!")

        st.write("---")
        st.subheader("📊 Danh Sách Lệnh Sản Xuất Đang Hoạt Động")
        if st.session_state.lsx_db:
            st.dataframe(pd.DataFrame(st.session_state.lsx_db), use_container_width=True)

# ---------------------------------------------------------
# PHẦN 3: BÁO CÔNG & BÁO PHẾ THEO TỪNG CÔNG ĐOẠN
# ---------------------------------------------------------
elif chuc_nang == "3. Báo Công & Báo Phế Công Đoạn":
    st.header("🏭 Báo Sản Lượng & Phế Theo Công Đoạn Thực Tế")
    
    if not st.session_state.lsx_db:
        st.warning("Chưa có Lệnh sản xuất nào được lập!")
    else:
        ds_lsx = [x["ma_lsx"] for x in st.session_state.lsx_db]
        
        c1, c2, c3 = st.columns(3)
        with c1:
            lsx_bc = st.selectbox("Chọn Lệnh Sản Xuất:", options=ds_lsx)
        
        # Tìm quy trình của LSX này
        lsx_info = next(item for item in st.session_state.lsx_db if item["ma_lsx"] == lsx_bc)
        bom_info = st.session_state.bom_db[lsx_info["ma_tp"]]
        
        with c2:
            cong_doan_bc = st.selectbox("Chọn Công Đoạn Báo Công:", options=bom_info["quy_trinh"])
        with c3:
            ma_may = st.text_input("Mã Máy / Dây Chuyền Running (VD: D_01, X_02):")

        st.write("---")
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            met_dat = st.number_input("Số mét ĐẠT công đoạn (m):", min_value=0, value=1000)
        with col_b:
            phe_dau_mauchot = st.number_input("Phế đầu/cuối/gạt nhựa (kg):", min_value=0.0, value=0.0)
        with col_c:
            phe_day_hong = st.number_input("Phế dây hỏng/đứt lõi (kg):", min_value=0.0, value=0.0)

        if st.button("📩 Ghi Nhận Báo Công", type="primary"):
            st.session_state.bao_cong_db.append({
                "ThoiGian": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "LSX": lsx_bc,
                "MaTP": lsx_info["ma_tp"],
                "CongDoan": cong_doan_bc,
                "May": ma_may,
                "MetDat": met_dat,
                "PheCuc_kg": phe_dau_mauchot,
                "PheDay_kg": phe_day_hong,
                "TongPhe_kg": phe_dau_mauchot + phe_day_hong
            })
            st.success(f"✅ Đã ghi nhận báo công cho công đoạn **{cong_doan_bc}**!")

        st.write("---")
        st.subheader("📋 Lịch Sử Báo Công Xưởng")
        if st.session_state.bao_cong_db:
            st.dataframe(pd.DataFrame(st.session_state.bao_cong_db), use_container_width=True)

# ---------------------------------------------------------
# PHẦN 4: BÁO CÁO QUYẾT TOÁN & TỔNG HỢP VẬT TƯ
# ---------------------------------------------------------
elif chuc_nang == "4. Báo Cáo Quyết Toán & Vật Tư":
    st.header("📈 Báo Cáo Quyết Toán Vật Tư & Tỷ Lệ Phế Thực Tế")
    
    if st.session_state.bao_cong_db:
        df_bc = pd.DataFrame(st.session_state.bao_cong_db)
        
        st.subheader("1. Tổng Mét Đạt Theo Công Đoạn")
        st.bar_chart(df_bc.groupby("CongDoan")["MetDat"].sum())
        
        st.subheader("2. Thống Kê Phế Phát Sinh Theo Công Đoạn (kg)")
        st.bar_chart(df_bc.groupby("CongDoan")["TongPhe_kg"].sum())
        
        st.subheader("3. Chi Tiết Bảng Sản Lượng & Phế Toàn Nhà Máy")
        st.dataframe(df_bc, use_container_width=True)
    else:
        st.info("Chưa có dữ liệu báo công nào từ xưởng.")
