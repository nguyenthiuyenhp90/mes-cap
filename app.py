import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# ==========================================
# 1. CẤU HÌNH GIAO DIỆN & DATABASE GIẢ LẬP
# ==========================================
st.set_page_config(page_title="MES DÂY CÁP", layout="wide", initial_sidebar_state="expanded")

# Khởi tạo Database (Session State) nếu chưa có
if 'bom_master' not in st.session_state:
    st.session_state.bom_master = pd.DataFrame([
        {'Ma_SP': 'CAT6.23AWG.BLUE', 'Loai': 'TP', 'OD_Loi': 0.55, 'Dinh_Muc_Dong': 0.015, 'Dinh_Muc_Nhua': 0.025, 'Tong_TL_kg_m': 0.040},
        {'Ma_SP': 'LOI.GR.081', 'Loai': 'Lõi', 'OD_Loi': 0.81, 'Dinh_Muc_Dong': 0.005, 'Dinh_Muc_Nhua': 0.003, 'Tong_TL_kg_m': 0.008},
        {'Ma_SP': 'LOI.BR.078', 'Loai': 'Lõi', 'OD_Loi': 0.78, 'Dinh_Muc_Dong': 0.004, 'Dinh_Muc_Nhua': 0.002, 'Tong_TL_kg_m': 0.006}
    ])
if 'po_list' not in st.session_state:
    st.session_state.po_list = pd.DataFrame(columns=['Ma_PO', 'Ma_TP', 'DVT', 'So_Luong', 'Chieu_Dai_1_PCS', 'Tong_Met', 'Trang_Thai'])
if 'kho_btp' not in st.session_state:
    st.session_state.kho_btp = pd.DataFrame(columns=['Ma_QR', 'Nguon_PO', 'Ma_SP', 'Trong_Luong_Tong', 'Trong_Luong_Bi', 'Trong_Luong_Tinh', 'So_Met'])
if 'phe_list' not in st.session_state:
    st.session_state.phe_list = pd.DataFrame(columns=['Nguon_PO', 'Cong_Doan', 'Trong_Luong_Phe'])

# ==========================================
# 2. MENU ĐIỀU HƯỚNG BÊN TRÁI
# ==========================================
st.sidebar.title("🏭 MES SẢN XUẤT CÁP")
menu = st.sidebar.radio("CHỌN MODULE TÁC NGHIỆP", [
    "1. BOM Master (Định mức)", 
    "2. Quản lý PO", 
    "3. Trạm Cân & In Tem (Sản Lượng)", 
    "4. Quản lý Phế", 
    "5. Dashboard (DAS)"
])

# ==========================================
# MODULE 1: BOM MASTER
# ==========================================
if menu == "1. BOM Master (Định mức)":
    st.header("⚙️ QUẢN LÝ ĐỊNH MỨC (BOM MASTER)")
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Bọc vỏ", "Xoắn tổng", "Xoắn đôi", "Lõi chi tiết", "Tổng hợp NVL"])
    
    with tab4:
        st.subheader("Khai báo Lõi chi tiết")
        with st.form("form_bom"):
            col1, col2, col3 = st.columns(3)
            ma_sp = col1.text_input("Mã SP/Lõi", "LOI.BL.081")
            od_loi = col2.number_input("OD Lõi (mm)", value=0.81, format="%.2f") 
            dm_dong = col3.number_input("Định mức Đồng (kg/m)", value=0.005, format="%.3f")
            
            submit = st.form_submit_button("Lưu Định Mức")
            if submit:
                new_bom = {'Ma_SP': ma_sp, 'Loai': 'Lõi', 'OD_Loi': od_loi, 'Dinh_Muc_Dong': dm_dong, 'Dinh_Muc_Nhua': 0.000, 'Tong_TL_kg_m': dm_dong}
                st.session_state.bom_master = pd.concat([st.session_state.bom_master, pd.DataFrame([new_bom])], ignore_index=True)
                st.success(f"Đã lưu BOM cho {ma_sp} với OD {od_loi}mm")
    
    st.dataframe(st.session_state.bom_master, use_container_width=True)

# ==========================================
# MODULE 2: QUẢN LÝ PO
# ==========================================
elif menu == "2. Quản lý PO":
    st.header("📝 NHẬP ĐƠN HÀNG (PO)")
    
    with st.form("form_po"):
        col1, col2 = st.columns(2)
        ma_po = col1.text_input("Mã PO", f"PO-{datetime.now().strftime('%Y%m%d')}-01")
        ma_tp = col2.selectbox("Mã Thành Phẩm", st.session_state.bom_master['Ma_SP'].tolist())
        
        col3, col4, col5 = st.columns(3)
        dvt = col3.selectbox("Đơn Vị Tính", ["MÉT", "PCS (Cuộn/Box)"])
        so_luong = col4.number_input("Số Lượng", min_value=1, value=900)
        chieu_dai = col5.number_input("Chiều dài 1 PCS (m)", min_value=1, value=305) if dvt == "PCS (Cuộn/Box)" else 1
        
        submit_po = st.form_submit_button("Tạo PO")
        if submit_po:
            tong_met = so_luong * chieu_dai
            new_po = {'Ma_PO': ma_po, 'Ma_TP': ma_tp, 'DVT': dvt, 'So_Luong': so_luong, 'Chieu_Dai_1_PCS': chieu_dai, 'Tong_Met': tong_met, 'Trang_Thai': 'Đang chạy'}
            st.session_state.po_list = pd.concat([st.session_state.po_list, pd.DataFrame([new_po])], ignore_index=True)
            st.success(f"Tạo thành công {ma_po} - Tổng mét kế hoạch: {tong_met:,.0f} m")
            
    st.dataframe(st.session_state.po_list, use_container_width=True)

# ==========================================
# MODULE 3: TRẠM CÂN & IN TEM
# ==========================================
elif menu == "3. Trạm Cân & In Tem (Sản Lượng)":
    st.header("📦 GHI NHẬN SẢN LƯỢNG & IN TEM QR")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.subheader("Thông tin Lệnh")
        danh_sach_po = ["-- Chọn --"] + st.session_state.po_list['Ma_PO'].tolist() if not st.session_state.po_list.empty else ["-- Chọn --"]
        nguon_po = st.selectbox("Chọn PO / Lệnh SX", danh_sach_po)
        ma_sp = st.selectbox("Mã Vật Tư Đang Chạy", st.session_state.bom_master['Ma_SP'].tolist())
        
        dm_tong = st.session_state.bom_master[st.session_state.bom_master['Ma_SP'] == ma_sp]['Tong_TL_kg_m'].values
        dm_tong_val = dm_tong[0] if len(dm_tong) > 0 else 0.010
        st.info(f"Định mức BOM: {dm_tong_val:.3f} kg/m")

    with col2:
        st.subheader("Trạm Cân Điện Tử")
        che_do_can = st.radio("Chế độ nhập liệu:", ["⚖️ Cân Tự Động (COM Port)", "⌨️ Nhập Tay"], horizontal=True)
        
        c1, c2, c3 = st.columns(3)
        if che_do_can == "⚖️ Cân Tự Động (COM Port)":
            tl_tong = c1.number_input("Tổng (KG) - [Đọc từ Cân]", value=152.00, disabled=True)
        else:
            tl_tong = c1.number_input("Tổng (KG) - [Nhập Tay]", value=0.00, min_value=0.00, format="%.3f")
            
        tl_bi = c2.number_input("Bì Rulo (KG)", value=10.552, format="%.3f")
        
        tl_tinh = max(0.0, tl_tong - tl_bi)
        so_met = tl_tinh / dm_tong_val if dm_tong_val > 0 else 0
        
        c3.metric("TỊNH (KG)", f"{tl_tinh:.3f}")
        st.metric("QUY ĐỔI SỐ MÉT", f"{so_met:,.0f} Mét")
        
        if st.button("Lưu Kho & In Tem QR 🖨️"):
            if nguon_po == "-- Chọn --":
                st.error("Lỗi: Vui lòng chọn Nguồn PO/Lệnh SX!")
            else:
                ma_qr = f"{ma_sp}_LOT_{datetime.now().strftime('%m%d%H%M')}"
                new_item = {
                    'Ma_QR': ma_qr, 
                    'Nguon_PO': nguon_po, 
                    'Ma_SP': ma_sp, 
                    'Trong_Luong_Tong': tl_tong, 
                    'Trong_Luong_Bi': tl_bi, 
                    'Trong_Luong_Tinh': tl_tinh, 
                    'So_Met': so_met
                }
                st.session_state.kho_btp = pd.concat([st.session_state.kho_btp, pd.DataFrame([new_item])], ignore_index=True)
                st.success(f"Đã hạch toán vào kho! Mã QR: {ma_qr}")
                
    st.divider()
    st.write("Lịch sử nhập kho (Dữ liệu đẩy sang BRAVO)")
    st.dataframe(st.session_state.kho_btp, use_container_width=True)

# ==========================================
# MODULE 4: QUẢN LÝ PHẾ
# ==========================================
elif menu == "4. Quản lý Phế":
    st.header("♻️ TRẠM GHI NHẬN PHẾ LIỆU")
    
    with st.form("form_phe"):
        c1, c2, c3 = st.columns(3)
        danh_sach_po = ["-- Chọn --"] + st.session_state.po_list['Ma_PO'].tolist() if not st.session_state.po_list.empty else ["-- Chọn --"]
        nguon_po = c1.selectbox("Nguồn PO / Lệnh SX", danh_sach_po)
        cong_doan = c2.selectbox("Công Đoạn Phát Sinh", ["Lõi", "Xoắn Đôi", "Vách", "Xoắn Tổng", "Bọc Vỏ"])
        tl_phe = c3.number_input("Trọng Lượng Phế (KG)", min_value=0.0, value=1.5, format="%.2f")
        
        btn_phe = st.form_submit_button("Lưu Ghi Nhận Phế")
        if btn_phe:
            if nguon_po == "-- Chọn --":
                st.error("Vui lòng chọn PO phát sinh phế!")
            else:
                new_phe = {'Nguon_PO': nguon_po, 'Cong_Doan': cong_doan, 'Trong_Luong_Phe': tl_phe}
                st.session_state.phe_list = pd.concat([st.session_state.phe_list, pd.DataFrame([new_phe])], ignore_index=True)
                st.success("Đã ghi nhận phế liệu thành công!")

    st.subheader("Bảng Lịch Sử Phế Liệu")
    st.dataframe(st.session_state.phe_list, use_container_width=True)

# ==========================================
# MODULE 5: DASHBOARD TỔNG & CHI TIẾT
# ==========================================
elif menu == "5. Dashboard (DAS)":
    st.markdown("<h2 style='text-align: center; color: #4DA8DA;'>MES SẢN XUẤT — DASHBOARD TỔNG QUAN</h2>", unsafe_allow_html=True)
    
    # BỘ LỌC
    danh_sach_loc = ["TẤT CẢ PO"] + st.session_state.po_list['Ma_PO'].tolist() if not st.session_state.po_list.empty else ["TẤT CẢ PO"]
    loc_po = st.selectbox("🔍 BỘ LỌC DỮ LIỆU:", danh_sach_loc)
    
    # LỌC DỮ LIỆU ĐỘNG
    if loc_po == "TẤT CẢ PO":
        df_po_filtered = st.session_state.po_list
        df_btp_filtered = st.session_state.kho_btp
        df_phe_filtered = st.session_state.phe_list
    else:
        df_po_filtered = st.session_state.po_list[st.session_state.po_list['Ma_PO'] == loc_po]
        df_btp_filtered = st.session_state.kho_btp[st.session_state.kho_btp['Nguon_PO'] == loc_po]
        df_phe_filtered = st.session_state.phe_list[st.session_state.phe_list['Nguon_PO'] == loc_po]

    # TÍNH TOÁN CÁC CHỈ SỐ REAL-TIME
    tong_met_kh = df_po_filtered['Tong_Met'].sum() if not df_po_filtered.empty else 0
    tong_met_sx = df_btp_filtered['So_Met'].sum() if not df_btp_filtered.empty else 0
    tong_phe_kg = df_phe_filtered['Trong_Luong_Phe'].sum() if not df_phe_filtered.empty else 0
    
    tiendo = (tong_met_sx / tong_met_kh * 100) if tong_met_kh > 0 else 0.0

    # METRICS TOP BAR
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("📦 TỔNG KH THÀNH PHẨM", f"{tong_met_kh:,.0f} m")
    col2.metric("📊 ĐÃ SẢN XUẤT", f"{tong_met_sx:,.0f} m")
    col3.metric("♻️ TỔNG PHẾ LIỆU", f"{tong_phe_kg:,.2f} KG", delta_color="inverse")
    col4.metric("📈 TIẾN ĐỘ SX", f"{tiendo:.1f}%")
    
    st.divider()

    # BIỂU ĐỒ SỬ DỤNG PLOTLY
    c1, c2 = st.columns(2)
    
    cong_doan_labels = ['Lõi', 'Xoắn Đôi', 'Vách', 'Xoắn Tổng', 'Bọc Vỏ']
    
    # Tính cơ cấu phế động
    if not df_phe_filtered.empty:
        phe_by_cd = df_phe_filtered.groupby('Cong_Doan')['Trong_Luong_Phe'].sum().reindex(cong_doan_labels, fill_value=0)
        phe_values = phe_by_cd.tolist()
    else:
        phe_values = [0, 0, 0, 0, 0]

    with c1:
        st.subheader("Cơ cấu Phế theo Công đoạn (KG)")
        fig_pie = go.Figure(data=[go.Pie(labels=cong_doan_labels, values=phe_values, hole=.4)])
        fig_pie.update_layout(template="plotly_dark", margin=dict(t=20, b=20, l=20, r=20))
        st.plotly_chart(fig_pie, use_container_width=True)
        
    with c2:
        st.subheader("Sản lượng Thực tế Kho (Mét)")
        fig_bar = go.Figure(data=[go.Bar(x=['Thực tế SX'], y=[tong_met_sx], marker_color='#4DA8DA')])
        fig_bar.update_layout(template="plotly_dark", yaxis=dict(title="Mét"))
        st.plotly_chart(fig_bar, use_container_width=True)
