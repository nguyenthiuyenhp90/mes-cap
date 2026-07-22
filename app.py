import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import random

# ==========================================
# 1. CẤU HÌNH GIAO DIỆN & DATABASE GIẢ LẬP
# ==========================================
st.set_page_config(page_title="MES DÂY CÁP - FULL WORKFLOW", layout="wide", initial_sidebar_state="expanded")

# Khởi tạo BOM Cây Đa Cấp (Level 0: TP | Level 1: BTP | Level 2: NVL)
if 'bom_tree' not in st.session_state:
    st.session_state.bom_tree = pd.DataFrame([
        # Level 0: Thành Phẩm
        {'Ma_Cha': 'ROOT', 'Ma_Con': 'CAT6.23AWG.BLUE', 'Ten_Mon': 'Cáp Mạng Cat6 Blue', 'Loai': 'TP', 'Level': 0, 'Cong_Doan': 'Thành phẩm', 'Dinh_Muc': 1.0, 'DVT': 'm', 'Ty_Le_Phe_Pct': 0.0},
        
        # Level 1: BTP Bọc vỏ
        {'Ma_Cha': 'CAT6.23AWG.BLUE', 'Ma_Con': 'BTP.CAT6.BOC_VO', 'Ten_Mon': 'BTP Sau Bọc Vỏ', 'Loai': 'BTP', 'Level': 1, 'Cong_Doan': 'Bọc vỏ', 'Dinh_Muc': 1.0, 'DVT': 'm', 'Ty_Le_Phe_Pct': 1.0},
        {'Ma_Cha': 'BTP.CAT6.BOC_VO', 'Ma_Con': 'NVL.PVC.BLUE', 'Ten_Mon': 'Hạt nhựa PVC Xanh', 'Loai': 'NVL', 'Level': 2, 'Cong_Doan': 'Bọc vỏ', 'Dinh_Muc': 0.025, 'DVT': 'kg/m', 'Ty_Le_Phe_Pct': 2.0},
        
        # Level 1: BTP Xoắn tổng
        {'Ma_Cha': 'BTP.CAT6.BOC_VO', 'Ma_Con': 'BTP.CAT6.XOAN_TONG', 'Ten_Mon': 'BTP Xoắn Tổng', 'Loai': 'BTP', 'Level': 1, 'Cong_Doan': 'Xoắn tổng', 'Dinh_Muc': 1.02, 'DVT': 'm', 'Ty_Le_Phe_Pct': 0.8},
        {'Ma_Cha': 'BTP.CAT6.XOAN_TONG', 'Ma_Con': 'NVL.BANG.NHOM', 'Ten_Mon': 'Băng Nhôm Chống Nhiễu', 'Loai': 'NVL', 'Level': 2, 'Cong_Doan': 'Xoắn tổng', 'Dinh_Muc': 0.005, 'DVT': 'kg/m', 'Ty_Le_Phe_Pct': 1.5},
        
        # Level 1: BTP Xoắn đôi
        {'Ma_Cha': 'BTP.CAT6.XOAN_TONG', 'Ma_Con': 'BTP.CAT6.XOAN_DOI', 'Ten_Mon': 'BTP Xoắn Đôi', 'Loai': 'BTP', 'Level': 1, 'Cong_Doan': 'Xoắn đôi', 'Dinh_Muc': 4.0, 'DVT': 'm', 'Ty_Le_Phe_Pct': 1.0},
        
        # Level 1 & 2: BTP Bọc lõi
        {'Ma_Cha': 'BTP.CAT6.XOAN_DOI', 'Ma_Con': 'BTP.LOI.081', 'Ten_Mon': 'BTP Lõi Bọc HDPE', 'Loai': 'BTP', 'Level': 1, 'Cong_Doan': 'Bọc lõi', 'Dinh_Muc': 2.0, 'DVT': 'm', 'Ty_Le_Phe_Pct': 0.5},
        {'Ma_Cha': 'BTP.LOI.081', 'Ma_Con': 'NVL.DONG.057', 'Ten_Mon': 'Sợi Đồng 0.57mm', 'Loai': 'NVL', 'Level': 2, 'Cong_Doan': 'Bọc lõi', 'Dinh_Muc': 0.005, 'DVT': 'kg/m', 'Ty_Le_Phe_Pct': 1.0},
        {'Ma_Cha': 'BTP.LOI.081', 'Ma_Con': 'NVL.HDPE.COLOR', 'Ten_Mon': 'Hạt Nhựa HDPE Màu', 'Loai': 'NVL', 'Level': 2, 'Cong_Doan': 'Bọc lõi', 'Dinh_Muc': 0.003, 'DVT': 'kg/m', 'Ty_Le_Phe_Pct': 2.0}
    ])

if 'po_list' not in st.session_state:
    st.session_state.po_list = pd.DataFrame([
        {'Ma_PO': 'PO-20260722-01', 'Ma_TP': 'CAT6.23AWG.BLUE', 'DVT': 'PCS', 'So_Luong': 100, 'Chieu_Dai_1_PCS': 305, 'Tong_Met_TP': 30500, 'Trang_Thai': 'Đang chạy'}
    ])

if 'kho_btp' not in st.session_state:
    st.session_state.kho_btp = pd.DataFrame([
        {'Ma_QR': 'BTP.LOI.081_LOT_01', 'Nguon_PO': 'PO-20260722-01', 'Cong_Doan': 'Bọc lõi', 'Ma_SP': 'BTP.LOI.081', 'Trong_Luong_Tinh': 1250.0, 'So_Met': 250000.0},
        {'Ma_QR': 'BTP.CAT6.XOAN_DOI_LOT_01', 'Nguon_PO': 'PO-20260722-01', 'Cong_Doan': 'Xoắn đôi', 'Ma_SP': 'BTP.CAT6.XOAN_DOI', 'Trong_Luong_Tinh': 1235.0, 'So_Met': 123500.0},
        {'Ma_QR': 'BTP.CAT6.BOC_VO_LOT_01', 'Nguon_PO': 'PO-20260722-01', 'Cong_Doan': 'Bọc vỏ', 'Ma_SP': 'BTP.CAT6.BOC_VO', 'Trong_Luong_Tinh': 1220.0, 'So_Met': 30500.0}
    ])

if 'phe_list' not in st.session_state:
    st.session_state.phe_list = pd.DataFrame([
        {'Nguon_PO': 'PO-20260722-01', 'Cong_Doan': 'Bọc lõi', 'Ma_NVL_BTP': 'NVL.DONG.057', 'Trong_Luong_Phe_KG': 12.5},
        {'Nguon_PO': 'PO-20260722-01', 'Cong_Doan': 'Bọc vỏ', 'Ma_NVL_BTP': 'NVL.PVC.BLUE', 'Trong_Luong_Phe_KG': 18.0}
    ])

# ==========================================
# 2. MENU ĐIỀU HƯỚNG BÊN TRÁI
# ==========================================
st.sidebar.title("🏭 MES SẢN XUẤT CÁP")
menu = st.sidebar.radio("CHỌN MODULE TÁC NGHIỆP", [
    "1. BOM Master (Đa Cấp Level 0-1-2)", 
    "2. Quản lý PO & Bóc Tách NVL (MRP)", 
    "3. Trạm Cân BTP & Thành Phẩm (COM Port / Manual)", 
    "4. Quản lý Phế Theo Công Đoạn", 
    "5. Quyết Toán Lệnh SX (Reconciliation)",
    "6. Dashboard Tiến Độ & Phế Liệu"
])

# ==========================================
# MODULE 1: BOM MASTER ĐA CẤP
# ==========================================
if menu == "1. BOM Master (Đa Cấp Level 0-1-2)":
    st.header("⚙️ QUẢN LÝ ĐỊNH MỨC ĐA CẤP (MULTI-LEVEL BOM)")
    
    col_left, col_right = st.columns([1, 2])
    with col_left:
        st.subheader("Khai báo Cấu trúc Cha - Con")
        with st.form("form_add_bom"):
            ma_cha = st.selectbox("Mã Cha (Parent)", ["ROOT"] + list(st.session_state.bom_tree['Ma_Con'].unique()))
            ma_con = st.text_input("Mã Con (Child / BTP / NVL)", "NVL.PVC.BLACK")
            ten_mon = st.text_input("Tên Chi Tiết / Vật Tư", "Nhựa PVC Đen Vỏ Thượng")
            loai = st.selectbox("Phân Loại Level", ["BTP (Level 1)", "NVL (Level 2)", "TP (Level 0)"])
            cong_doan = st.selectbox("Công Đoạn", ["Bọc lõi", "Xoắn đôi", "Xoắn tổng", "Bọc vỏ", "Đóng gói"])
            dinh_muc = st.number_input("Định Mức / 1m Mã Cha", min_value=0.0001, value=1.0, format="%.4f")
            dvt = st.selectbox("Đơn Vị Tính", ["m", "kg/m", "kg", "cuộn"])
            phe_pct = st.number_input("% Phế Định Mức (Loss Factor)", min_value=0.0, value=1.0, format="%.1f")
            
            if st.form_submit_button("➕ Thêm vào Định Mức"):
                level_num = 0 if "Level 0" in loai else (1 if "Level 1" in loai else 2)
                loai_str = "TP" if level_num == 0 else ("BTP" if level_num == 1 else "NVL")
                
                new_row = {
                    'Ma_Cha': ma_cha, 'Ma_Con': ma_con, 'Ten_Mon': ten_mon,
                    'Loai': loai_str, 'Level': level_num, 'Cong_Doan': cong_doan,
                    'Dinh_Muc': dinh_muc, 'DVT': dvt, 'Ty_Le_Phe_Pct': phe_pct
                }
                st.session_state.bom_tree = pd.concat([st.session_state.bom_tree, pd.DataFrame([new_row])], ignore_index=True)
                st.success(f"Đã thêm {ma_con} thuộc {ma_cha}")

    with col_right:
        st.subheader("Cây Đa Cấp BOM Hiện Tại")
        df_tree = st.session_state.bom_tree.copy()
        df_tree['Cấu Trúc Cây'] = df_tree.apply(lambda r: ("— " * r['Level']) + r['Ma_Con'] + f" ({r['Ten_Mon']})", axis=1)
        st.dataframe(df_tree[['Cấu Trúc Cây', 'Ma_Cha', 'Loai', 'Cong_Doan', 'Dinh_Muc', 'DVT', 'Ty_Le_Phe_Pct']], use_container_width=True, height=450)

# ==========================================
# MODULE 2: QUẢN LÝ PO & BÓC TÁCH NVL (MRP)
# ==========================================
elif menu == "2. Quản lý PO & Bóc Tách NVL (MRP)":
    st.header("📝 QUẢN LÝ ĐƠN HÀNG & BÓC TÁCH NHU CẦU BTP / NVL")
    
    with st.form("form_po"):
        c1, c2, c3, c4 = st.columns(4)
        ma_po = c1.text_input("Mã PO", f"PO-{datetime.now().strftime('%Y%m%d')}-02")
        list_tp = st.session_state.bom_tree[st.session_state.bom_tree['Level'] == 0]['Ma_Con'].tolist()
        ma_tp = c2.selectbox("Mã Thành Phẩm", list_tp if list_tp else ["CAT6.23AWG.BLUE"])
        so_luong_box = c3.number_input("Số Lượng Box/Cuộn", min_value=1, value=500)
        chieu_dai_box = c4.number_input("Chiều dài 1 Box (m)", min_value=1, value=305)
        
        if st.form_submit_button("Tạo PO & Bóc Tách Nhu Cầu"):
            tong_met_tp = so_luong_box * chieu_dai_box
            new_po = {'Ma_PO': ma_po, 'Ma_TP': ma_tp, 'DVT': 'PCS', 'So_Luong': so_luong_box, 'Chieu_Dai_1_PCS': chieu_dai_box, 'Tong_Met_TP': tong_met_tp, 'Trang_Thai': 'Đang chạy'}
            st.session_state.po_list = pd.concat([st.session_state.po_list, pd.DataFrame([new_po])], ignore_index=True)
            st.success(f"Đã tạo {ma_po} - Kế hoạch TP: {tong_met_tp:,.0f} m")

    st.subheader("Danh Sách PO")
    st.dataframe(st.session_state.po_list, use_container_width=True)

# ==========================================
# MODULE 3: TRẠM CÂN BTP & THÀNH PHẨM (PHÂN BIỆT TỰ ĐỘNG / NHẬP TAY)
# ==========================================
elif menu == "3. Trạm Cân BTP & Thành Phẩm (COM Port / Manual)":
    st.header("📦 TRẠM GHI NHẬN SẢN LƯỢNG (HỖ TRỢ CÂN TỰ ĐỘNG & NHẬP TAY)")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.subheader("1. Thông tin Lệnh & Công Đoạn")
        list_po = ["-- Chọn --"] + st.session_state.po_list[st.session_state.po_list['Trang_Thai'] == 'Đang chạy']['Ma_PO'].tolist()
        nguon_po = st.selectbox("Chọn PO / Lệnh SX", list_po)
        
        cong_doan = st.selectbox("Công Đoạn Cân", ["Bọc lõi", "Xoắn đôi", "Xoắn tổng", "Bọc vỏ"])
        sub_bom = st.session_state.bom_tree[st.session_state.bom_tree['Cong_Doan'] == cong_doan]
        ma_sp = st.selectbox("Mã BTP / Thành Phẩm", sub_bom['Ma_Con'].tolist() if not sub_bom.empty else ["N/A"])
        
    with col2:
        st.subheader("2. Chế Độ Cân Điện Tử")
        che_do_can = st.radio("Lựa chọn phương thức đọc tín hiệu:", ["⚖️ Cân Tự Động (RS232/COM Port)", "⌨️ Nhập Tay Thủ Công"], horizontal=True)
        
        c1, c2 = st.columns(2)
        
        if che_do_can == "⚖️ Cân Tự Động (RS232/COM Port)":
            # Giá trị mô phỏng đọc trực tiếp từ đầu cân RS232
            if 'sim_weight' not in st.session_state:
                st.session_state.sim_weight = 152.45
                
            tl_tong = c1.number_input("Tổng Trọng Lượng (KG) - [Đọc Cổng COM]", value=st.session_state.sim_weight, disabled=True)
            if c1.button("🔄 Đọc Lại Tín Hiệu Cân"):
                st.session_state.sim_weight = round(random.uniform(100.0, 300.0), 2)
                st.rerun()
        else:
            tl_tong = c1.number_input("Tổng Trọng Lượng (KG) - [Nhập Tay]", min_value=0.0, value=150.0, format="%.2f")
            
        tl_bi = c2.number_input("Trọng Lượng Bì Rulo (KG)", min_value=0.0, value=10.5, format="%.2f")
        tl_tinh = max(0.0, tl_tong - tl_bi)
        
        # Đọc định mức để quy đổi ra mét
        dm_row = st.session_state.bom_tree[st.session_state.bom_tree['Ma_Con'] == ma_sp]
        dm_val = dm_row['Dinh_Muc'].values[0] if not dm_row.empty else 0.005
        so_met_quydoi = (tl_tinh / dm_val) if (not dm_row.empty and dm_row['DVT'].values[0] == 'kg/m') else tl_tinh
        
        st.info(f"👉 **Tịnh:** {tl_tinh:.2f} KG  |  👉 **Quy đổi:** {so_met_quydoi:,.0f} Mét")
        
        if st.button("💾 Lưu Kho BTP & In Tem QR 🖨️"):
            if nguon_po == "-- Chọn --":
                st.error("Vui lòng chọn Mã PO!")
            else:
                ma_qr = f"{ma_sp}_LOT_{datetime.now().strftime('%m%d%H%M')}"
                new_item = {
                    'Ma_QR': ma_qr, 'Nguon_PO': nguon_po, 'Cong_Doan': cong_doan,
                    'Ma_SP': ma_sp, 'Trong_Luong_Tinh': tl_tinh, 'So_Met': so_met_quydoi
                }
                st.session_state.kho_btp = pd.concat([st.session_state.kho_btp, pd.DataFrame([new_item])], ignore_index=True)
                st.success(f"Đã lưu kho BTP thành công! Mã QR: {ma_qr}")

    st.divider()
    st.subheader("Nhật Ký Nhập Kho BTP (WIP Inventory)")
    st.dataframe(st.session_state.kho_btp, use_container_width=True)

# ==========================================
# MODULE 4: QUẢN LÝ PHẾ THEO CÔNG ĐOẠN
# ==========================================
elif menu == "4. Quản lý Phế Theo Công Đoạn":
    st.header("♻️ TRẠM GHI NHẬN PHẾ LIỆU")
    
    with st.form("form_phe_multi"):
        c1, c2, c3, c4 = st.columns(4)
        list_po = ["-- Chọn --"] + st.session_state.po_list['Ma_PO'].tolist()
        nguon_po = c1.selectbox("Nguồn PO", list_po)
        cong_doan = c2.selectbox("Công Đoạn Phát Sinh", ["Bọc lõi", "Xoắn đôi", "Xoắn tổng", "Bọc vỏ"])
        ma_nvl = c3.selectbox("Loại NVL / BTP Phế", st.session_state.bom_tree['Ma_Con'].tolist())
        tl_phe = c4.number_input("Trọng Lượng Phế (KG)", min_value=0.0, value=2.5, format="%.2f")
        
        if st.form_submit_button("Lưu Ghi Nhận Phế"):
            if nguon_po == "-- Chọn --":
                st.error("Vui lòng chọn PO!")
            else:
                new_phe = {'Nguon_PO': nguon_po, 'Cong_Doan': cong_doan, 'Ma_NVL_BTP': ma_nvl, 'Trong_Luong_Phe_KG': tl_phe}
                st.session_state.phe_list = pd.concat([st.session_state.phe_list, pd.DataFrame([new_phe])], ignore_index=True)
                st.success("Đã ghi nhận phế thành công!")

    st.dataframe(st.session_state.phe_list, use_container_width=True)

# ==========================================
# MODULE 5: QUYẾT TOÁN LỆNH SX (RECONCILIATION & VARIANCE ANALYSIS)
# ==========================================
elif menu == "5. Quyết Toán Lệnh SX (Reconciliation)":
    st.header("⚖️ QUYẾT TOÁN LỆNH SẢN XUẤT (RECONCILIATION)")
    st.caption("Cân đối giữa Kế Hoạch Định Mức vs Thực Tế Thu Hồi BTP/Thành Phẩm vs Phế Thu Gom để kiểm soát thất thoát Bất Thường")
    
    if not st.session_state.po_list.empty:
        po_selected = st.selectbox("Chọn Lệnh SX Cần Quyết Toán:", st.session_state.po_list['Ma_PO'].tolist())
        po_row = st.session_state.po_list[st.session_state.po_list['Ma_PO'] == po_selected].iloc[0]
        
        st.subheader(f"📊 Báo Cáo Cân Đối Lệnh: {po_selected} (Trạng thái: {po_row['Trang_Thai']})")
        
        # 1. Thu thập dữ liệu
        met_tp_kh = po_row['Tong_Met_TP']
        df_btp_po = st.session_state.kho_btp[st.session_state.kho_btp['Nguon_PO'] == po_selected]
        df_phe_po = st.session_state.phe_list[st.session_state.phe_list['Nguon_PO'] == po_selected]
        
        met_tp_thucte = df_btp_po[df_btp_po['Cong_Doan'] == 'Bọc vỏ']['So_Met'].sum() if not df_btp_po.empty else 0
        tong_phe_kg = df_phe_po['Trong_Luong_Phe_KG'].sum() if not df_phe_po.empty else 0
        
        pct_hoan_thanh = (met_tp_thucte / met_tp_kh * 100) if met_tp_kh > 0 else 0
        
        # Hiển thị thẻ chỉ số chính
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Kế Hoạch Thành Phẩm", f"{met_tp_kh:,.0f} m")
        c2.metric("Thực Tế Nhập Kho (Bọc Vỏ)", f"{met_tp_thucte:,.0f} m", f"{pct_hoan_thanh:.1f}%")
        c3.metric("Tổng Phế Thu Gom", f"{tong_phe_kg:.2f} KG")
        
        # Đánh giá độ lệch (Variance)
        phe_dinh_muc_cho_phep_kg = (met_tp_kh * 0.040) * 0.015 # Giả định phế định mức cho phép ~1.5%
        do_lech_phe = tong_phe_kg - phe_dinh_muc_cho_phep_kg
        
        if do_lech_phe <= 0:
            c4.metric("Đánh Giá Hao Hụt", "ĐẠT CHUẨN", f"Dưới định mức {-do_lech_phe:.1f} KG", delta_color="normal")
        else:
            c4.metric("Đánh Giá Hao Hụt", "VƯỢT ĐỊNH MỨC", f"Vượt {do_lech_phe:.1f} KG", delta_color="inverse")
            
        st.divider()
        
        # Bảng đối soát chi tiết từng công đoạn
        st.subheader("📋 Bảng Bóc Tách Chi Tiết Theo Công Đoạn")
        recon_data = []
        for cd in ["Bọc lõi", "Xoắn đôi", "Xoắn tổng", "Bọc vỏ"]:
            met_cd = df_btp_po[df_btp_po['Cong_Doan'] == cd]['So_Met'].sum() if not df_btp_po.empty else 0
            phe_cd = df_phe_po[df_phe_po['Cong_Doan'] == cd]['Trong_Luong_Phe_KG'].sum() if not df_phe_po.empty else 0
            recon_data.append({
                'Công Đoạn': cd,
                'Sản Lượng BTP Cân Được': f"{met_cd:,.0f} m",
                'Phế Thực Tế Thu Gom': f"{phe_cd:.2f} KG",
                'Đánh Giá Vận Hành': 'Bình thường' if phe_cd < 15.0 else '⚠️ Phế Cao'
            })
        st.dataframe(pd.DataFrame(recon_data), use_container_width=True)
        
        # Nút Chốt Quyết Toán
        st.divider()
        col_btn1, col_btn2 = st.columns([1, 3])
        if po_row['Trang_Thai'] == 'Đang chạy':
            if col_btn1.button("🔒 CHỐT QUYẾT TOÁN & KHÓA LỆNH"):
                st.session_state.po_list.loc[st.session_state.po_list['Ma_PO'] == po_selected, 'Trang_Thai'] = 'Đã Quyết Toán'
                st.success(f"Lệnh {po_selected} đã được chốt quyết toán thành công!")
                st.rerun()
        else:
            st.success("✅ Lệnh SX này đã được Quyết toán và Khóa dữ liệu.")

# ==========================================
# MODULE 6: DASHBOARD TIẾN ĐỘ & PHẾ LIỆU
# ==========================================
elif menu == "6. Dashboard Tiến Độ & Phế Liệu":
    st.markdown("<h2 style='text-align: center; color: #4DA8DA;'>MES SẢN XUẤT CÁP — DASHBOARD TIẾN ĐỘ BTP</h2>", unsafe_allow_html=True)
    
    list_po_filter = ["TẤT CẢ PO"] + st.session_state.po_list['Ma_PO'].tolist()
    selected_po = st.selectbox("🔍 BỘ LỌC DỮ LIỆU PO:", list_po_filter)
    
    df_btp = st.session_state.kho_btp if selected_po == "TẤT CẢ PO" else st.session_state.kho_btp[st.session_state.kho_btp['Nguon_PO'] == selected_po]
    df_phe = st.session_state.phe_list if selected_po == "TẤT CẢ PO" else st.session_state.phe_list[st.session_state.phe_list['Nguon_PO'] == selected_po]

    cong_doans = ["Bọc lõi", "Xoắn đôi", "Xoắn tổng", "Bọc vỏ"]
    san_luong_met = [df_btp[df_btp['Cong_Doan'] == cd]['So_Met'].sum() if not df_btp.empty else 0 for cd in cong_doans]
    phe_kg = [df_phe[df_phe['Cong_Doan'] == cd]['Trong_Luong_Phe_KG'].sum() if not df_phe.empty else 0 for cd in cong_doans]

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Sản Lượng BTP Theo Công Đoạn (m)")
        fig_bar = go.Figure(data=[go.Bar(x=cong_doans, y=san_luong_met, marker_color='#4DA8DA')])
        fig_bar.update_layout(template="plotly_dark")
        st.plotly_chart(fig_bar, use_container_width=True)

    with c2:
        st.subheader("Lượng Phế Phát Sinh Theo Công Đoạn (KG)")
        fig_pie = go.Figure(data=[go.Pie(labels=cong_doans, values=phe_kg, hole=.4)])
        fig_pie.update_layout(template="plotly_dark")
        st.plotly_chart(fig_pie, use_container_width=True)
