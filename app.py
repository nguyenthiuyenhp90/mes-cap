import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import random

st.set_page_config(page_title="MES DÂY CÁP - FULL WORKFLOW", layout="wide", initial_sidebar_state="expanded")

# ==========================================
# 1. DATABASE GIẢ LẬP & DỮ LIỆU MẪU CÓ SẴN
# ==========================================
if 'bom_tree' not in st.session_state:
    st.session_state.bom_tree = pd.DataFrame([
        {'Ma_Cha': 'ROOT', 'Ma_Con': 'CAT6.23AWG.BLUE', 'Ten_Mon': 'Cáp Mạng Cat6 Blue', 'Loai': 'TP', 'Level': 0, 'Cong_Doan': 'Thành phẩm', 'Dinh_Muc': 1.0, 'DVT': 'm', 'Ty_Le_Phe_Pct': 0.0},
        
        {'Ma_Cha': 'CAT6.23AWG.BLUE', 'Ma_Con': 'BTP.CAT6.BOC_VO', 'Ten_Mon': 'BTP Sau Bọc Vỏ', 'Loai': 'BTP', 'Level': 1, 'Cong_Doan': 'Bọc vỏ', 'Dinh_Muc': 1.0, 'DVT': 'm', 'Ty_Le_Phe_Pct': 1.0},
        {'Ma_Cha': 'BTP.CAT6.BOC_VO', 'Ma_Con': 'NVL.PVC.BLUE', 'Ten_Mon': 'Hạt nhựa PVC Xanh', 'Loai': 'NVL', 'Level': 2, 'Cong_Doan': 'Bọc vỏ', 'Dinh_Muc': 0.025, 'DVT': 'kg/m', 'Ty_Le_Phe_Pct': 2.0},
        
        {'Ma_Cha': 'BTP.CAT6.BOC_VO', 'Ma_Con': 'BTP.CAT6.XOAN_TONG', 'Ten_Mon': 'BTP Xoắn Tổng', 'Loai': 'BTP', 'Level': 1, 'Cong_Doan': 'Xoắn tổng', 'Dinh_Muc': 1.02, 'DVT': 'm', 'Ty_Le_Phe_Pct': 0.8},
        
        {'Ma_Cha': 'BTP.CAT6.XOAN_TONG', 'Ma_Con': 'BTP.CAT6.XOAN_DOI', 'Ten_Mon': 'BTP Xoắn Đôi', 'Loai': 'BTP', 'Level': 1, 'Cong_Doan': 'Xoắn đôi', 'Dinh_Muc': 4.0, 'DVT': 'm', 'Ty_Le_Phe_Pct': 1.0},
        
        {'Ma_Cha': 'BTP.CAT6.XOAN_DOI', 'Ma_Con': 'BTP.LOI.081', 'Ten_Mon': 'BTP Lõi Bọc HDPE', 'Loai': 'BTP', 'Level': 1, 'Cong_Doan': 'Bọc lõi', 'Dinh_Muc': 2.0, 'DVT': 'm', 'Ty_Le_Phe_Pct': 0.5},
        {'Ma_Cha': 'BTP.LOI.081', 'Ma_Con': 'NVL.DONG.057', 'Ten_Mon': 'Sợi Đồng 0.57mm', 'Loai': 'NVL', 'Level': 2, 'Cong_Doan': 'Bọc lõi', 'Dinh_Muc': 0.005, 'DVT': 'kg/m', 'Ty_Le_Phe_Pct': 1.0},
        {'Ma_Cha': 'BTP.LOI.081', 'Ma_Con': 'NVL.HDPE.COLOR', 'Ten_Mon': 'Hạt Nhựa HDPE Màu', 'Loai': 'NVL', 'Level': 2, 'Cong_Doan': 'Bọc lõi', 'Dinh_Muc': 0.003, 'DVT': 'kg/m', 'Ty_Le_Phe_Pct': 2.0}
    ])

if 'po_list' not in st.session_state:
    st.session_state.po_list = pd.DataFrame([
        {'Ma_PO': 'PO-20260722-01', 'Ma_TP': 'CAT6.23AWG.BLUE', 'DVT': 'PCS', 'So_Luong': 100, 'Chieu_Dai_1_PCS': 305, 'Tong_Met_TP': 30500, 'Trang_Thai': 'Đang chạy'}
    ])

# DỮ LIỆU NVL KHO ĐÃ XUẤT CẤP CHO PO (ĐẦU VÀO)
if 'xuat_kho_nvl' not in st.session_state:
    st.session_state.xuat_kho_nvl = pd.DataFrame([
        {'Nguon_PO': 'PO-20260722-01', 'Ma_NVL': 'NVL.DONG.057', 'Ten_NVL': 'Sợi Đồng 0.57mm', 'So_Luong_Xuat_KG': 325.0},
        {'Nguon_PO': 'PO-20260722-01', 'Ma_NVL': 'NVL.HDPE.COLOR', 'Ten_NVL': 'Hạt Nhựa HDPE Màu', 'So_Luong_Xuat_KG': 195.0},
        {'Nguon_PO': 'PO-20260722-01', 'Ma_NVL': 'NVL.PVC.BLUE', 'Ten_NVL': 'Hạt nhựa PVC Xanh', 'So_Luong_Xuat_KG': 780.0}
    ])

# DỮ LIỆU BTP SẢN XUẤT ĐƯỢC (ĐẦU RA - BTP/TP)
if 'kho_btp' not in st.session_state:
    st.session_state.kho_btp = pd.DataFrame([
        {'Ma_QR': 'BTP.LOI_LOT_01', 'Nguon_PO': 'PO-20260722-01', 'Cong_Doan': 'Bọc lõi', 'Ma_SP': 'BTP.LOI.081', 'Trong_Luong_Tinh': 1220.0, 'So_Met': 244000.0},
        {'Ma_QR': 'BTP.XOAN_LOT_01', 'Nguon_PO': 'PO-20260722-01', 'Cong_Doan': 'Xoắn đôi', 'Ma_SP': 'BTP.CAT6.XOAN_DOI', 'Trong_Luong_Tinh': 1210.0, 'So_Met': 121000.0},
        {'Ma_QR': 'BTP.VO_LOT_01', 'Nguon_PO': 'PO-20260722-01', 'Cong_Doan': 'Bọc vỏ', 'Ma_SP': 'BTP.CAT6.BOC_VO', 'Trong_Luong_Tinh': 1200.0, 'So_Met': 30000.0}
    ])

# DỮ LIỆU PHẾ THU GOM (ĐẦU RA - PHẾ)
if 'phe_list' not in st.session_state:
    st.session_state.phe_list = pd.DataFrame([
        {'Nguon_PO': 'PO-20260722-01', 'Cong_Doan': 'Bọc lõi', 'Ma_NVL_BTP': 'NVL.DONG.057', 'Trong_Luong_Phe_KG': 3.5},
        {'Nguon_PO': 'PO-20260722-01', 'Cong_Doan': 'Bọc lõi', 'Ma_NVL_BTP': 'NVL.HDPE.COLOR', 'Trong_Luong_Phe_KG': 4.2},
        {'Nguon_PO': 'PO-20260722-01', 'Cong_Doan': 'Bọc vỏ', 'Ma_NVL_BTP': 'NVL.PVC.BLUE', 'Trong_Luong_Phe_KG': 15.0}
    ])

# ==========================================
# 2. MENU ĐIỀU HƯỚNG BÊN TRÁI
# ==========================================
st.sidebar.title("🏭 MES SẢN XUẤT CÁP")
menu = st.sidebar.radio("CHỌN MODULE TÁC NGHIỆP", [
    "1. BOM Master (Đa Cấp Level 0-1-2)", 
    "2. Quản lý PO & Xuất Kho NVL", 
    "3. Trạm Cân BTP & Thành Phẩm (COM Port / Manual)", 
    "4. Quản lý Phế Theo Công Đoạn", 
    "5. Quyết Toán Lệnh SX (Đối Soát Đồng/Nhựa)",
    "6. Dashboard Tiến Độ & Phế Liệu"
])

# ==========================================
# MODULE 2: QUẢN LÝ PO & XUẤT KHO NVL
# ==========================================
if menu == "2. Quản lý PO & Xuất Kho NVL":
    st.header("📝 ĐƠN HÀNG & GHI NHẬN XUẤT KHO NVL CHO PO")
    
    col_po, col_nvl = st.columns([1, 1])
    with col_po:
        st.subheader("1. Danh Sách Lệnh SX (PO)")
        st.dataframe(st.session_state.po_list, use_container_width=True)
        
    with col_nvl:
        st.subheader("2. Cấp Phát NVL (Đồng / Nhựa) Cho Lệnh")
        with st.form("form_xuat_nvl"):
            po_sel = st.selectbox("Chọn PO", st.session_state.po_list['Ma_PO'].tolist())
            nvl_row = st.session_state.bom_tree[st.session_state.bom_tree['Loai'] == 'NVL']
            ma_nvl = st.selectbox("Chọn Vật Tư (Đồng / Nhựa)", nvl_row['Ma_Con'].tolist())
            kg_xuat = st.number_input("Số Lượng Xuất Cấp (KG)", min_value=0.1, value=50.0)
            
            if st.form_submit_button("➕ Xuất Kho NVL"):
                ten_nvl = nvl_row[nvl_row['Ma_Con'] == ma_nvl]['Ten_Mon'].values[0]
                new_xk = {'Nguon_PO': po_sel, 'Ma_NVL': ma_nvl, 'Ten_NVL': ten_nvl, 'So_Luong_Xuat_KG': kg_xuat}
                st.session_state.xuat_kho_nvl = pd.concat([st.session_state.xuat_kho_nvl, pd.DataFrame([new_xk])], ignore_index=True)
                st.success(f"Đã xuất {kg_xuat} KG {ten_nvl} cho {po_sel}")

    st.subheader("📋 Lịch Sử Xuất Kho NVL Cho Các Lệnh SX")
    st.dataframe(st.session_state.xuat_kho_nvl, use_container_width=True)

# ==========================================
# MODULE 5: QUYẾT TOÁN LỆNH SX (CÂN BẰNG KHỐI LƯỢNG ĐỒNG/NHỰA)
# ==========================================
elif menu == "5. Quyết Toán Lệnh SX (Đối Soát Đồng/Nhựa)":
    st.header("⚖️ QUYẾT TOÁN LỆNH SẢN XUẤT & ĐỐI SOÁT ĐỒNG/NHỰA")
    st.caption("Cân bằng khối lượng NVL Đầu Vào (Kho Xuất) vs Đầu Ra (BTP/TP + Phế) để phát hiện thất thoát ĐỒNG/NHỰA")
    
    if not st.session_state.po_list.empty:
        po_selected = st.selectbox("Chọn Lệnh SX Cần Quyết Toán:", st.session_state.po_list['Ma_PO'].tolist())
        po_row = st.session_state.po_list[st.session_state.po_list['Ma_PO'] == po_selected].iloc[0]
        
        st.subheader(f"📊 Báo Cáo Cân Bằng Vật Tư PO: {po_selected}")
        
        # Lấy dữ liệu thuộc PO này
        df_xuat = st.session_state.xuat_kho_nvl[st.session_state.xuat_kho_nvl['Nguon_PO'] == po_selected]
        df_btp = st.session_state.kho_btp[st.session_state.kho_btp['Nguon_PO'] == po_selected]
        df_phe = st.session_state.phe_list[st.session_state.phe_list['Nguon_PO'] == po_selected]
        
        # BẢNG CÂN BẰNG KHỐI LƯỢNG (MASS BALANCE TABLE)
        list_nvl = st.session_state.bom_tree[st.session_state.bom_tree['Loai'] == 'NVL']
        
        mass_balance_rows = []
        for _, nvl in list_nvl.iterrows():
            m_nvl = nvl['Ma_Con']
            ten_nvl = nvl['Ten_Mon']
            dinh_muc = nvl['Dinh_Muc'] # kg/m
            cong_doan = nvl['Cong_Doan']
            
            # 1. Đầu vào: Tổng xuất từ kho
            kg_xuat = df_xuat[df_xuat['Ma_NVL'] == m_nvl]['So_Luong_Xuat_KG'].sum() if not df_xuat.empty else 0.0
            
            # 2. Đầu ra: Nằm trong BTP/TP thực tế sản xuất (Mét * Định mức)
            met_btp = df_btp[df_btp['Cong_Doan'] == cong_doan]['So_Met'].sum() if not df_btp.empty else 0.0
            kg_trong_sp = met_btp * dinh_muc
            
            # 3. Đầu ra: Phế thu gom
            kg_phe = df_phe[df_phe['Ma_NVL_BTP'] == m_nvl]['Trong_Luong_Phe_KG'].sum() if not df_phe.empty else 0.0
            
            # 4. Thất thoát bất thường (Variance / Unaccounted Loss)
            kg_mat_mat = kg_xuat - (kg_trong_sp + kg_phe)
            pct_mat_mat = (kg_mat_mat / kg_xuat * 100) if kg_xuat > 0 else 0.0
            
            # Đánh giá cảnh báo
            trang_thai = "🟢 Bình thường"
            if pct_mat_mat > 1.5:
                trang_thai = f"🔴 Thất thoát cao ({pct_mat_mat:.1f}%)"
            elif pct_mat_mat < 0 and kg_xuat > 0:
                trang_thai = "⚠️ Âm (Thiếu xuất NVL)"

            mass_balance_rows.append({
                'Mã NVL': m_nvl,
                'Tên Nguyên Vật Liệu': ten_nvl,
                'Công Đoạn': cong_doan,
                '1. Kho Xuất Cấp (KG)': round(kg_xuat, 2),
                '2. Nằm Trong BTP/TP (KG)': round(kg_trong_sp, 2),
                '3. Phế Thu Gom (KG)': round(kg_phe, 2),
                '4. Thất Thoát Bất Thường (KG)': round(kg_mat_mat, 2),
                'Tỷ Lệ Thất Thoát (%)': f"{pct_mat_mat:.2f}%",
                'Cảnh Báo Vận Hành': trang_thai
            })
            
        df_mb = pd.DataFrame(mass_balance_rows)
        
        # HIỂN THỊ BẢNG ĐỐI SOÁT CHI TIẾT THEO TỪNG DÒNG VẬT TƯ
        st.dataframe(df_mb, use_container_width=True)
        
        st.divider()
        
        # TỔNG HỢP RIÊNG CHO ĐỒNG (VẬT TƯ CỐT LÕI)
        dong_row = df_mb[df_mb['Mã NVL'].str.contains('DONG', case=False)]
        if not dong_row.empty:
            kg_dong_xuat = dong_row['1. Kho Xuất Cấp (KG)'].values[0]
            kg_dong_tp = dong_row['2. Nằm Trong BTP/TP (KG)'].values[0]
            kg_dong_phe = dong_row['3. Phế Thu Gom (KG)'].values[0]
            kg_dong_mat = dong_row['4. Thất Thoát Bất Thường (KG)'].values[0]
            
            st.subheader("🔴 ĐỐI SOÁT CHUYÊN SÂU: NGUYÊN LIỆU ĐỒNG (COPPER RECONCILIATION)")
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Tổng Đồng Cấp Vào", f"{kg_dong_xuat:.2f} KG")
            c2.metric("Đồng Tạo Thành BTP/TP", f"{kg_dong_tp:.2f} KG")
            c3.metric("Đồng Phế Thu Gom", f"{kg_dong_phe:.2f} KG")
            c4.metric("Đồng Mất Mát / Thất Thát", f"{kg_dong_mat:.2f} KG", delta=f"{kg_dong_mat:.2f} KG", delta_color="inverse")

        # NÚT KHÓA LỆNH
        st.divider()
        if po_row['Trang_Thai'] == 'Đang chạy':
            if st.button("🔒 CHỐT QUYẾT TOÁN & KHÓA LỆNH SX"):
                st.session_state.po_list.loc[st.session_state.po_list['Ma_PO'] == po_selected, 'Trang_Thai'] = 'Đã Quyết Toán'
                st.success(f"Đã khóa Lệnh {po_selected}. Dữ liệu đối soát Đồng/Nhựa đã lưu cố định!")
                st.rerun()
        else:
            st.success("✅ Lệnh SX này đã được Quyết toán và Khóa dữ liệu.")

# Các module 1, 3, 4, 6 giữ nguyên cấu trúc mượt mà trước đó...
