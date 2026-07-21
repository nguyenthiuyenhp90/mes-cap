import streamlit as st
import pandas as pd
import qrcode
from io import BytesIO
from PIL import Image
import datetime

# ----------------------------------------------------
# 1. CẤU HÌNH TRANG WEB
# ----------------------------------------------------
st.set_page_config(page_title="Hệ Thống MES - Cáp Mạng", page_icon="⚡", layout="wide")

# ----------------------------------------------------
# 2. KHỞI TẠO DỮ LIỆU KHO ẢO & TỪ ĐIỂN BOM MASTER
# ----------------------------------------------------
if 'inventory' not in st.session_state:
    st.session_state['inventory'] = pd.DataFrame(columns=["Mã QR", "Mã Hàng", "Loại", "Số Lô", "Số Mét (m)", "Trọng Lượng (kg)", "Thời Gian Nhập"])
if 'history' not in st.session_state:
    st.session_state['history'] = []

# TỪ ĐIỂN BOM MASTER (Làm cơ sở dữ liệu ngầm cho Module 2 và Module 3)
BOM_DB = {
    "TP": {
        "SCP.BL.0.55BC": {"BTP": "BTP.XT.068", "Nhua_Vo_kg_m": 0.013838, "Mau_Vo": "PVC Xanh Dương", "Tong_TL_kg_m": 0.039022},
        "SCP.WT.0.55BC": {"BTP": "BTP.XT.068", "Nhua_Vo_kg_m": 0.013838, "Mau_Vo": "PVC Trắng", "Tong_TL_kg_m": 0.039022},
        "SCP.GR.0.55BC": {"BTP": "BTP.XT.068", "Nhua_Vo_kg_m": 0.013838, "Mau_Vo": "PVC Xanh Lá", "Tong_TL_kg_m": 0.039022}
    },
    "BTP": {
        "BTP.XT.068": {
            "Dong_kg_m": 0.017120, 
            "Nhua_Loi_kg_m": 0.003964, 
            "Nhua_Vach_kg_m": 0.003951, 
            "HeSo_XT": 1.005,
            "Tong_TL_kg_m": 0.021084
        }
    },
    "LOI": {
        "Lõi Đồng 0.81": {"Tong_TL_kg_m": 0.00461},
        "Lõi Đồng 0.78": {"Tong_TL_kg_m": 0.00428}
    }
}

def create_qr_code(data_string):
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=6, border=2)
    qr.add_data(data_string)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

# ----------------------------------------------------
# 3. SIDEBAR ĐIỀU HƯỚNG
# ----------------------------------------------------
st.sidebar.title("🏭 HỆ THỐNG MES CÁP MẠNG")
st.sidebar.caption("Phiên bản Tích hợp Trọng Lượng Bì & Kho Barcode")

module_choice = st.sidebar.radio(
    "CHỌN MÔ-ĐUN LÀM VIỆC:",
    [
        "1. Quản lý BOM Master & Định mức",
        "2. Tiếp Nhận PO & Lập Lệnh Sản Xuất",
        "3. Nhật ký SX, Quản lý Kho & Quyết toán"
    ]
)

st.sidebar.divider()
st.sidebar.info("💡 **Tính năng Cân Điện Tử:**\nTại Mô-đun 3, hệ thống sẽ lấy [Tổng] - [Bì] = [Tịnh], sau đó tự động chia cho hệ số BOM để ra [Số Mét].")

# ====================================================
# MODULE 1: QUẢN LÝ BOM MASTER (Giữ nguyên cấu trúc gốc)
# ====================================================
if module_choice == "1. Quản lý BOM Master & Định mức":
    st.header("📋 MODULE 1: QUẢN LÝ BOM & ĐỊNH MỨC CHI TIẾT")
    
    search_bom = st.text_input("🔍 Tìm kiếm Mã Sản Phẩm / BOM (VD: SCP.BL, SCP.WT...):", placeholder="Nhập mã để tìm nhanh...")
    st.markdown("---")

    tab0, tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "0. Đơn Hàng & Kế Hoạch", "1. Định Mức Bọc Vỏ", "2. Định Mức Xoắn Tổng", 
        "3. Định Mức Xoắn Đôi", "4. Chi Tiết 8 Lõi", "5. Tổng Hợp NVL"
    ])

    with tab0:
        st.subheader("0. KẾ HOẠCH THEO ĐƠN HÀNG (MÉT TP)")
        c1, c2, c3 = st.columns(3)
        with c1:
            code_bl = st.text_input("Mã SP 1:", "SCP.BL.0.55BC" if not search_bom else search_bom)
            pcs_bl = st.number_input("Số cuộn (PCS)", value=900)
        with c2:
            pcs_to_m = st.number_input("1 PCS = (Mét)", value=305.0)
            pct_du_phong = st.number_input("Dự phòng hao hụt (%)", value=4.0) / 100
        with c3:
            met_bl = pcs_bl * pcs_to_m
            met_hh = met_bl * pct_du_phong
            met_tong_kh = met_bl + met_hh
            st.metric("🎯 TỔNG SỐ MÉT KẾ HOẠCH", f"{met_tong_kh:,.1f} m")

    with tab1:
        st.subheader("1. ĐỊNH MỨC BỌC VỎ")
        b1, b2 = st.columns(2)
        with b1:
            tl_pvc = st.number_input("Vỏ PVC (KG/m)", value=0.013838, format="%.6f")
            tl_4cap = st.number_input("BTP Xoắn tổng (KG/m)", value=0.021084, format="%.6f")
            tl_vach_boc = st.number_input("Nhựa vách (KG/m)", value=0.003951, format="%.6f", key="vach_tab1")
            tl_chi = st.number_input("Chỉ dệt/xé (KG/m)", value=0.000149, format="%.6f")
        with b2:
            hs_boc = st.number_input("Hệ số mét bọc", value=1.0)
            st.metric("Tổng T.L Bọc (KG/mét)", f"{tl_pvc + tl_4cap + tl_vach_boc + tl_chi:.6f}")

    with tab2:
        st.subheader("2. ĐỊNH MỨC XOẮN TỔNG")
        xt1, xt2 = st.columns(2)
        with xt1:
            st.text_input("Mã BTP:", "BTP.XT.068", disabled=True)
            tl_vach_xt = st.number_input("Nhựa vách (KG/m)", value=0.003951, format="%.6f", key="vach_tab2")
        with xt2:
            hs_xt = st.number_input("Hệ số mét xoắn tổng", value=1.005, format="%.3f")

    with tab3:
        st.subheader("3. ĐỊNH MỨC XOẮN ĐÔI")
        data_xd = {
            "Cặp màu": ["XD.140.GRWH", "XD.141.BLWH", "XD.142.ORWH", "XD.143.BRWH"],
            "T.L (KG/mét)": [0.005352, 0.005350, 0.005208, 0.005174],
            "Hệ số mét": [1.035, 1.045, 1.030, 1.025]
        }
        df_xd = st.data_editor(pd.DataFrame(data_xd), num_rows="dynamic", use_container_width=True)

    with tab4:
        st.subheader("4. ĐỊNH MỨC LÕI CHI TIẾT")
        data_loi = {
            "Mã lõi": ["LOI.262.GR", "LOI.259.BL", "LOI.261.OR", "LOI.260.BR"],
            "T.L Đồng (KG/m)": [0.002157, 0.002159, 0.002133, 0.002113],
            "T.L Nhựa (KG/m)": [0.000519, 0.000516, 0.000471, 0.000474],
            "Hệ số mét Lõi": [1.040, 1.050, 1.035, 1.030],
            "Cặp Xoắn": [0, 1, 2, 3]
        }
        df_loi = st.data_editor(pd.DataFrame(data_loi), num_rows="dynamic", use_container_width=True)

    with tab5:
        st.subheader("5. TỔNG HỢP NHU CẦU NVL (KG)")
        met_boc_act = met_tong_kh * hs_boc
        met_xt_act = met_boc_act * hs_xt
        sum_dong, sum_nhua = 0, 0
        for idx, row in df_loi.iterrows():
            m_loi = met_xt_act * df_xd.iloc[int(row["Cặp Xoắn"])]["Hệ số mét"] * row["Hệ số mét Lõi"]
            sum_dong += m_loi * row["T.L Đồng (KG/m)"] * 2
            sum_nhua += m_loi * row["T.L Nhựa (KG/m)"] * 2

        df_nvl = pd.DataFrame({
            "Loại NVL": ["Đồng", "Nhựa Lõi", "Nhựa Vách", "Nhựa Bọc", "Chỉ"],
            "Tổng Cần (KG)": [sum_dong, sum_nhua, met_xt_act * tl_vach_xt, met_boc_act * tl_pvc, met_boc_act * tl_chi]
        })
        st.dataframe(df_nvl.style.format({"Tổng Cần (KG)": "{:,.2f}"}), use_container_width=True)


# ====================================================
# MODULE 2: TÁCH PO & LẬP LỆNH SẢN XUẤT (Tách riêng)
# ====================================================
elif module_choice == "2. Tiếp Nhận PO & Lập Lệnh Sản Xuất":
    st.header("⚙️ MODULE 2: TÁCH PO THÔNG MINH (KẾ THỪA BOM MASTER)")
    
    search_po = st.text_input("🔍 Tìm kiếm Lệnh Sản Xuất / PO:", placeholder="Nhập mã TP hoặc mã Lệnh...")
    st.markdown("---")

    st.subheader("📝 1. Bảng Tiếp Nhận Đơn Hàng (PO)")
    st.caption("Hướng dẫn: Chọn Mã Thành Phẩm từ danh sách. Hệ thống sẽ tự động đối chiếu BOM Master để xuất dữ liệu vật tư.")
    
    default_po = pd.DataFrame({
        "Mã PO": ["PO-2026-01", "PO-2026-02"],
        "Mã Thành Phẩm (TP)": ["SCP.BL.0.55BC", "SCP.WT.0.55BC"],
        "Số Lượng Kế Hoạch (Cuộn)": [900, 396]
    })
    
    edited_po_df = st.data_editor(
        default_po,
        column_config={
            "Mã Thành Phẩm (TP)": st.column_config.SelectboxColumn(
                "Mã Thành Phẩm (TP)",
                help="Chọn Mã Hàng TP đã cài đặt trong BOM Master",
                options=list(BOM_DB["TP"].keys()),
                required=True,
            )
        },
        num_rows="dynamic",
        use_container_width=True
    )

    c1, c2 = st.columns(2)
    with c1: len_cuon = st.number_input("Chiều dài 1 cuộn TP (mét):", value=305.0)
    with c2: ti_le_phong_ngua = st.number_input("Dự phòng hao hụt phế (%):", value=4.0) / 100

    if st.button("🔄 CHẠY TỰ ĐỘNG TÁCH/GOM LỆNH LSX", type="primary"):
        st.success("✅ Đã trích xuất dữ liệu thành công từ BOM Master!")
        
        lsx_boc_list = []
        tong_met_btp_gom = 0
        
        for index, row in edited_po_df.iterrows():
            ma_po = row["Mã PO"]
            ma_tp = row["Mã Thành Phẩm (TP)"]
            so_cuon = row["Số Lượng Kế Hoạch (Cuộn)"]
            
            if pd.isna(ma_tp) or ma_tp not in BOM_DB["TP"]:
                continue
            
            tp_bom = BOM_DB["TP"][ma_tp]
            ma_btp_can_dung = tp_bom["BTP"]
            
            met_tp_chuan = so_cuon * len_cuon
            met_tp_ke_hoach = met_tp_chuan * (1 + ti_le_phong_ngua)
            nhua_boc_can = met_tp_ke_hoach * tp_bom["Nhua_Vo_kg_m"]
            
            lsx_boc_list.append({
                "Nguồn PO": ma_po,
                "Lệnh Bọc Máy Số": f"LSX-TP-{ma_tp.split('.')[1]}",
                "Mã TP Đích": ma_tp,
                "Màu Nhựa Bọc": tp_bom["Mau_Vo"],
                "Mục Tiêu (mét)": met_tp_ke_hoach,
                "Nhu Cầu Nhựa Bọc (KG)": nhua_boc_can
            })
            
            btp_bom = BOM_DB["BTP"][ma_btp_can_dung]
            met_btp_thuc = met_tp_ke_hoach * btp_bom["HeSo_XT"]
            tong_met_btp_gom += met_btp_thuc

        st.subheader("🔵 A. Lệnh Sản Xuất Bán Thành Phẩm (BTP) - Gom Chung")
        btp_code = "BTP.XT.068"
        btp_bom = BOM_DB["BTP"][btp_code]
        
        df_lsx_btp = pd.DataFrame({
            "Mã Lệnh Gom": ["LSX-BTP-TỔNG"],
            "Mã BTP Cần Kéo/Xoắn": [btp_code],
            "Tổng Sản Lượng (m)": [tong_met_btp_gom],
            "Tổng Đồng Cần (KG)": [tong_met_btp_gom * btp_bom["Dong_kg_m"]],
            "Nhựa Lõi Cần (KG)": [tong_met_btp_gom * btp_bom["Nhua_Loi_kg_m"]],
            "Nhựa Vách Cần (KG)": [tong_met_btp_gom * btp_bom["Nhua_Vach_kg_m"]]
        })
        st.dataframe(df_lsx_btp.style.format({
            "Tổng Sản Lượng (m)": "{:,.1f}", "Tổng Đồng Cần (KG)": "{:,.2f}", 
            "Nhựa Lõi Cần (KG)": "{:,.2f}", "Nhựa Vách Cần (KG)": "{:,.2f}"
        }), use_container_width=True)

        st.subheader("🟢 B. Lệnh Sản Xuất Thành Phẩm - Tách Riêng Từng Máy Bọc")
        df_lsx_tp = pd.DataFrame(lsx_boc_list)
        st.dataframe(df_lsx_tp.style.format({
            "Mục Tiêu (mét)": "{:,.1f}", "Nhu Cầu Nhựa Bọc (KG)": "{:,.2f}"
        }), use_container_width=True)


# ====================================================
# MODULE 3: NHẬT KÝ SX, KHO & QUYẾT TOÁN
# ====================================================
elif module_choice == "3. Nhật ký SX, Quản lý Kho & Quyết toán":
    st.header("📦 MODULE 3: ĐIỀU HÀNH XƯỞNG & QUẢN LÝ KHO (BARCODE)")
    st.markdown("---")

    tab_nhap, tab_xuat, tab_ton, tab_qt = st.tabs([
        "📥 1. In Tem & Nhập Kho", 
        "📤 2. Quét Tem Xuất Kho (Sản xuất)", 
        "🏢 3. Tồn Kho Hiện Tại", 
        "📊 4. Quyết Toán PO"
    ])

    with tab_nhap:
        st.subheader("📥 GHI NHẬN SẢN LƯỢNG (TÍNH TỊNH TỪ BÌ TỰ ĐỘNG)")
        
        # Gom tất cả mã hàng từ BOM_DB vào 1 list để chọn
        danh_sach_ma = list(BOM_DB["BTP"].keys()) + list(BOM_DB["TP"].keys()) + list(BOM_DB["LOI"].keys())
        
        c_in1, c_in2 = st.columns([1, 1])
        
        with c_in1:
            loai_sp = st.radio("Loại sản phẩm hoàn thành:", ["Bán Thành Phẩm (BTP)", "Thành Phẩm (TP)"], horizontal=True)
            ma_sp = st.selectbox("Chọn Mã Hàng:", danh_sach_ma)
            so_lot = st.text_input("Số Lô / Ca SX:", value="LOT-2026A")
            
            st.markdown("---")
            st.write("⚖️ **THÔNG SỐ CÂN THỰC TẾ:**")
            trong_luong_tong = st.number_input("Trọng lượng TỔNG (Cả Bì + Lõi/Cáp - kg):", value=75.5)
            trong_luong_bi = st.number_input("Trọng lượng BÌ (Bobbin/Rulo - kg):", value=12.2)
            
            # Tính Tịnh
            trong_luong_tinh = trong_luong_tong - trong_luong_bi
            if trong_luong_tinh < 0: trong_luong_tinh = 0.0
            
            # Tìm hệ số BOM để quy đổi mét
            he_so_kg_m = 0.021084 # Mặc định
            if ma_sp in BOM_DB["BTP"]: he_so_kg_m = BOM_DB["BTP"][ma_sp]["Tong_TL_kg_m"]
            elif ma_sp in BOM_DB["TP"]: he_so_kg_m = BOM_DB["TP"][ma_sp]["Tong_TL_kg_m"]
            elif ma_sp in BOM_DB["LOI"]: he_so_kg_m = BOM_DB["LOI"][ma_sp]["Tong_TL_kg_m"]
            
            so_met_tu_dong = trong_luong_tinh / he_so_kg_m if he_so_kg_m > 0 else 0.0
            
            st.info(f"✅ **Trọng lượng TỊNH:** {trong_luong_tinh:.2f} kg")
            st.success(f"📏 **Số Mét quy đổi tự động (từ BOM):** {so_met_tu_dong:,.1f} mét")

        with c_in2:
            st.write("") # Dóng hàng
            st.write("")
            st.write("")
            if st.button("🖨️ IN TEM & TỰ ĐỘNG NHẬP KHO", type="primary", use_container_width=True):
                ma_qr = f"{ma_sp}_{so_lot}_{datetime.datetime.now().strftime('%H%M%S')}"
                qr_payload = f"QRID:{ma_qr}|CODE:{ma_sp}|LOT:{so_lot}|QTY:{so_met_tu_dong:.1f}M|W:{trong_luong_tinh:.2f}KG"
                
                new_item = pd.DataFrame([{
                    "Mã QR": ma_qr, "Mã Hàng": ma_sp, "Loại": loai_sp, "Số Lô": so_lot, 
                    "Số Mét (m)": round(so_met_tu_dong, 1), "Trọng Lượng (kg)": round(trong_luong_tinh, 2), 
                    "Thời Gian Nhập": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                }])
                st.session_state['inventory'] = pd.concat([st.session_state['inventory'], new_item], ignore_index=True)
                st.session_state['history'].append(f"🟢 NHẬP KHO: {ma_sp} ({so_met_tu_dong:.1f}m - {trong_luong_tinh:.2f}kg) - QR: {ma_qr}")
                
                st.success("✅ Đã ghi nhận sản lượng vào Kho và Tạo tem thành công!")
                
                qr_bytes = create_qr_code(qr_payload)
                st.image(qr_bytes, caption=f"Tem Dán Lên Cuộn - Mã QR: {ma_qr}", width=200)
                st.download_button("⬇️ Tải Tem (In Nhiệt)", data=qr_bytes, file_name=f"QR_{ma_qr}.png", mime="image/png")

    with tab_xuat:
        st.subheader("📤 QUÉT MÃ BTP ĐỂ ĐƯA VÀO CÔNG ĐOẠN TIẾP THEO")
        st.info("Mô phỏng: Công nhân dùng súng bắn mã vạch quét mã QR trên cuộn BTP để xuất vật tư ra chạy máy bọc.")
        
        scan_data = st.text_input("🔫 QUÉT MÃ QR (Đưa con trỏ chuột vào đây và bấm cò súng):", placeholder="VD: BTP.XT.068_LOT-2026A_145023")
        
        if st.button("XÁC NHẬN XUẤT KHO"):
            if scan_data in st.session_state['inventory']["Mã QR"].values:
                st.session_state['inventory'] = st.session_state['inventory'][st.session_state['inventory']["Mã QR"] != scan_data]
                st.session_state['history'].append(f"🔴 XUẤT KHO: Đưa vào SX cuộn BTP có QR: {scan_data}")
                st.success(f"✅ Đã xuất kho thành công cuộn BTP: {scan_data}!")
            else:
                st.error("❌ Mã QR không tồn tại trong kho hoặc đã được xuất!")

    with tab_ton:
        st.subheader("🏢 TÌNH TRẠNG KHO BTP & THÀNH PHẨM HIỆN TẠI")
        search_kho = st.text_input("🔍 Tìm kiếm tồn kho (Nhập Mã hàng, Số lô...):")
        
        df_kho = st.session_state['inventory']
        if search_kho:
            df_kho = df_kho[df_kho.apply(lambda row: row.astype(str).str.contains(search_kho, case=False).any(), axis=1)]
        
        st.dataframe(df_kho, use_container_width=True)
        
        st.markdown("**Lịch sử Nhập/Xuất gần đây:**")
        for log in reversed(st.session_state['history'][-5:]):
            st.text(log)

    with tab_qt:
        st.subheader("📊 QUYẾT TOÁN VẬT TƯ LỆNH SẢN XUẤT / PO")
        search_po_qt = st.selectbox("🔍 Chọn PO cần Quyết toán:", ["PO-01 (SCP.BL)", "PO-02 (SCP.WT)"])
        
        c_qt1, c_qt2, c_qt3 = st.columns(3)
        with c_qt1: tp_m = st.number_input("Mét TP nhập kho:", value=274500.0)
        with c_qt2: dong_xuat = st.number_input("Đồng xuất (kg):", value=4820.0)
        with c_qt3: phe_dong = st.number_input("Phế Đồng thu (kg):", value=85.5)

        if st.button("🔴 CHỐT LỆNH & XUẤT BÁO CÁO"):
            dong_bom = tp_m * 1.005 * 0.017120
            hao_hut_dong_tong = dong_xuat - dong_bom
            hao_hut_dong_vo_hinh = dong_xuat - (tp_m * 0.017120 + phe_dong)

            res_df = pd.DataFrame({
                "NVL": ["Đồng 0.55BC"],
                "Định Mức BOM (kg)": [dong_bom],
                "Thực Xuất (kg)": [dong_xuat],
                "Phế Thu Hồi (kg)": [phe_dong],
                "Hao Hụt Vô Hình (kg)": [hao_hut_dong_vo_hinh],
                "Chênh Lệch So BOM": [hao_hut_dong_tong]
            })
            st.dataframe(res_df.style.format({
                "Định Mức BOM (kg)": "{:,.2f}", "Thực Xuất (kg)": "{:,.2f}", 
                "Phế Thu Hồi (kg)": "{:,.2f}", "Hao Hụt Vô Hình (kg)": "{:,.2f}", 
                "Chênh Lệch So BOM": "{:,.2f}"
            }), use_container_width=True)
