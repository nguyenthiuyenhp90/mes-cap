import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# ==========================================
# 1. CẤU HÌNH GIAO DIỆN & DATABASE GIẢ LẬP
# ==========================================
st.set_page_config(page_title="MES DÂY CÁP - BOM ĐA CẤP", layout="wide", initial_sidebar_state="expanded")

# Khởi tạo BOM Cây Đa Cấp (Level 0: TP | Level 1: BTP | Level 2: NVL)
if 'bom_tree' not in st.session_state:
    st.session_state.bom_tree = pd.DataFrame([
        # Level 0: Thành Phẩm
        {'Ma_Cha': 'ROOT', 'Ma_Con': 'CAT6.23AWG.BLUE', 'Ten_Mon': 'Cáp Mạng Cat6 Blue', 'Loai': 'TP', 'Level': 0, 'Cong_Doan': 'Thành phẩm', 'Dinh_Muc': 1.0, 'DVT': 'm', 'Ty_Le_Phe_Pct': 0.0},
        
        # Level 1: BTP Bọc vỏ (Công đoạn Bọc vỏ tiêu thụ BTP Xoắn tổng + Hạt nhựa PVC)
        {'Ma_Cha': 'CAT6.23AWG.BLUE', 'Ma_Con': 'BTP.CAT6.BOC_VO', 'Ten_Mon': 'BTP Sau Bọc Vỏ', 'Loai': 'BTP', 'Level': 1, 'Cong_Doan': 'Bọc vỏ', 'Dinh_Muc': 1.0, 'DVT': 'm', 'Ty_Le_Phe_Pct': 1.0},
        {'Ma_Cha': 'BTP.CAT6.BOC_VO', 'Ma_Con': 'NVL.PVC.BLUE', 'Ten_Mon': 'Hạt nhựa PVC Xanh', 'Loai': 'NVL', 'Level': 2, 'Cong_Doan': 'Bọc vỏ', 'Dinh_Muc': 0.025, 'DVT': 'kg/m', 'Ty_Le_Phe_Pct': 2.0},
        
        # Level 1: BTP Xoắn tổng (Công đoạn Xoắn tổng tiêu thụ BTP Xoắn đôi + Băng nhôm)
        {'Ma_Cha': 'BTP.CAT6.BOC_VO', 'Ma_Con': 'BTP.CAT6.XOAN_TONG', 'Ten_Mon': 'BTP Xoắn Tổng', 'Loai': 'BTP', 'Level': 1, 'Cong_Doan': 'Xoắn tổng', 'Dinh_Muc': 1.02, 'DVT': 'm', 'Ty_Le_Phe_Pct': 0.8},
        {'Ma_Cha': 'BTP.CAT6.XOAN_TONG', 'Ma_Con': 'NVL.BANG.NHOM', 'Ten_Mon': 'Băng Nhôm Chống Nhiễu', 'Loai': 'NVL', 'Level': 2, 'Cong_Doan': 'Xoắn tổng', 'Dinh_Muc': 0.005, 'DVT': 'kg/m', 'Ty_Le_Phe_Pct': 1.5},
        
        # Level 1: BTP Xoắn đôi (1m Xoắn tổng cần 4m BTP Xoắn đôi)
        {'Ma_Cha': 'BTP.CAT6.XOAN_TONG', 'Ma_Con': 'BTP.CAT6.XOAN_DOI', 'Ten_Mon': 'BTP Xoắn Đôi', 'Loai': 'BTP', 'Level': 1, 'Cong_Doan': 'Xoắn đôi', 'Dinh_Muc': 4.0, 'DVT': 'm', 'Ty_Le_Phe_Pct': 1.0},
        
        # Level 1 & 2: BTP Bọc lõi (1m Xoắn đôi cần 2m Lõi = 8m Lõi/1m Cáp. Lõi tiêu thụ Đồng + HDPE)
        {'Ma_Cha': 'BTP.CAT6.XOAN_DOI', 'Ma_Con': 'BTP.LOI.081', 'Ten_Mon': 'BTP Lõi Bọc HDPE', 'Loai': 'BTP', 'Level': 1, 'Cong_Doan': 'Bọc lõi', 'Dinh_Muc': 2.0, 'DVT': 'm', 'Ty_Le_Phe_Pct': 0.5},
        {'Ma_Cha': 'BTP.LOI.081', 'Ma_Con': 'NVL.DONG.057', 'Ten_Mon': 'Sợi Đồng 0.57mm', 'Loai': 'NVL', 'Level': 2, 'Cong_Doan': 'Bọc lõi', 'Dinh_Muc': 0.005, 'DVT': 'kg/m', 'Ty_Le_Phe_Pct': 1.0},
        {'Ma_Cha': 'BTP.LOI.081', 'Ma_Con': 'NVL.HDPE.COLOR', 'Ten_Mon': 'Hạt Nhựa HDPE Màu', 'Loai': 'NVL', 'Level': 2, 'Cong_Doan': 'Bọc lõi', 'Dinh_Muc': 0.003, 'DVT': 'kg/m', 'Ty_Le_Phe_Pct': 2.0}
    ])

if 'po_list' not in st.session_state:
    st.session_state.po_list = pd.DataFrame(columns=['Ma_PO', 'Ma_TP', 'DVT', 'So_Luong', 'Chieu_Dai_1_PCS', 'Tong_Met_TP', 'Trang_Thai'])
if 'kho_btp' not in st.session_state:
    st.session_state.kho_btp = pd.DataFrame(columns=['Ma_QR', 'Nguon_PO', 'Cong_Doan', 'Ma_SP', 'Trong_Luong_Tinh', 'So_Met'])
if 'phe_list' not in st.session_state:
    st.session_state.phe_list = pd.DataFrame(columns=['Nguon_PO', 'Cong_Doan', 'Ma_NVL_BTP', 'Trong_Luong_Phe_KG'])

# ==========================================
# 2. MENU ĐIỀU HƯỚNG BÊN TRÁI
# ==========================================
st.sidebar.title("🏭 MES SẢN XUẤT CÁP")
menu = st.sidebar.radio("CHỌN MODULE TÁC NGHIỆP", [
    "1. BOM Master (Đa Cấp Level 0-1-2)", 
    "2. Quản lý PO & Bóc Tách NVL (MRP)", 
    "3. Trạm Cân BTP & Thành Phẩm", 
    "4. Quản lý Phế Theo Công Đoạn", 
    "5. Dashboard Tiến Độ & Phế Liệu"
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
        # Tạo thụt lề hiển thị cấp bậc trực quan
        df_tree['Cấu Trúc Cây'] = df_tree.apply(lambda r: ("— " * r['Level']) + r['Ma_Con'] + f" ({r['Ten_Mon']})", axis=1)
        
        st.dataframe(
            df_tree[['Cấu Trúc Cây', 'Ma_Cha', 'Loai', 'Cong_Doan', 'Dinh_Muc', 'DVT', 'Ty_Le_Phe_Pct']], 
            use_container_width=True,
            height=450
        )

# ==========================================
# MODULE 2: QUẢN LÝ PO & BÓC TÁCH NVL (MRP)
# ==========================================
elif menu == "2. Quản lý PO & Bóc Tách NVL (MRP)":
    st.header("📝 QUẢN LÝ ĐƠN HÀNG & BÓC TÁCH NHU CẦU BTP / NVL")
    
    with st.form("form_po"):
        c1, c2, c3, c4 = st.columns(4)
        ma_po = c1.text_input("Mã PO", f"PO-{datetime.now().strftime('%Y%m%d')}-01")
        
        # Chọn các Mã Level 0 (TP)
        list_tp = st.session_state.bom_tree[st.session_state.bom_tree['Level'] == 0]['Ma_Con'].tolist()
        ma_tp = c2.selectbox("Mã Thành Phẩm", list_tp if list_tp else ["CAT6.23AWG.BLUE"])
        
        so_luong_box = c3.number_input("Số Lượng Box/Cuộn", min_value=1, value=1000)
        chieu_dai_box = c4.number_input("Chiều dài 1 Box (m)", min_value=1, value=305)
        
        if st.form_submit_button("Tạo PO & Bóc Tách Nhu Cầu"):
            tong_met_tp = so_luong_box * chieu_dai_box
            new_po = {'Ma_PO': ma_po, 'Ma_TP': ma_tp, 'DVT': 'PCS', 'So_Luong': so_luong_box, 'Chieu_Dai_1_PCS': chieu_dai_box, 'Tong_Met_TP': tong_met_tp, 'Trang_Thai': 'Đang chạy'}
            st.session_state.po_list = pd.concat([st.session_state.po_list, pd.DataFrame([new_po])], ignore_index=True)
            st.success(f"Đã tạo {ma_po} - Kế hoạch TP: {tong_met_tp:,.0f} m")

    st.subheader("Danh Sách PO Đang Chạy")
    st.dataframe(st.session_state.po_list, use_container_width=True)
    
    st.divider()
    
    # THUẬT TOÁN BÓC TÁCH BOM (BOM EXPLOSION)
    st.subheader("🔍 Tính Toán Nhu Cầu BTP & NVL Thô Theo PO (Bao gồm % Bù Phế)")
    if not st.session_state.po_list.empty:
        selected_po = st.selectbox("Chọn PO để xem chi tiết nhu cầu:", st.session_state.po_list['Ma_PO'].tolist())
        po_info = st.session_state.po_list[st.session_state.po_list['Ma_PO'] == selected_po].iloc[0]
        met_tp = po_info['Tong_Met_TP']
        
        # Tính toán cấp bậc
        mrp_data = []
        bom = st.session_state.bom_tree
        
        # Level 1: Bọc Vỏ
        boc_vo_bom = bom[bom['Ma_Con'] == 'BTP.CAT6.BOC_VO'].iloc[0]
        met_boc_vo = met_tp * boc_vo_bom['Dinh_Muc'] * (1 + boc_vo_bom['Ty_Le_Phe_Pct']/100)
        mrp_data.append({'Công Đoạn': 'Bọc vỏ', 'Mã Vật Tư/BTP': 'BTP.CAT6.BOC_VO', 'Loại': 'BTP (Level 1)', 'Nhu Cầu Kế Hoạch': f"{met_boc_vo:,.0f} m", 'Bao Gồm Phế': f"{boc_vo_bom['Ty_Le_Phe_Pct']}%"})
        
        pvc_bom = bom[bom['Ma_Con'] == 'NVL.PVC.BLUE'].iloc[0]
        kg_pvc = met_boc_vo * pvc_bom['Dinh_Muc'] * (1 + pvc_bom['Ty_Le_Phe_Pct']/100)
        mrp_data.append({'Công Đoạn': 'Bọc vỏ', 'Mã Vật Tư/BTP': 'NVL.PVC.BLUE', 'Loại': 'NVL (Level 2)', 'Nhu Cầu Kế Hoạch': f"{kg_pvc:,.2f} kg", 'Bao Gồm Phế': f"{pvc_bom['Ty_Le_Phe_Pct']}%"})

        # Level 1: Xoắn Tổng
        xoan_tong_bom = bom[bom['Ma_Con'] == 'BTP.CAT6.XOAN_TONG'].iloc[0]
        met_xoan_tong = met_boc_vo * xoan_tong_bom['Dinh_Muc'] * (1 + xoan_tong_bom['Ty_Le_Phe_Pct']/100)
        mrp_data.append({'Công Đoạn': 'Xoắn tổng', 'Mã Vật Tư/BTP': 'BTP.CAT6.XOAN_TONG', 'Loại': 'BTP (Level 1)', 'Nhu Cầu Kế Hoạch': f"{met_xoan_tong:,.0f} m", 'Bao Gồm Phế': f"{xoan_tong_bom['Ty_Le_Phe_Pct']}%"})

        # Level 1: Xoắn Đôi
        xoan_doi_bom = bom[bom['Ma_Con'] == 'BTP.CAT6.XOAN_DOI'].iloc[0]
        met_xoan_doi = met_xoan_tong * xoan_doi_bom['Dinh_Muc'] * (1 + xoan_doi_bom['Ty_Le_Phe_Pct']/100)
        mrp_data.append({'Công Đoạn': 'Xoắn đôi', 'Mã Vật Tư/BTP': 'BTP.CAT6.XOAN_DOI', 'Loại': 'BTP (Level 1)', 'Nhu Cầu Kế Hoạch': f"{met_xoan_doi:,.0f} m", 'Bao Gồm Phế': f"{xoan_doi_bom['Ty_Le_Phe_Pct']}%"})

        # Level 1: Bọc Lõi
        loi_bom = bom[bom['Ma_Con'] == 'BTP.LOI.081'].iloc[0]
        met_loi = met_xoan_doi * loi_bom['Dinh_Muc'] * (1 + loi_bom['Ty_Le_Phe_Pct']/100)
        mrp_data.append({'Công Đoạn': 'Bọc lõi', 'Mã Vật Tư/BTP': 'BTP.LOI.081', 'Loại': 'BTP (Level 1)', 'Nhu Cầu Kế Hoạch': f"{met_loi:,.0f} m", 'Bao Gồm Phế': f"{loi_bom['Ty_Le_Phe_Pct']}%"})

        dong_bom = bom[bom['Ma_Con'] == 'NVL.DONG.057'].iloc[0]
        kg_dong = met_loi * dong_bom['Dinh_Muc'] * (1 + dong_bom['Ty_Le_Phe_Pct']/100)
        mrp_data.append({'Công Đoạn': 'Bọc lõi', 'Mã Vật Tư/BTP': 'NVL.DONG.057', 'Loại': 'NVL (Level 2)', 'Nhu Cầu Kế Hoạch': f"{kg_dong:,.2f} kg", 'Bao Gồm Phế': f"{dong_bom['Ty_Le_Phe_Pct']}%"})

        st.dataframe(pd.DataFrame(mrp_data), use_container_width=True)

# ==========================================
# MODULE 3: TRẠM CÂN BTP & THÀNH PHẨM
# ==========================================
elif menu == "3. Trạm Cân BTP & Thành Phẩm":
    st.header("📦 TRẠM GHI NHẬN SẢN LƯỢNG BTP & THÀNH PHẨM")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.subheader("Thông tin Lệnh SX")
        list_po = ["-- Chọn --"] + st.session_state.po_list['Ma_PO'].tolist() if not st.session_state.po_list.empty else ["-- Chọn --"]
        nguon_po = st.selectbox("Chọn PO / Lệnh SX", list_po)
        
        cong_doan = st.selectbox("Công Đoạn Hoàn Thành", ["Bọc lõi", "Xoắn đôi", "Xoắn tổng", "Bọc vỏ"])
        
        # Lọc danh sách BTP tương ứng với công đoạn
        sub_bom = st.session_state.bom_tree[st.session_state.bom_tree['Cong_Doan'] == cong_doan]
        ma_sp = st.selectbox("Mã BTP / Thành Phẩm", sub_bom['Ma_Con'].tolist() if not sub_bom.empty else ["N/A"])
        
    with col2:
        st.subheader("Trạm Cân Hạch Toán Met")
        c1, c2 = st.columns(2)
        tl_tong = c1.number_input("Tổng Trọng Lượng Cân (KG)", min_value=0.0, value=50.0, format="%.2f")
        tl_bi = c2.number_input("Trọng Lượng Bì Rulo (KG)", min_value=0.0, value=5.0, format="%.2f")
        
        tl_tinh = max(0.0, tl_tong - tl_bi)
        
        # Lấy định mức để quy đổi ra Mét
        dm_row = st.session_state.bom_tree[st.session_state.bom_tree['Ma_Con'] == ma_sp]
        dm_val = dm_row['Dinh_Muc'].values[0] if not dm_row.empty else 0.01
        
        # Tạm tính quy đổi
        so_met_quydoi = (tl_tinh / dm_val) if (dm_row.empty or dm_row['DVT'].values[0] == 'kg/m') else tl_tinh
        
        st.metric("TỊNH (KG)", f"{tl_tinh:.2f} KG")
        st.metric("QUY ĐỔI SỐ MÉT BTP", f"{so_met_quydoi:,.0f} m")
        
        if st.button("💾 Nhập Kho BTP / In Tem QR"):
            if nguon_po == "-- Chọn --":
                st.error("Vui lòng chọn Mã PO!")
            else:
                ma_qr = f"{ma_sp}_LOT_{datetime.now().strftime('%m%d%H%M')}"
                new_item = {
                    'Ma_QR': ma_qr, 'Nguon_PO': nguon_po, 'Cong_Doan': cong_doan,
                    'Ma_SP': ma_sp, 'Trong_Luong_Tinh': tl_tinh, 'So_Met': so_met_quydoi
                }
                st.session_state.kho_btp = pd.concat([st.session_state.kho_btp, pd.DataFrame([new_item])], ignore_index=True)
                st.success(f"Đã lưu kho BTP! QR: {ma_qr}")

    st.divider()
    st.subheader("Nhật Ký Nhập Kho BTP (WIP Inventory)")
    st.dataframe(st.session_state.kho_btp, use_container_width=True)

# ==========================================
# MODULE 4: QUẢN LÝ PHẾ THEO CÔNG ĐOẠN
# ==========================================
elif menu == "4. Quản lý Phế Theo Công Đoạn":
    st.header("♻️ TRẠM GHI NHẬN PHẾ LIỆU THEO LEVEL 1 & 2")
    
    with st.form("form_phe_multi"):
        c1, c2, c3, c4 = st.columns(4)
        list_po = ["-- Chọn --"] + st.session_state.po_list['Ma_PO'].tolist() if not st.session_state.po_list.empty else ["-- Chọn --"]
        nguon_po = c1.selectbox("Nguồn PO", list_po)
        cong_doan = c2.selectbox("Công Đoạn Phát Sinh", ["Bọc lõi", "Xoắn đôi", "Xoắn tổng", "Bọc vỏ"])
        
        # Chọn loại phế (Đồng, Nhựa, BTP hỏng...)
        ma_nvl = c3.selectbox("Loại NVL / BTP Phế", st.session_state.bom_tree['Ma_Con'].tolist())
        tl_phe = c4.number_input("Trọng Lượng Phế (KG)", min_value=0.0, value=2.5, format="%.2f")
        
        if st.form_submit_button("Lưu Ghi Nhận Phế"):
            if nguon_po == "-- Chọn --":
                st.error("Vui lòng chọn PO!")
            else:
                new_phe = {'Nguon_PO': nguon_po, 'Cong_Doan': cong_doan, 'Ma_NVL_BTP': ma_nvl, 'Trong_Luong_Phe_KG': tl_phe}
                st.session_state.phe_list = pd.concat([st.session_state.phe_list, pd.DataFrame([new_phe])], ignore_index=True)
                st.success("Đã lưu phế liệu thành công!")

    st.subheader("Lịch Sử Phát Sinh Phế Liệu")
    st.dataframe(st.session_state.phe_list, use_container_width=True)

# ==========================================
# MODULE 5: DASHBOARD TIẾN ĐỘ & PHẾ LIỆU
# ==========================================
elif menu == "5. Dashboard Tiến Độ & Phế Liệu":
    st.markdown("<h2 style='text-align: center; color: #4DA8DA;'>MES SẢN XUẤT CÁP — DASHBOARD TIẾN ĐỘ BTP</h2>", unsafe_allow_html=True)
    
    list_po_filter = ["TẤT CẢ PO"] + st.session_state.po_list['Ma_PO'].tolist() if not st.session_state.po_list.empty else ["TẤT CẢ PO"]
    selected_po = st.selectbox("🔍 BỘ LỌC DỮ LIỆU PO:", list_po_filter)
    
    # Lọc dữ liệu
    df_btp = st.session_state.kho_btp if selected_po == "TẤT CẢ PO" else st.session_state.kho_btp[st.session_state.kho_btp['Nguon_PO'] == selected_po]
    df_phe = st.session_state.phe_list if selected_po == "TẤT CẢ PO" else st.session_state.phe_list[st.session_state.phe_list['Nguon_PO'] == selected_po]

    # Tổng hợp tiến độ sản lượng BTP theo từng Công Đoạn
    cong_doans = ["Bọc lõi", "Xoắn đôi", "Xoắn tổng", "Bọc vỏ"]
    san_luong_met = [df_btp[df_btp['Cong_Doan'] == cd]['So_Met'].sum() if not df_btp.empty else 0 for cd in cong_doans]
    phe_kg = [df_phe[df_phe['Cong_Doan'] == cd]['Trong_Luong_Phe_KG'].sum() if not df_phe.empty else 0 for cd in cong_doans]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("📦 TỔNG LÕI ĐÃ BỌC", f"{san_luong_met[0]:,.0f} m")
    col2.metric("🔄 TỔNG XOẮN ĐÔI", f"{san_luong_met[1]:,.0f} m")
    col3.metric("🔀 TỔNG XOẮN TỔNG", f"{san_luong_met[2]:,.0f} m")
    col4.metric("🛡️ TỔNG BỌC VỎ (TP)", f"{san_luong_met[3]:,.0f} m")

    st.divider()

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Sản Lượng BTP Theo Công Đoạn (m)")
        fig_bar = go.Figure(data=[go.Bar(x=cong_doans, y=san_luong_met, marker_color='#4DA8DA')])
        fig_bar.update_layout(template="plotly_dark", yaxis=dict(title="Số Mét"))
        st.plotly_chart(fig_bar, use_container_width=True)

    with c2:
        st.subheader("Lượng Phế Phát Sinh Theo Công Đoạn (KG)")
        fig_pie = go.Figure(data=[go.Pie(labels=cong_doans, values=phe_kg, hole=.4)])
        fig_pie.update_layout(template="plotly_dark")
        st.plotly_chart(fig_pie, use_container_width=True)
