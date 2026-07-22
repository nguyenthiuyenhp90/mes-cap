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
# MODULE 1: BOM MASTER (Giữ nguyên 5 Tab, Không fix cứng OD)
# ==========================================
if menu == "1. BOM Master (Định mức)":
    st.header("⚙️ QUẢN LÝ ĐỊNH MỨC (BOM MASTER)")
    
    # Giữ nguyên cấu trúc 5 tab
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Bọc vỏ", "Xoắn tổng", "Xoắn đôi", "Lõi chi tiết", "Tổng hợp NVL"])
    
    with tab4:
        st.subheader("Khai báo Lõi chi tiết")
        with st.form("form_bom"):
            col1, col2, col3 = st.columns(3)
            ma_sp = col1.text_input("Mã SP/Lõi", "LOI.BL.081")
            # OD không còn fix cứng, cho phép nhập linh hoạt dạng số thập phân
            od_loi = col2.number_input("OD Lõi (mm)", value=0.81, format="%.2f") 
            dm_dong = col3.number_input("Định mức Đồng (kg/m)", value=0.005, format="%.3f")
            
            submit = st.form_submit_button("Lưu Định Mức")
            if submit:
                # Cập nhật logic lưu vào DataFrame Session State
                new_bom = {'Ma_SP': ma_sp, 'Loai': 'Lõi', 'OD_Loi': od_loi, 'Dinh_Muc_Dong': dm_dong, 'Dinh_Muc_Nhua': 0.000, 'Tong_TL_kg_m': dm_dong}
                st.session_state.bom_master = pd.concat([st.session_state.bom_master, pd.DataFrame([new_bom])], ignore_index=True)
                st.success(f"Đã lưu BOM cho {ma_sp} với OD {od_loi}mm")
    
    st.dataframe(st.session_state.bom_master, use_container_width=True)

# ==========================================
# MODULE 2: QUẢN LÝ PO (Hỗ trợ Mét & PCS)
# ==========================================
elif menu == "2. Quản lý PO":
    st.header("📝 NHẬP ĐƠN HÀNG (PO)")
    
    with st.form("form_po"):
        col1, col2 = st.columns(2)
        ma_po = col1.text_input("Mã PO", "PO-2026-04-01")
        ma_tp = col2.selectbox("Mã Thành Phẩm", st.session_state.bom_master['Ma_SP'].tolist())
        
        col3, col4, col5 = st.columns(3)
        # Bổ sung lựa chọn ĐVT
        dvt = col3.selectbox("Đơn Vị Tính", ["MÉT", "PCS (Cuộn/Box)"])
        so_luong = col4.number_input("Số Lượng", min_value=1, value=900)
        
        # Nếu là PCS thì mới cần nhập chiều dài 1 cuộn (ví dụ 305m), nếu là Mét thì tự hiểu là 1
        chieu_dai = col5.number_input("Chiều dài 1 PCS (m)", min_value=1, value=305) if dvt == "PCS (Cuộn/Box)" else 1
        
        submit_po = st.form_submit_button("Tạo PO")
        if submit_po:
            tong_met = so_luong * chieu_dai
            new_po = {'Ma_PO': ma_po, 'Ma_TP': ma_tp, 'DVT': dvt, 'So_Luong': so_luong, 'Chieu_Dai_1_PCS': chieu_dai, 'Tong_Met': tong_met, 'Trang_Thai': 'Đang chạy'}
            st.session_state.po_list = pd.concat([st.session_state.po_list, pd.DataFrame([new_po])], ignore_index=True)
            st.success(f"Tạo thành công {ma_po} - Tổng mét kế hoạch: {tong_met:,.0f} m")
            
    st.dataframe(st.session_state.po_list, use_container_width=True)

# ==========================================
# MODULE 3: TRẠM CÂN & IN TEM (Thêm Nguồn PO, Radio Cân)
# ==========================================
elif menu == "3. Trạm Cân & In Tem (Sản Lượng)":
    st.header("📦 GHI NHẬN SẢN LƯỢNG & IN TEM QR")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.subheader("Thông tin Lệnh")
        # Bắt buộc chọn nguồn PO/Lệnh SX để truy xuất nguồn gốc
        danh_sach_po = ["-- Chọn --"] + st.session_state.po_list['Ma_PO'].tolist() if not st.session_state.po_list.empty else ["-- Chọn --"]
        nguon_po = st.selectbox("Chọn PO / Lệnh SX", danh_sach_po)
        ma_sp = st.selectbox("Mã Vật Tư Đang Chạy", st.session_state.bom_master['Ma_SP'].tolist())
        
        # Lấy định mức tổng để tính toán
        dm_tong = st.session_state.bom_master[st.session_state.bom_master['Ma_SP'] == ma_sp]['Tong_TL_kg_m'].values
        dm_tong_val = dm_tong[0] if len(dm_tong) > 0 else 0.010
        st.info(f"Định mức BOM: {dm_tong_val:.3f} kg/m")

    with col2:
        st.subheader("Trạm Cân Điện Tử")
        # Khôi phục tính năng chọn chế độ cân
        che_do_can = st.radio("Chế độ nhập liệu:", ["⚖️ Cân Tự Động (COM Port)", "⌨️ Nhập Tay"], horizontal=True)
        
        c1, c2, c3 = st.columns(3)
        if che_do_can == "⚖️ Cân Tự Động (COM Port)":
            tl_tong = c1.number_input("Tổng (KG) - [Đọc từ Cân]", value=152.00, disabled=True)
        else:
            tl_tong = c1.number_input("Tổng (KG) - [Nhập Tay]", value=0.00, min_value=0.00, format="%.3f")
            
        tl_bi = c2.number_input("Bì Rulo (KG)", value=10.552, format="%.3f")
        
        # Tính toán Tịnh và Số Mét với độ chính xác cao
        tl_tinh = tl_tong - tl_bi
        so_met = tl_tinh / dm_tong_val if dm_tong_val > 0 else 0
        
        c3.metric("TỊNH (KG)", f"{tl_tinh:.3f}")
        st.metric("QUY ĐỔI SỐ MÉT", f"{so_met:,.0f} Mét")
        
        if st.button("Lưu Kho & In Tem QR 🖨️"):
            if nguon_po == "-- Chọn --":
                st.error("Lỗi: Vui lòng chọn Nguồn PO/Lệnh SX!")
            else:
                ma_qr = f"{ma_sp}_LOT_{datetime.now().strftime('%m%d%H%M')}"
                new_item = {'Ma_QR': ma_qr, 'Nguon_PO': nguon_po, 'Ma_SP': ma_sp, 'Trong_Luong_Tong': tl_tong, 'Trong_Luong_Bi': tl_bi, 'Trong_Luong_Tinh': tl_tinh, 'So_Met': so_met}
                st.session_state.kho_btp = pd.concat([st.session_state.kho_btp, pd.DataFrame([new_item])], ignore_index=True)
                st.success(f"Đã hạch toán vào kho! Mã QR: {ma_qr}")
                
    st.divider()
    st.write("Lịch sử nhập kho (Dữ liệu đẩy sang BRAVO)")
    st.dataframe(st.session_state.kho_btp)

# ==========================================
# MODULE 4: QUẢN LÝ PHẾ (Giữ nguyên form cơ bản chờ phát triển)
# ==========================================
elif menu == "4. Quản lý Phế":
    st.header("♻️ TRẠM GHI NHẬN PHẾ LIỆU")
    st.info("Chức năng đang được quy hoạch theo chuẩn Quyết toán Lệnh.")

# ==========================================
# MODULE 5: DASHBOARD TỔNG & CHI TIẾT
# ==========================================
elif menu == "5. Dashboard (DAS)":
    st.markdown("<h2 style='text-align: center; color: #4DA8DA;'>MES SẢN XUẤT — DASHBOARD TỔNG QUAN</h2>", unsafe_allow_html=True)
    
    # TẦNG 1: BỘ LỌC KÍNH LÚP
    danh_sach_loc = ["TẤT CẢ PO"] + st.session_state.po_list['Ma_PO'].tolist() if not st.session_state.po_list.empty else ["TẤT CẢ PO"]
    loc_po = st.selectbox("🔍 BỘ LỌC DỮ LIỆU:", danh_sach_loc)
    
    # Lọc dữ liệu giả lập dựa trên bộ lọc
    if loc_po == "TẤT CẢ PO":
        tong_met_kh = st.session_state.po_list['Tong_Met'].sum() if not st.session_state.po_list.empty else 395280
        tong_met_sx = st.session_state.kho_btp['So_Met'].sum() if not st.session_state.kho_btp.empty else 157327
    else:
        # Nếu chọn riêng PO
        tong_met_kh = st.session_state.po_list[st.session_state.po_list['Ma_PO'] == loc_po]['Tong_Met'].sum()
        tong_met_sx = st.session_state.kho_btp[st.session_state.kho_btp['Nguon_PO'] == loc_po]['So_Met'].sum()
        
    tiendo = (tong_met_sx / tong_met_kh * 100) if tong_met_kh > 0 else 0

    # TẦNG 2: THẺ METRIC CHÍNH
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("📦 TỔNG KH THÀNH PHẨM", f"{tong_met_kh:,.0f} m")
    col2.metric("📝 NVL ĐÃ SỬ DỤNG", "66.9%", "10,316 / 15,425 KG", delta_color="off")
    col3.metric("♻️ TỶ LỆ PHẾ TOÀN PO", "0.47%", "Tổng phế: 82.3 KG", delta_color="inverse")
    col4.metric("📊 TIẾN ĐỘ SX TỔNG", f"{tiendo:.1f}%", f"SX: {tong_met_sx:,.0f} m")
    
    st.divider()

    # TẦNG 3: TRỰC QUAN HÓA BIỂU ĐỒ (Dark Theme như mẫu)
    c1, c2 = st.columns(2)
    
    with c1:
        st.subheader("Cơ cấu Phế & Tiến độ theo Công đoạn")
        # Biểu đồ Donut (Mô phỏng dữ liệu)
        labels = ['Lõi', 'Xoắn Đôi', 'Vách', 'Xoắn Tổng', 'Bọc']
        values = [54.3, 7.8, 0.0, 20.2, 0.0]
        fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.5)])
        fig.update_layout(template="plotly_dark", margin=dict(t=0, b=0, l=0, r=0))
        st.plotly_chart(fig, use_container_width=True)
        
    with c2:
        st.subheader("% Hoàn thành theo Công đoạn")
        # Biểu đồ Cột đứng
        fig2 = go.Figure(data=[go.Bar(x=labels, y=[103.1, 53.2, 47.3, 35.9, 0.0], marker_color='#4DA8DA')])
        fig2.update_layout(template="plotly_dark", yaxis=dict(range=[0, 110]))
        st.plotly_chart(fig2, use_container_width=True)

    # TẦNG 4: BẢNG DỮ LIỆU HIỆU SUẤT
    st.subheader("Bảng Tổng Hợp Hiệu Suất (Tự động tính)")
    df_hieu_suat = pd.DataFrame({
        'Công đoạn': labels,
        'KH (KG)': [8334, 8334, 1562, 9896, 15425],
        'Thực tế SX (KG)': [8593, 4437, 739, 3558, 0],
        '% Hoàn thành': ['103.1%', '53.2%', '47.3%', '35.9%', '0.0%'],
        'Phế (KG)': [54.3, 7.8, 0.0, 20.2, 0.0],
        '% Phế': ['0.63%', '0.18%', '0.00%', '0.56%', '0.00%'],
        'Đánh giá': ['Tốt', 'Tốt', 'Tốt', 'Tốt', 'Cần đẩy nhanh']
    })
    st.dataframe(df_hieu_suat, use_container_width=True)
