import streamlit as st
import pandas as pd
import numpy as np
import random
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px

# ==========================================
# 1. CẤU HÌNH TRANG WEB & THEME
# ==========================================
st.set_page_config(
    page_title="HỆ THỐNG MES SẢN XUẤT CÁP MẠNG (CAT6 / 0.55BC)",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .main-header {
        font-size: 24px;
        font-weight: bold;
        color: #1E88E5;
        padding-bottom: 10px;
        border-bottom: 2px solid #1E88E5;
        margin-bottom: 20px;
    }
    .metric-card {
        background-color: #1E222A;
        border-radius: 8px;
        padding: 15px;
        border-left: 5px solid #1E88E5;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    .stTable { font-size: 13px; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. KHỞI TẠO DỮ LIỆU BOM CHUẨN THEO BẢNG SẢN XUẤT
# ==========================================

# 0. Thông tin đơn hàng mẫu mặc định
if 'order_info' not in st.session_state:
    st.session_state.order_info = {
        'pcs_bl': 900,
        'pcs_wt': 396,
        'pcs_du_phong': 16,
        'quy_doi_m': 305.0
    }

# 1. Định mức bọc vỏ (1 mét TP)
if 'bom_boc_vo' not in st.session_state:
    st.session_state.bom_boc_vo = pd.DataFrame([
        {'Vật tư': 'Vỏ PVC', 'TL_KG_m': 0.013838, 'Ti_le_Pct': 35.5, 'Ghi_chu': 'NVL nhựa bọc vỏ ngoài'},
        {'Vật tư': '4 cặp màu (Xoắn Tổng)', 'TL_KG_m': 0.021084, 'Ti_le_Pct': 54.0, 'Ghi_chu': 'Bằng đồng Lõi + nhựa Lõi (xem mục 4)'},
        {'Vật tư': 'Nhựa vách', 'TL_KG_m': 0.003951, 'Ti_le_Pct': 10.1, 'Ghi_chu': 'Xương chéo định hình'},
        {'Vật tư': 'Chỉ', 'TL_KG_m': 0.000149, 'Ti_le_Pct': 0.4, 'Ghi_chu': 'Chỉ dệt/quấn xé vỏ'}
    ])

# 3. Định mức xoắn tổng (1 mét Xoắn Tổng)
if 'bom_xoan_tong' not in st.session_state:
    st.session_state.bom_xoan_tong = pd.DataFrame([
        {'Vật tư': '4 cặp màu', 'TL_KG_m': 0.021004, 'Ti_le_Pct': 84.2, 'Ghi_chu': 'Tập hợp 4 đôi xoắn'},
        {'Vật tư': 'Nhựa vách', 'TL_KG_m': 0.003951, 'Ti_le_Pct': 15.8, 'Ghi_chu': 'Vách chữ thập định hình'}
    ])

# 4. Định mức xoắn đôi (1 mét)
if 'bom_xoan_doi' not in st.session_state:
    st.session_state.bom_xoan_doi = pd.DataFrame([
        {'Cặp màu': 'XD.140.GRWH (Xanh lá - Trắng)', 'TL_KG_m': 0.005352, 'Ti_le_Pct': 25.4, 'He_so_met': 1.035},
        {'Cặp màu': 'XD.141.BLWH (Xanh dương - Trắng)', 'TL_KG_m': 0.005350, 'Ti_le_Pct': 25.4, 'He_so_met': 1.045},
        {'Cặp màu': 'XD.142.ORWH (Cam - Trắng)', 'TL_KG_m': 0.005208, 'Ti_le_Pct': 24.7, 'He_so_met': 1.030},
        {'Cặp màu': 'XD.143.BRWH (Nâu - Trắng)', 'TL_KG_m': 0.005174, 'Ti_le_Pct': 24.5, 'He_so_met': 1.025}
    ])

# 5. Định mức bọc lõi 8 màu chi tiết
if 'bom_loi' not in st.session_state:
    st.session_state.bom_loi = pd.DataFrame([
        {'Mã màu': 'LOI.262.GR (Xanh Lá)', 'TL_Dong_KG_m': 0.002157, 'TL_Nhua_KG_m': 0.000519, 'OD_mm': 0.977, 'He_so_met': 1.040},
        {'Mã màu': 'LOI.263.KẺ XANH LÁ', 'TL_Dong_KG_m': 0.002157, 'TL_Nhua_KG_m': 0.000519, 'OD_mm': 0.977, 'He_so_met': 1.040},
        {'Mã màu': 'LOI.259.BL (Xanh Dương)', 'TL_Dong_KG_m': 0.002159, 'TL_Nhua_KG_m': 0.000516, 'OD_mm': 0.967, 'He_so_met': 1.050},
        {'Mã màu': 'LOI.264.KẺ XANH DƯƠNG', 'TL_Dong_KG_m': 0.002159, 'TL_Nhua_KG_m': 0.000516, 'OD_mm': 0.967, 'He_so_met': 1.050},
        {'Mã màu': 'LOI.261.OR (Cam)', 'TL_Dong_KG_m': 0.002133, 'TL_Nhua_KG_m': 0.000471, 'OD_mm': 0.950, 'He_so_met': 1.035},
        {'Mã màu': 'LOI.265.KẺ CAM', 'TL_Dong_KG_m': 0.002133, 'TL_Nhua_KG_m': 0.000471, 'OD_mm': 0.950, 'He_so_met': 1.035},
        {'Mã màu': 'LOI.260.BR (Nâu)', 'TL_Dong_KG_m': 0.002113, 'TL_Nhua_KG_m': 0.000474, 'OD_mm': 0.955, 'He_so_met': 1.030},
        {'Mã màu': 'LOI.266.KẺ NÂU', 'TL_Dong_KG_m': 0.002113, 'TL_Nhua_KG_m': 0.000474, 'OD_mm': 0.955, 'He_so_met': 1.030}
    ])

# Dữ liệu giao dịch sản xuất giả lập
if 'po_list' not in st.session_state:
    st.session_state.po_list = pd.DataFrame([
        {'Ma_PO': 'PO-20260722-01', 'Ma_TP': 'SCP.BL.0.55BC', 'So_Luong_PCS': 900, 'Tong_Met': 274500, 'Trang_Thai': 'Đang sản xuất'},
        {'Ma_PO': 'PO-20260722-02', 'Ma_TP': 'SCP.WT.0.55BC', 'So_Luong_PCS': 396, 'Tong_Met': 120780, 'Trang_Thai': 'Chuẩn bị chạy'}
    ])

if 'xuat_kho_nvl' not in st.session_state:
    st.session_state.xuat_kho_nvl = pd.DataFrame([
        {'Nguon_PO': 'PO-20260722-01', 'Ma_NVL': '0.55BS (Đồng 0.55)', 'Ten_NVL': 'Sợi đồng bọc lõi 0.55', 'So_Luong_Xuat_KG': 4750.0},
        {'Nguon_PO': 'PO-20260722-01', 'Ma_NVL': 'Nhựa Lõi 1101', 'Ten_NVL': 'Hạt nhựa HDPE bọc lõi', 'So_Luong_Xuat_KG': 1100.0},
        {'Nguon_PO': 'PO-20260722-01', 'Ma_NVL': 'Nhựa bọc 303 BL', 'Ten_NVL': 'Hạt nhựa PVC vỏ xanh', 'So_Luong_Xuat_KG': 3820.0},
        {'Nguon_PO': 'PO-20260722-01', 'Ma_NVL': 'Nhựa vách 221 WT', 'Ten_NVL': 'Nhựa xương vách chéo', 'So_Luong_Xuat_KG': 1090.0},
        {'Nguon_PO': 'PO-20260722-01', 'Ma_NVL': 'Chỉ', 'Ten_NVL': 'Chỉ xé vỏ', 'So_Luong_Xuat_KG': 41.5}
    ])

if 'kho_btp' not in st.session_state:
    st.session_state.kho_btp = pd.DataFrame([
        {'Ma_QR': 'BTP_LOI_GR_LOT01', 'Nguon_PO': 'PO-20260722-01', 'Cong_Doan': 'Bọc lõi', 'Ma_SP': 'LOI.262.GR', 'Trong_Luong_Tinh': 1080.0, 'So_Met_Quy_Doi': 403587.0},
        {'Ma_QR': 'BTP_XD_GRWH_LOT01', 'Nguon_PO': 'PO-20260722-01', 'Cong_Doan': 'Xoắn đôi', 'Ma_SP': 'XD.140.GRWH', 'Trong_Luong_Tinh': 1480.0, 'So_Met_Quy_Doi': 276532.0},
        {'Ma_QR': 'BTP_XT_LOT01', 'Nguon_PO': 'PO-20260722-01', 'Cong_Doan': 'Xoắn tổng', 'Ma_SP': 'BTP.XT.068', 'Trong_Luong_Tinh': 6850.0, 'So_Met_Quy_Doi': 273616.0}
    ])

if 'phe_list' not in st.session_state:
    st.session_state.phe_list = pd.DataFrame([
        {'Nguon_PO': 'PO-20260722-01', 'Cong_Doan': 'Bọc lõi', 'Loai_Phe': '0.55BS (Đồng)', 'Trong_Luong_Phe_KG': 42.0},
        {'Nguon_PO': 'PO-20260722-01', 'Cong_Doan': 'Bọc lõi', 'Loai_Phe': 'Nhựa Lõi 1101', 'Trong_Luong_Phe_KG': 11.5},
        {'Nguon_PO': 'PO-20260722-01', 'Cong_Doan': 'Bọc vỏ', 'Loai_Phe': 'Nhựa bọc 303 BL', 'Trong_Luong_Phe_KG': 18.0}
    ])


# ==========================================
# 3. CÁC HÀM TÍNH TOÁN THEO CÔNG THỨC CHUẨN TRONG BẢNG
# ==========================================
def calculate_full_bom():
    # 0. Số mét quy đổi
    info = st.session_state.order_info
    m_bl = info['pcs_bl'] * info['quy_doi_m']
    m_wt = info['pcs_wt'] * info['quy_doi_m']
    m_dp = info['pcs_du_phong'] * info['quy_doi_m']
    tong_m_tp = m_bl + m_wt + m_dp

    # 5. Chi tiết Lõi
    df_loi = st.session_state.bom_loi.copy()
    df_loi['Tong_KG_m'] = df_loi['TL_Dong_KG_m'] + df_loi['TL_Nhua_KG_m']
    
    # Công thức quan trọng trong ghi chú ảnh:
    # KG Lõi = Tong_m_TP * Định mức KG/m Lõi
    # Mét Lõi = Tong_m_TP * Hệ số mét Lõi
    df_loi['KH_KG'] = tong_m_tp * df_loi['Tong_KG_m']
    df_loi['KH_Met'] = tong_m_tp * df_loi['He_so_met']
    
    df_loi['Ti_Le_Dong_Pct'] = (df_loi['TL_Dong_KG_m'] / df_loi['Tong_KG_m']) * 100
    df_loi['Ti_Le_Nhua_Pct'] = (df_loi['TL_Nhua_KG_m'] / df_loi['Tong_KG_m']) * 100
    
    # 4. Chi tiết Xoắn Đôi
    df_xd = st.session_state.bom_xoan_doi.copy()
    
    # 2. Bảng Nguyên Vật Liệu Tổng Hợp Quy Ra KG
    kg_dong_per_m = df_loi['TL_Dong_KG_m'].sum()
    kg_nhua_loi_per_m = df_loi['TL_Nhua_KG_m'].sum()
    
    df_bv = st.session_state.bom_boc_vo.copy()
    kg_nhua_vach_per_m = df_bv[df_bv['Vật tư'] == 'Nhựa vách']['TL_KG_m'].values[0] if 'Nhựa vách' in df_bv['Vật tư'].values else 0.003951
    kg_chi_per_m = df_bv[df_bv['Vật tư'] == 'Chỉ']['TL_KG_m'].values[0] if 'Chỉ' in df_bv['Vật tư'].values else 0.000149
    kg_nhua_boc_per_m = df_bv[df_bv['Vật tư'] == 'Vỏ PVC']['TL_KG_m'].values[0] if 'Vỏ PVC' in df_bv['Vật tư'].values else 0.013838

    nvl_summary = [
        {
            'NVL': '0.55BS (Sợi đồng)',
            'Định_Mức_KG_m': kg_dong_per_m,
            'KG_mã_BL': m_bl * kg_dong_per_m,
            'KG_mã_WT': m_wt * kg_dong_per_m,
            'KG_hao_hut_DP': m_dp * kg_dong_per_m,
            'TỔNG_KG_KH': tong_m_tp * kg_dong_per_m,
            'Ghi_chú': 'Đồng 0.55BC (tổng 8 lõi)'
        },
        {
            'NVL': 'Nhựa Lõi 1101',
            'Định_Mức_KG_m': kg_nhua_loi_per_m,
            'KG_mã_BL': m_bl * kg_nhua_loi_per_m,
            'KG_mã_WT': m_wt * kg_nhua_loi_per_m,
            'KG_hao_hut_DP': m_dp * kg_nhua_loi_per_m,
            'TỔNG_KG_KH': tong_m_tp * kg_nhua_loi_per_m,
            'Ghi_chú': 'Nhựa HDPE bọc lõi (tổng 8 lõi)'
        },
        {
            'NVL': 'Nhựa vách 221 WT',
            'Định_Mức_KG_m': kg_nhua_vach_per_m,
            'KG_mã_BL': m_bl * kg_nhua_vach_per_m,
            'KG_mã_WT': m_wt * kg_nhua_vach_per_m,
            'KG_hao_hut_DP': m_dp * kg_nhua_vach_per_m,
            'TỔNG_KG_KH': tong_m_tp * kg_nhua_vach_per_m,
            'Ghi_chú': 'Xương vách định hình'
        },
        {
            'NVL': 'Chỉ',
            'Định_Mức_KG_m': kg_chi_per_m,
            'KG_mã_BL': m_bl * kg_chi_per_m,
            'KG_mã_WT': m_wt * kg_chi_per_m,
            'KG_hao_hut_DP': m_dp * kg_chi_per_m,
            'TỔNG_KG_KH': tong_m_tp * kg_chi_per_m,
            'Ghi_chú': 'Chỉ xé vỏ'
        },
        {
            'NVL': 'Nhựa bọc (Vỏ ngoài)',
            'Định_Mức_KG_m': kg_nhua_boc_per_m,
            'KG_mã_BL': m_bl * kg_nhua_boc_per_m,
            'KG_mã_WT': m_wt * kg_nhua_boc_per_m,
            'KG_hao_hut_DP': m_dp * kg_nhua_boc_per_m,
            'TỔNG_KG_KH': tong_m_tp * kg_nhua_boc_per_m,
            'Ghi_chú': 'Nhựa PVC vỏ ngoài (Mã 303 dùng BL / Mã 307 dùng WT)'
        }
    ]
    df_nvl = pd.DataFrame(nvl_summary)

    return {
        'm_bl': m_bl, 'm_wt': m_wt, 'm_dp': m_dp, 'tong_m_tp': tong_m_tp,
        'df_bv': df_bv,
        'df_nvl': df_nvl,
        'df_xt': st.session_state.bom_xoan_tong,
        'df_xd': df_xd,
        'df_loi': df_loi
    }


# ==========================================
# 4. CHỨC NĂNG 1: QUẢN LÝ ĐỊNH MỨC BOM CHUẨN (GIỐNG BẢNG ẢNH 100%)
# ==========================================
def render_bom_page():
    st.markdown("<div class='main-header'>📋 BOM CHUẨN — ĐỊNH MỨC CHI TIẾT THEO MÉT / MÃ HÀNG CÁP MẠNG</div>", unsafe_allow_html=True)
    
    st.caption("📌 *Dữ liệu tính toán dựa trên định mức chuẩn 1 mét Thành Phẩm (TP). Bạn có thể chỉnh sửa trực tiếp các thông số dưới đây.*")
    
    # 0. THÔNG TIN ĐƠN HÀNG & QUY ĐỔI ĐƠN VỊ
    with st.expander("0. THÔNG TIN ĐƠN HÀNG & QUY ĐỔI ĐƠN VỊ", expanded=True):
        c1, c2, c3, c4 = st.columns(4)
        info = st.session_state.order_info
        info['pcs_bl'] = c1.number_input("Đơn hàng SCP.BL.0.55BC (PCS)", min_value=0, value=info['pcs_bl'])
        info['pcs_wt'] = c2.number_input("Đơn hàng SCP.WT.0.55BC (PCS)", min_value=0, value=info['pcs_wt'])
        info['pcs_du_phong'] = c3.number_input("Hao hụt dự phòng (PCS)", min_value=0, value=info['pcs_du_phong'])
        info['quy_doi_m'] = c4.number_input("Quy đổi 1 PCS = Mét", min_value=1.0, value=info['quy_doi_m'])

    # Tính toán lại toàn bộ dữ liệu
    calc = calculate_full_bom()

    # Bảng hiển thị tóm tắt mét
    st.info(f"""
    🔹 **Mét mã SCP.BL.0.55BC:** {calc['m_bl']:,} m  |  
    🔹 **Mét mã SCP.WT.0.55BC:** {calc['m_wt']:,} m  |  
    🔹 **Mét dự phòng:** {calc['m_dp']:,} m  
    👉 **TỔNG SỐ MÉT TP KẾ HOẠCH (KẾT HỢP): {calc['tong_m_tp']:,} MÉT**
    """)

    # TABS CHI TIẾT 5 MỤC ĐỊNH MỨC
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "1. Định Mức Bọc Vỏ", 
        "2. Nhu Cầu NVL Quy Ra KG", 
        "3. Định Mức Xoắn Tổng", 
        "4. Định Mức Xoắn Đôi", 
        "5. Định Mức Bọc Lõi (8 Màu)"
    ])

    with tab1:
        st.subheader("1. ĐỊNH MỨC BỌC VỎ (tính cho 1 mét Thành phẩm)")
        ed_bv = st.data_editor(
            st.session_state.bom_boc_vo,
            num_rows="dynamic",
            use_container_width=True,
            key="ed_boc_vo"
        )
        st.session_state.bom_boc_vo = ed_bv
        st.caption(f"**Tổng Trọng Lượng Bọc Vỏ / 1m TP:** `{ed_bv['TL_KG_m'].sum():.6f} KG/m` | **OD ngoài:** `6.1 mm`")

    with tab2:
        st.subheader("2. NGUYÊN VẬT LIỆU QUY RA KG THEO MÃ HÀNG")
        df_nvl = calc['df_nvl']
        st.dataframe(
            df_nvl.style.format({
                'Định_Mức_KG_m': '{:.6f}',
                'KG_mã_BL': '{:,.2f}',
                'KG_mã_WT': '{:,.2f}',
                'KG_hao_hut_DP': '{:,.2f}',
                'TỔNG_KG_KH': '{:,.2f}'
            }),
            use_container_width=True
        )
        
        # Dòng tổng cộng
        tong_kg = df_nvl['TỔNG_KG_KH'].sum()
        st.success(f"⚖️ **TỔNG NHU CẦU NGUYÊN VẬT LIỆU TẤT CẢ LÀ: {tong_kg:,.2f} KG** (~ {tong_kg/1000:.2f} Tấn)")

    with tab3:
        st.subheader("3. ĐỊNH MỨC XOẮN TỔNG (Mã BTP: BTP.XT.068)")
        ed_xt = st.data_editor(
            st.session_state.bom_xoan_tong,
            num_rows="dynamic",
            use_container_width=True,
            key="ed_xoan_tong"
        )
        st.session_state.bom_xoan_tong = ed_xt
        st.caption("Hệ số mét quy đổi Xoắn Tổng: **1.005** (1m TP cần 1.005m Xoắn Tổng)")

    with tab4:
        st.subheader("4. ĐỊNH MỨC XOẮN ĐÔI (theo từng cặp màu)")
        ed_xd = st.data_editor(
            st.session_state.bom_xoan_doi,
            num_rows="dynamic",
            use_container_width=True,
            key="ed_xoan_doi"
        )
        st.session_state.bom_xoan_doi = ed_xd
        st.caption(f"**Tổng Định Mức 4 Đôi Xoắn / 1m TP:** `{ed_xd['TL_KG_m'].sum():.6f} KG/m`")

    with tab5:
        st.subheader("5. ĐỊNH MỨC LÕI BỌC HDPE (Chi tiết 8 màu)")
        st.warning("⚠️ **Ghi chú công thức quan trọng:** KG Lõi = Mét TP × Định mức KG/m Lõi. Mét Lõi = Mét TP × Hệ số mét công đoạn.")
        
        ed_loi = st.data_editor(
            st.session_state.bom_loi,
            num_rows="dynamic",
            use_container_width=True,
            key="ed_loi"
        )
        st.session_state.bom_loi = ed_loi
        
        # Bảng tính kết quả tự động
        df_loi_calc = calc['df_loi']
        st.write("📊 **Kết quả tính toán nhu cầu sản xuất Bọc Lõi theo đơn hàng:**")
        st.dataframe(
            df_loi_calc[['Mã màu', 'TL_Dong_KG_m', 'TL_Nhua_KG_m', 'Tong_KG_m', 'OD_mm', 'He_so_met', 'Ti_Le_Dong_Pct', 'Ti_Le_Nhua_Pct', 'KH_KG', 'KH_Met']].style.format({
                'TL_Dong_KG_m': '{:.6f}',
                'TL_Nhua_KG_m': '{:.6f}',
                'Tong_KG_m': '{:.6f}',
                'OD_mm': '{:.3f}',
                'He_so_met': '{:.3f}',
                'Ti_Le_Dong_Pct': '{:.1f}%',
                'Ti_Le_Nhua_Pct': '{:.1f}%',
                'KH_KG': '{:,.2f}',
                'KH_Met': '{:,.0f}'
            }),
            use_container_width=True
        )
        
        c_k1, c_k2 = st.columns(2)
        c_k1.metric("Tổng Trọng Lượng Đồng Cần Cho 8 Lõi", f"{df_loi_calc['KH_KG'].sum() * (df_loi_calc['TL_Dong_KG_m'].sum()/df_loi_calc['Tong_KG_m'].sum()):,.2f} KG")
        c_k2.metric("Tổng Số Mét Lõi Phải Đùn (Tổng 8 màu)", f"{df_loi_calc['KH_Met'].sum():,.0f} Mét")


# ==========================================
# 5. CHỨC NĂNG 2: LỆNH PO & XUẤT KHO NVL
# ==========================================
def render_po_page():
    st.markdown("<div class='main-header'>📝 QUẢN LÝ LỆNH SẢN XUẤT (PO) & XUẤT NVL</div>", unsafe_allow_html=True)
    c1, c2 = st.columns([1, 1])
    
    with c1:
        st.subheader("1. Tạo PO Mới")
        with st.form("f_create_po"):
            ma_po = st.text_input("Mã Lệnh PO", f"PO-{datetime.now().strftime('%Y%m%d')}-01")
            ma_tp = st.selectbox("Mã Hàng Thành Phẩm", ["SCP.BL.0.55BC", "SCP.WT.0.55BC"])
            sl_pcs = st.number_input("Số Lượng Cuộn/Thùng (PCS)", min_value=1, value=300)
            quy_doi = st.number_input("Chiều dài 1 PCS (Mét)", min_value=1.0, value=305.0)
            if st.form_submit_button("➕ Khởi Tạo PO"):
                tong_m = sl_pcs * quy_doi
                new_po = pd.DataFrame([{'Ma_PO': ma_po, 'Ma_TP': ma_tp, 'So_Luong_PCS': sl_pcs, 'Tong_Met': tong_m, 'Trang_Thai': 'Đang sản xuất'}])
                st.session_state.po_list = pd.concat([st.session_state.po_list, new_po], ignore_index=True)
                st.success(f"Đã tạo PO {ma_po} thành công!")
                
        st.write("📋 **Danh sách PO hiện tại:**")
        st.dataframe(st.session_state.po_list, use_container_width=True)

    with c2:
        st.subheader("2. Xuất Kho NVL Cho Sản Xuất")
        with st.form("f_xuat_nvl"):
            po_target = st.selectbox("Chọn Lệnh PO Nhận NVL", st.session_state.po_list['Ma_PO'].tolist())
            list_nvl = ["0.55BS (Đồng 0.55)", "Nhựa Lõi 1101", "Nhựa bọc 303 BL", "Nhựa bọc 307 WT", "Nhựa vách 221 WT", "Chỉ"]
            ma_nvl = st.selectbox("Chọn Nguyên Vật Liệu", list_nvl)
            kg_xuat = st.number_input("Số Lượng Xuất Kho (KG)", min_value=0.1, value=500.0)
            if st.form_submit_button("📦 Xuất NVL"):
                new_xuat = pd.DataFrame([{'Nguon_PO': po_target, 'Ma_NVL': ma_nvl, 'Ten_NVL': ma_nvl, 'So_Luong_Xuat_KG': kg_xuat}])
                st.session_state.xuat_kho_nvl = pd.concat([st.session_state.xuat_kho_nvl, new_xuat], ignore_index=True)
                st.success("Đã ghi nhận phiếu xuất kho NVL!")

        st.write("📜 **Lịch sử xuất kho NVL:**")
        st.dataframe(st.session_state.xuat_kho_nvl, use_container_width=True)


# ==========================================
# 6. CHỨC NĂNG 3: TRẠM CÂN BTP (TỰ ĐỘNG QUY ĐỔI MÉT)
# ==========================================
def render_can_page():
    st.markdown("<div class='main-header'>📦 TRẠM CÂN BTP / THÀNH PHẨM (MÔ PHỎNG TÍN HIỆU CÂN COM)</div>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("1. Thông Tin Lô Hàng Cân")
        po_sel = st.selectbox("Chọn PO", st.session_state.po_list['Ma_PO'].tolist())
        cd_sel = st.selectbox("Công Đoạn Cân", ["Bọc lõi", "Xoắn đôi", "Xoắn tổng", "Bọc vỏ"])
        
        # Lấy danh sách mã SP tương ứng công đoạn
        if cd_sel == "Bọc lõi":
            list_sp = st.session_state.bom_loi['Mã màu'].tolist()
        elif cd_sel == "Xoắn đôi":
            list_sp = st.session_state.bom_xoan_doi['Cặp màu'].tolist()
        elif cd_sel == "Xoắn tổng":
            list_sp = ["BTP.XT.068"]
        else:
            list_sp = ["SCP.BL.0.55BC", "SCP.WT.0.55BC"]
            
        ma_sp_sel = st.selectbox("Mã Sản Phẩm / BTP", list_sp)

    with col2:
        st.subheader("2. Đọc Tín Hiệu & Quy Đổi Số Mét")
        mode = st.radio("Chế độ đọc cân:", ["⚖️ Tự Động Từ Cân Điện Tử", "⌨️ Nhập Thủ Công"], horizontal=True)
        
        if mode == "⚖️ Tự Động Từ Cân Điện Tử":
            if 'sim_weight' not in st.session_state:
                st.session_state.sim_weight = 250.80
            
            tl_tong = st.number_input("Tổng KG (Đọc từ Cân)", value=st.session_state.sim_weight, disabled=True)
            if st.button("🔄 Nhận Tín Hiệu Cân Mới"):
                st.session_state.sim_weight = round(random.uniform(50.0, 500.0), 2)
                st.rerun()
        else:
            tl_tong = st.number_input("Nhập Tổng KG Trên Cân", min_value=0.0, value=200.0)

        tl_bi = st.number_input("Trọng Lượng Bì / Rulo / Pallet (KG)", min_value=0.0, value=12.5)
        tl_tinh = max(0.0, tl_tong - tl_bi)

        # Tra cứu định mức KG/m từ BOM
        dm_kg_m = 0.002676 # Mặc định
        if cd_sel == "Bọc lõi":
            row = st.session_state.bom_loi[st.session_state.bom_loi['Mã màu'] == ma_sp_sel]
            if not row.empty:
                dm_kg_m = row['TL_Dong_KG_m'].values[0] + row['TL_Nhua_KG_m'].values[0]
        elif cd_sel == "Xoắn đôi":
            row = st.session_state.bom_xoan_doi[st.session_state.bom_xoan_doi['Cặp màu'] == ma_sp_sel]
            if not row.empty:
                dm_kg_m = row['TL_KG_m'].values[0]
        elif cd_sel == "Xoắn tổng":
            dm_kg_m = 0.025035
        else:
            dm_kg_m = 0.039022

        so_met_qd = (tl_tinh / dm_kg_m) if dm_kg_m > 0 else 0.0

        st.markdown(f"""
        <div style="background-color: #0E1117; padding: 15px; border-radius: 8px; border: 1px solid #1E88E5;">
            <h3 style="color: #4CAF50; margin:0;">⚖️ Tịnh: {tl_tinh:.2f} KG</h3>
            <h3 style="color: #2196F3; margin:0;">📏 Số Mét Quy Đổi: {so_met_qd:,.0f} MÉT</h3>
            <small><i>(Định mức tra cứu BOM: {dm_kg_m:.6f} KG/m)</i></small>
        </div>
        """, unsafe_allow_html=True)

        st.write("")
        if st.button("💾 Lưu Nhập Kho BTP & In Mã QR", type="primary"):
            qr_code = f"QR_{cd_sel[:2].upper()}_{datetime.now().strftime('%m%d%H%M%S')}"
            new_btp = pd.DataFrame([{
                'Ma_QR': qr_code, 'Nguon_PO': po_sel, 'Cong_Doan': cd_sel,
                'Ma_SP': ma_sp_sel, 'Trong_Luong_Tinh': tl_tinh, 'So_Met_Quy_Doi': so_met_qd
            }])
            st.session_state.kho_btp = pd.concat([st.session_state.kho_btp, new_btp], ignore_index=True)
            st.success(f"Đã lưu nhập kho BTP! Mã Barcode/QR: **{qr_code}**")

    st.write("---")
    st.subheader("📋 Danh Sách BTP Trong Kho Công Đoạn")
    st.dataframe(st.session_state.kho_btp, use_container_width=True)


# ==========================================
# 7. CHỨC NĂNG 4: GHI NHẬN PHẾ LIỆU CÔNG ĐOẠN
# ==========================================
def render_phe_page():
    st.markdown("<div class='main-header'>♻️ GHI NHẬN PHẾ LIỆU & HAO HỤT CÔNG ĐOẠN</div>", unsafe_allow_html=True)
    
    with st.form("f_phe_input"):
        c1, c2, c3, c4 = st.columns(4)
        po_sel = c1.selectbox("Thuộc Lệnh PO", st.session_state.po_list['Ma_PO'].tolist())
        cd_sel = c2.selectbox("Công Đoạn Phát Sinh Phế", ["Bọc lõi", "Xoắn đôi", "Xoắn tổng", "Bọc vỏ"])
        loai_phe = c3.selectbox("Loại Phế Thu Gom", ["0.55BS (Đồng)", "Nhựa Lõi 1101", "Nhựa vách 221 WT", "Nhựa bọc 303 BL", "Chỉ", "BTP Dây Hỏng"])
        tl_phe = c4.number_input("Trọng Lượng Phế (KG)", min_value=0.1, value=5.0)
        
        if st.form_submit_button("📌 Ghi Nhận Phế"):
            new_phe = pd.DataFrame([{
                'Nguon_PO': po_sel, 'Cong_Doan': cd_sel, 'Loai_Phe': loai_phe, 'Trong_Luong_Phe_KG': tl_phe
            }])
            st.session_state.phe_list = pd.concat([st.session_state.phe_list, new_phe], ignore_index=True)
            st.success("Đã ghi nhận dữ liệu phế thành công!")

    st.subheader("📊 Bảng Thống Kê Phế Đã Thu Gom")
    st.dataframe(st.session_state.phe_list, use_container_width=True)


# ==========================================
# 8. CHỨC NĂNG 5: QUYẾT TOÁN & ĐỐI SOÁT ĐỒNG / NHỰA
# ==========================================
def render_quyet_toan_page():
    st.markdown("<div class='main-header'>⚖️ QUYẾT TOÁN & ĐỐI SOÁT NVL (ĐỒNG / NHỰA) THEO PO</div>", unsafe_allow_html=True)
    
    po_sel = st.selectbox("Chọn Lệnh PO Cần Quyết Toán:", st.session_state.po_list['Ma_PO'].tolist())
    
    # Lọc dữ liệu theo PO
    df_xuat = st.session_state.xuat_kho_nvl[st.session_state.xuat_kho_nvl['Nguon_PO'] == po_sel]
    df_btp = st.session_state.kho_btp[st.session_state.kho_btp['Nguon_PO'] == po_sel]
    df_phe = st.session_state.phe_list[st.session_state.phe_list['Nguon_PO'] == po_sel]

    st.write("📊 **Bảng Cân Đối Vật Tư - Xuất / BTP / Phế / Thất Thoát:**")
    
    # Lấy tính toán BOM
    calc = calculate_full_bom()
    df_nvl_bom = calc['df_nvl']
    
    rows = []
    for _, item in df_nvl_bom.iterrows():
        nvl_name = item['NVL']
        
        # 1. Tổng xuất
        kg_xuat = df_xuat[df_xuat['Ma_NVL'].str.contains(nvl_name[:4], na=False)]['So_Luong_Xuat_KG'].sum() if not df_xuat.empty else 0.0
        
        # 2. Đã nằm trong BTP
        kg_btp = 0.0
        if "Đồng" in nvl_name or "0.55BS" in nvl_name:
            met_loi = df_btp[df_btp['Cong_Doan'] == 'Bọc lõi']['So_Met_Quy_Doi'].sum()
            kg_btp = met_loi * item['Định_Mức_KG_m']
        else:
            met_btp = df_btp['So_Met_Quy_Doi'].sum()
            kg_btp = met_btp * item['Định_Mức_KG_m'] * 0.1
            
        # 3. Phế thu gom
        kg_phe = df_phe[df_phe['Loai_Phe'].str.contains(nvl_name[:4], na=False)]['Trong_Luong_Phe_KG'].sum() if not df_phe.empty else 0.0
        
        # 4. Thất thoát / Chênh lệch
        kg_loss = kg_xuat - (kg_btp + kg_phe)
        pct_loss = (kg_loss / kg_xuat * 100) if kg_xuat > 0 else 0.0
        
        rows.append({
            'Loại Vật Tư': nvl_name,
            '1. Tổng Xuất Kho (KG)': round(kg_xuat, 2),
            '2. Trong BTP/Thành Phẩm (KG)': round(kg_btp, 2),
            '3. Phế Thu Gom (KG)': round(kg_phe, 2),
            '4. Thất Thoát / Chênh Lệch (KG)': round(kg_loss, 2),
            'Tỷ Lệ Thất Thoát (%)': f"{pct_loss:.2f}%"
        })
        
    df_qt = pd.DataFrame(rows)
    st.dataframe(df_qt, use_container_width=True)


# ==========================================
# 9. CHỨC NĂNG 6: DASHBOARD TIẾN ĐỘ & BÁO CÁO
# ==========================================
def render_dashboard_page():
    st.markdown("<div class='main-header'>📊 DASHBOARD TỔNG QUAN TIẾN ĐỘ SẢN XUẤT</div>", unsafe_allow_html=True)
    
    # Metrics tổng quan
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Tổng Mét Lõi Đã Bọc", f"{st.session_state.kho_btp[st.session_state.kho_btp['Cong_Doan']=='Bọc lõi']['So_Met_Quy_Doi'].sum():,.0f} m")
    m2.metric("Tổng Mét Xoắn Đôi", f"{st.session_state.kho_btp[st.session_state.kho_btp['Cong_Doan']=='Xoắn đôi']['So_Met_Quy_Doi'].sum():,.0f} m")
    m3.metric("Tổng Mét Xoắn Tổng", f"{st.session_state.kho_btp[st.session_state.kho_btp['Cong_Doan']=='Xoắn tổng']['So_Met_Quy_Doi'].sum():,.0f} m")
    m4.metric("Tổng Phế Thu Gom", f"{st.session_state.phe_list['Trong_Luong_Phe_KG'].sum():,.1f} KG")

    st.write("---")
    
    # Biểu đồ tiến độ
    cd_list = ["Bọc lõi", "Xoắn đôi", "Xoắn tổng", "Bọc vỏ"]
    met_by_cd = [st.session_state.kho_btp[st.session_state.kho_btp['Cong_Doan']==cd]['So_Met_Quy_Doi'].sum() for cd in cd_list]
    
    fig = go.Figure(data=[
        go.Bar(name='Sản lượng (Mét)', x=cd_list, y=met_by_cd, marker_color='#1E88E5')
    ])
    fig.update_layout(title="Sản Lượng BTP Theo Công Đoạn (Mét)", template="plotly_dark", height=400)
    st.plotly_chart(fig, use_container_width=True)


# ==========================================
# 10. MENUBAR VÀ ĐIỀU HƯỚNG CHÍNH
# ==========================================
def main():
    st.sidebar.title("🏭 MES CÁP MẠNG")
    st.sidebar.caption("Phiên bản: 3.0 (BOM Chuẩn SCP 0.55BC)")
    
    menu = st.sidebar.radio(
        "CHỌN CHỨC NĂNG:",
        [
            "1. Định Mức BOM Chuẩn", 
            "2. Lệnh PO & Xuất NVL", 
            "3. Trạm Cân BTP", 
            "4. Ghi Nhận Phế", 
            "5. Quyết Toán Đồng/Nhựa",
            "6. Dashboard Tiến Độ"
        ]
    )

    if menu == "1. Định Mức BOM Chuẩn":
        render_bom_page()
    elif menu == "2. Lệnh PO & Xuất NVL":
        render_po_page()
    elif menu == "3. Trạm Cân BTP":
        render_can_page()
    elif menu == "4. Ghi Nhận Phế":
        render_phe_page()
    elif menu == "5. Quyết Toán Đồng/Nhựa":
        render_quyet_toan_page()
    elif menu == "6. Dashboard Tiến Độ":
        render_dashboard_page()

if __name__ == '__main__':
    main()
