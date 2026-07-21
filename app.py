import streamlit as st
import pandas as pd

# Cấu hình trang web
st.set_page_config(page_title="Hệ thống MES - Quản lý BOM Cáp Mạng", layout="wide")

st.title("⚡ HỆ THỐNG MES - QUẢN LÝ BOM & TÍNH ĐỊNH MỨC CÁP MẠNG")
st.caption("Dựa trên quy trình sản xuất cáp 4 cặp xoắn đôi (Core -> Pair -> Assembly -> Sheathing)")

st.divider()

# ==========================================
# TAB 1: THÔNG TIN ĐƠN HÀNG & QUY ĐỔI MET
# ==========================================
st.sidebar.header("📋 1. Thông Tin Đơn Hàng")
code_scp_bl = st.sidebar.text_input("Mã đơn BL", "SCP.BL.0.55BC")
qty_bl_pcs = st.sidebar.number_input("Số lượng mã BL (PCS)", value=900)

code_scp_wt = st.sidebar.text_input("Mã đơn WT", "SCP.WT.0.55BC")
qty_wt_pcs = st.sidebar.number_input("Số lượng mã WT (PCS)", value=396)

pcs_to_meter = st.sidebar.number_input("Quy đổi 1 PCS = (Mét)", value=305.0)
hao_hut_pct = st.sidebar.number_input("Tỷ lệ hao hụt dự phòng (%)", value=4.0) / 100

# Tính toán tổng mét
met_bl = qty_bl_pcs * pcs_to_meter
met_wt = qty_wt_pcs * pcs_to_meter
met_tong_chua_hh = met_bl + met_wt
met_hao_hut = met_tong_chua_hh * hao_hut_pct
met_tong_kh = met_tong_chua_hh + met_hao_hut

st.subheader("📌 0. Tổng Quan Đơn Hàng & Kế Hoạch Sản Xuất")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Tổng Mét SCP.BL", f"{met_bl:,.1f} m")
col2.metric("Tổng Mét SCP.WT", f"{met_wt:,.1f} m")
col3.metric("Mét Hao Hụt Dự Phòng", f"{met_hao_hut:,.1f} m")
col4.metric("🎯 TỔNG MÉT TP KẾ HOẠCH", f"{met_tong_kh:,.1f} m")

st.divider()

# ==========================================
# TAB 2: CẤU HÌNH ĐỊNH MỨC TỪNG CÔNG ĐOẠN
# ==========================================
tab_boc, tab_xt, tab_xd, tab_loi = st.tabs([
    "1. ĐỊNH MỨC BỌC VỎ", 
    "2. ĐỊNH MỨC XOẮN TỔNG", 
    "3. ĐỊNH MỨC XOẮN ĐÔI", 
    "4. ĐỊNH MỨC LÕI (8 MÀU)"
])

with tab_boc:
    st.markdown("### Định mức Công đoạn Bọc (Tính cho 1 mét Thành phẩm)")
    col_b1, col_b2 = st.columns(2)
    with col_b1:
        tl_pvc = st.number_input("T.L Vỏ PVC (KG/mét)", value=0.013838, format="%.6f")
        tl_chi = st.number_input("T.L Chỉ xé (KG/mét)", value=0.000149, format="%.6f")
    with col_b2:
        od_vo = st.number_input("Đường kính ngoài OD (mm)", value=6.1)
        he_so_met_boc = st.number_input("Hệ số mét Bọc vỏ", value=1.0)

with tab_xt:
    st.markdown("### Định mức Công đoạn Xoắn Tổng (BTP.XT.068)")
    col_xt1, col_xt2 = st.columns(2)
    with col_xt1:
        tl_vach = st.number_input("T.L Nhựa vách chữ thập (KG/mét)", value=0.003951, format="%.6f")
    with col_xt2:
        he_so_met_xt = st.number_input("Hệ số mét Xoắn tổng", value=1.005)

with tab_xd:
    st.markdown("### Định mức Xoắn Đôi (4 Cặp màu)")
    data_xd = {
        "Cặp màu": ["XD.140.GRWH (Xanh lá - Trắng)", "XD.141.BLWH (Xanh dương - Trắng)", "XD.142.ORWH (Cam - Trắng)", "XD.143.BRWH (Nâu - Trắng)"],
        "Hệ số mét Xoắn": [1.035, 1.045, 1.030, 1.025]
    }
    df_xd = st.data_editor(pd.DataFrame(data_xd), num_rows="dynamic", use_container_width=True)

with tab_loi:
    st.markdown("### Định mức Chi tiết 8 Lõi Dây")
    default_loi = {
        "Mã màu lõi": ["LOI.262.GR", "LOI.263.KẺ XANH LÁ", "LOI.259.BL", "LOI.264.KẺ XANH DƯƠNG", "LOI.261.OR", "LOI.265.KẺ CAM", "LOI.260.BR", "LOI.266.KẺ NÂU"],
        "T.L Đồng (KG/m)": [0.002157, 0.002157, 0.002159, 0.002159, 0.002133, 0.002133, 0.002113, 0.002113],
        "T.L Nhựa (KG/m)": [0.000519, 0.000519, 0.000516, 0.000516, 0.000471, 0.000471, 0.000474, 0.000474],
        "OD Lõi (mm)": [0.977, 0.977, 0.967, 0.967, 0.950, 0.950, 0.955, 0.955],
        "Hệ số mét Lõi": [1.040, 1.040, 1.050, 1.050, 1.035, 1.035, 1.030, 1.030],
        "Thuộc Cặp Xoắn": [0, 0, 1, 1, 2, 2, 3, 3] # Chỉ số ứng với 4 cặp ở Tab Xoắn đôi
    }
    df_loi = st.data_editor(pd.DataFrame(default_loi), num_rows="dynamic", use_container_width=True)

st.divider()

# ==========================================
# 3. TÍNH TOÁN VÀ XUẤT BẢNG NGUYÊN VẬT LIỆU
# ==========================================
st.subheader("📊 2. Bảng Tổng Hợp Nhu Cầu Nguyên Vật Liệu (Tính theo Đơn hàng)")

if st.button("🚀 TÍNH TOÁN ĐỊNH MỨC NVL", type="primary"):
    # 1. Tính chiều dài BTP qua các công đoạn
    met_boc = met_tong_kh * he_so_met_boc
    met_xoan_tong = met_boc * he_so_met_xt
    
    # 2. Tính cho từng Lõi
    df_loi_calc = df_loi.copy()
    
    # Tính Mét Lõi thực tế = Mét TP * HS_Bọc * HS_XT * HS_XD * HS_Lõi
    met_loi_list = []
    kg_dong_list = []
    kg_nhua_loi_list = []
    
    for idx, row in df_loi_calc.iterrows():
        cap_idx = int(row["Thuộc Cặp Xoắn"])
        hs_xd = df_xd.iloc[cap_idx]["Hệ số mét Xoắn"]
        
        # Hệ số mét tích lũy
        met_loi_thuc_te = met_xoan_tong * hs_xd * row["Hệ số mét Lõi"]
        
        kg_dong = met_loi_thuc_te * row["T.L Đồng (KG/m)"]
        kg_nhua = met_loi_thuc_te * row["T.L Nhựa (KG/m)"]
        
        met_loi_list.append(met_loi_thuc_te)
        kg_dong_list.append(kg_dong)
        kg_nhua_loi_list.append(kg_nhua)
        
    df_loi_calc["Sản lượng Mét Lõi (m)"] = met_loi_list
    df_loi_calc["Tổng Đồng (KG)"] = kg_dong_list
    df_loi_calc["Tổng Nhựa Lõi (KG)"] = kg_nhua_loi_list
    
    # Tổng các vật tư chính
    tong_kg_dong = sum(kg_dong_list)
    tong_kg_nhua_loi = sum(kg_nhua_loi_list)
    tong_kg_nhua_vach = met_xoan_tong * tl_vach
    tong_kg_pvc = met_boc * tl_pvc
    tong_kg_chi = met_boc * tl_chi
    
    tong_nvl_kg = tong_kg_dong + tong_kg_nhua_loi + tong_kg_nhua_vach + tong_kg_pvc + tong_kg_chi

    # Hiển thị kết quả chi tiết từng lõi
    st.markdown("#### A. Bảng Chi Tiết Định Mức 8 Lõi")
    st.dataframe(df_loi_calc[["Mã màu lõi", "Hệ số mét Lõi", "Sản lượng Mét Lõi (m)", "Tổng Đồng (KG)", "Tổng Nhựa Lõi (KG)"]], use_container_width=True)

    # Hiển thị bảng tổng hợp NVL xuất kho
    st.markdown("#### B. Bảng Tổng Hợp Nguyên Vật Liệu Cần Cho Đơn Hàng (KG)")
    
    df_summary = pd.DataFrame({
        "Loại Nguyên Vật Liệu": ["Đồng (0.55BC)", "Nhựa Lõi (HDPE/PE)", "Nhựa Vách Chữ Thập", "Nhựa Vỏ (PVC)", "Chỉ Xé"],
        "Tổng Khối Lượng (KG)": [tong_kg_dong, tong_kg_nhua_loi, tong_kg_nhua_vach, tong_kg_pvc, tong_kg_chi],
        "Tỷ lệ % Trong TP": [
            (tong_kg_dong/tong_nvl_kg)*100, 
            (tong_kg_nhua_loi/tong_nvl_kg)*100, 
            (tong_kg_nhua_vach/tong_nvl_kg)*100, 
            (tong_kg_pvc/tong_nvl_kg)*100, 
            (tong_kg_chi/tong_nvl_kg)*100
        ]
    })
    
    st.table(df_summary.style.format({"Tổng Khối Lượng (KG)": "{:,.2f}", "Tỷ lệ % Trong TP": "{:.2f}%"}))
    st.success(f"⚖️ **TỔNG NGUYÊN VẬT LIỆU CẦN CHUẨN BỊ:** **{tong_nvl_kg:,.2f} KG**")
