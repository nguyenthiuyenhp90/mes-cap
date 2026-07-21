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
# 2. KHỞI TẠO DỮ LIỆU KHO ẢO (SESSION STATE)
# Để mô phỏng việc Tự động Nhập/Xuất kho khi in/quét QR
# ----------------------------------------------------
if 'inventory' not in st.session_state:
    st.session_state['inventory'] = pd.DataFrame(columns=["Mã QR", "Mã Hàng", "Loại", "Số Lô", "Số Mét (m)", "Trọng Lượng (kg)", "Thời Gian Nhập"])
if 'history' not in st.session_state:
    st.session_state['history'] = []

# Hàm tạo QR
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
st.sidebar.caption("Phiên bản Tích hợp Barcode & Kho Tự Động")

module_choice = st.sidebar.radio(
    "CHỌN MÔ-ĐUN LÀM VIỆC:",
    [
        "1. Quản lý BOM Master & Định mức",
        "2. Tách PO & Lập Lệnh Sản Xuất",
        "3. Nhật ký SX, Quản lý Kho & Quyết toán"
    ]
)

st.sidebar.divider()
st.sidebar.info("💡 **Luồng QR Mới:**\nIn tem BTP/TP -> Auto Nhập Kho.\nQuét tem BTP tại máy bọc -> Auto Xuất Kho.")

# ====================================================
# MODULE 1: QUẢN LÝ BOM MASTER (Đã thêm Tìm kiếm, Giữ nguyên 5 tab)
# ====================================================
if module_choice == "1. Quản lý BOM Master & Định mức":
    st.header("📋 MODULE 1: QUẢN LÝ BOM & ĐỊNH MỨC CHI TIẾT")
    
    # NÚT TÌM KIẾM BOM
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
            tl_vach_boc = st.number_input("Nhựa vách (KG/m)", value=0.003951, format="%.6f")
            tl_chi = st.number_input("Chỉ dệt/xé (KG/m)", value=0.000149, format="%.6f")
        with b2:
            hs_boc = st.number_input("Hệ số mét bọc", value=1.0)
            st.metric("Tổng T.L Bọc (KG/mét)", f"{tl_pvc + tl_4cap + tl_vach_boc + tl_chi:.6f}")

    with tab2:
        st.subheader("2. ĐỊNH MỨC XOẮN TỔNG")
        xt1, xt2 = st.columns(2)
        with xt1:
            st.text_input("Mã BTP:", "BTP.XT.068", disabled=True)
            tl_vach_xt = st.number_input("Nhựa vách (KG/m)", value=0.003951, format="%.6f")
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
        st.info("💡 Lưu ý: Tính năng In Tem QR đã được dời sang Module 3 (Nhật ký Sản xuất) để đồng bộ luồng Nhập/Xuất kho tự động.")
        met_boc_act = met_tong_kh * hs_boc
        met_xt_act = met_boc_act * hs_xt
        sum_dong, sum_nhua = 0, 0
        for idx, row in df_loi.iterrows():
            m_loi = met_xt_act * df_xd.iloc[int(row["Cặp Xoắn"])]["Hệ số mét"] * row["Hệ số mét Lõi"]
            sum_dong += m_loi * row["T.L Đồng (KG/m)"] * 2 # Nhân 2 vì mỗi cặp 2 sợi (tính giản lược)
            sum_nhua += m_loi * row["T.L Nhựa (KG/m)"] * 2

        df_nvl = pd.DataFrame({
            "Loại NVL": ["Đồng", "Nhựa Lõi", "Nhựa Vách", "Nhựa Bọc", "Chỉ"],
            "Tổng Cần (KG)": [sum_dong, sum_nhua, met_xt_act * tl_vach_xt, met_boc_act * tl_pvc, met_boc_act * tl_chi]
        })
        st.dataframe(df_nvl.style.format({"Tổng Cần (KG)": "{:,.2f}"}), use_container_width=True)


# ====================================================
# MODULE 2: TÁCH PO & LẬP LỆNH SẢN XUẤT (Đã thêm Tìm kiếm)
# ====================================================
elif module_choice == "2. Tách PO & Lập Lệnh Sản Xuất":
    st.header("⚙️ MODULE 2: TÁCH PO & PHÁT HÀNH LSX")
    
    # NÚT TÌM KIẾM PO
    search_po = st.text_input("🔍 Tìm kiếm nhanh PO / Lệnh Sản xuất:", placeholder="Nhập số PO (VD: PO-2026-001)...")
    st.markdown("---")

    po_c1, po_c2 = st.columns(2)
    with po_c1:
        po1_pcs = st.number_input("PO-01: Cat6 Xanh Dương - Số cuộn:", value=900)
    with po_c2:
        po2_pcs = st.number_input("PO-02: Cat6 Trắng - Số cuộn:", value=396)

    if st.button("🔄 PHÂN TÍCH TÁCH PO & GOM LỆNH", type="primary"):
        st.success("✅ Đã xử lý gom lệnh xoắn tổng và tách lệnh bọc vỏ thành công!")
        m_btp_gom = ((po1_pcs + po2_pcs) * 305 * 1.04) * 1.005
        
        st.subheader("🔵 A. Lệnh BTP Gom (Kéo & Xoắn)")
        st.dataframe(pd.DataFrame({"Mã LSX": ["LSX-BTP-01"], "Mã BTP": ["BTP.XT.068"], "Tổng Mét": [m_btp_gom]}), use_container_width=True)
        
        st.subheader("🟢 B. Lệnh TP Tách (Bọc Vỏ)")
        st.dataframe(pd.DataFrame({"Mã LSX": ["LSX-TP-BL", "LSX-TP-WT"], "Mã TP": ["SCP.BL", "SCP.WT"], "Mục tiêu (m)": [po1_pcs*305, po2_pcs*305]}), use_container_width=True)


# ====================================================
# MODULE 3: NHẬT KÝ SX, KHO & QUYẾT TOÁN (Giao diện chuẩn MES)
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

    # ------------- TAB 1: IN TEM & TỰ ĐỘNG NHẬP KHO -------------
    with tab_nhap:
        st.subheader("📥 GHI NHẬN SẢN LƯỢNG & TỰ ĐỘNG NHẬP KHO")
        c_in1, c_in2 = st.columns([1, 1])
        
        with c_in1:
            loai_sp = st.radio("Loại sản phẩm hoàn thành:", ["Bán Thành Phẩm (BTP)", "Thành Phẩm (TP)"], horizontal=True)
            ma_sp = st.selectbox("Chọn Mã Hàng:", ["BTP.XT.068", "SCP.BL.0.55BC", "SCP.WT.0.55BC", "Lõi Đồng 0.81"])
            so_lot = st.text_input("Số Lô / Ca SX:", value="LOT-2026A")
            so_met = st.number_input("Chiều dài thực tế (mét):", value=3000.0)
            
            st.write("⚖️ **Phương thức lấy Trọng lượng:**")
            mode_can = st.radio("Chế độ:", ["Tự động (Lấy từ Cân điện tử)", "Nhập tay"], horizontal=True)
            if mode_can == "Nhập tay":
                trong_luong = st.number_input("Nhập trọng lượng (kg):", value=63.5)
            else:
                trong_luong = so_met * 0.021084 # Giả lập hệ thống cân đọc được
                st.info(f"Đang kết nối COM Port... Cân đọc được: **{trong_luong:.2f} kg**")

        with c_in2:
            if st.button("🖨️ IN TEM & TỰ ĐỘNG NHẬP KHO", type="primary", use_container_width=True):
                # Tạo Payload QR (Dữ liệu ngầm)
                ma_qr = f"{ma_sp}_{so_lot}_{datetime.datetime.now().strftime('%H%M%S')}"
                qr_payload = f"QRID:{ma_qr}|CODE:{ma_sp}|LOT:{so_lot}|QTY:{so_met}M|W:{trong_luong}KG"
                
                # Lưu vào Kho Ảo (Session State)
                new_item = pd.DataFrame([{
                    "Mã QR": ma_qr, "Mã Hàng": ma_sp, "Loại": loai_sp, "Số Lô": so_lot, 
                    "Số Mét (m)": so_met, "Trọng Lượng (kg)": trong_luong, 
                    "Thời Gian Nhập": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                }])
                st.session_state['inventory'] = pd.concat([st.session_state['inventory'], new_item], ignore_index=True)
                st.session_state['history'].append(f"🟢 NHẬP KHO: {ma_sp} ({so_met}m - {trong_luong}kg) - QR: {ma_qr}")
                
                st.success("✅ Đã ghi nhận sản lượng vào Kho và Tạo tem thành công!")
                
                # Hiển thị tem QR
                qr_bytes = create_qr_code(qr_payload)
                st.image(qr_bytes, caption=f"Tem Dán Lên Cuộn - Mã QR: {ma_qr}", width=200)
                st.download_button("⬇️ Tải Tem (In Nhiệt)", data=qr_bytes, file_name=f"QR_{ma_qr}.png", mime="image/png")

    # ------------- TAB 2: QUÉT TEM & TỰ ĐỘNG XUẤT KHO -------------
    with tab_xuat:
        st.subheader("📤 QUÉT MÃ BTP ĐỂ ĐƯA VÀO CÔNG ĐOẠN TIẾP THEO")
        st.info("Mô phỏng: Công nhân dùng súng bắn mã vạch quét mã QR trên cuộn BTP để xuất vật tư ra chạy máy bọc.")
        
        # Nhập tay hoặc giả lập súng bắn barcode (Súng barcode thực chất là bàn phím tự động nhập và Enter)
        scan_data = st.text_input("🔫 QUÉT MÃ QR (Đưa con trỏ chuột vào đây và bấm cò súng):", placeholder="VD: BTP.XT.068_LOT-2026A_145023")
        
        if st.button("XÁC NHẬN XUẤT KHO"):
            if scan_data in st.session_state['inventory']["Mã QR"].values:
                # Trừ đi khỏi kho ảo
                st.session_state['inventory'] = st.session_state['inventory'][st.session_state['inventory']["Mã QR"] != scan_data]
                st.session_state['history'].append(f"🔴 XUẤT KHO: Đưa vào SX cuộn BTP có QR: {scan_data}")
                st.success(f"✅ Đã xuất kho thành công cuộn BTP: {scan_data}!")
            else:
                st.error("❌ Mã QR không tồn tại trong kho hoặc đã được xuất!")

    # ------------- TAB 3: TỒN KHO HIỆN TẠI -------------
    with tab_ton:
        st.subheader("🏢 TÌNH TRẠNG KHO BTP & THÀNH PHẨM HIỆN TẠI")
        search_kho = st.text_input("🔍 Tìm kiếm tồn kho (Nhập Mã hàng, Số lô...):")
        
        df_kho = st.session_state['inventory']
        if search_kho:
            df_kho = df_kho[df_kho.apply(lambda row: row.astype(str).str.contains(search_kho, case=False).any(), axis=1)]
        
        st.dataframe(df_kho, use_container_width=True)
        
        st.markdown("**Lịch sử Nhập/Xuất gần đây:**")
        for log in reversed(st.session_state['history'][-5:]): # Show 5 newest logs
            st.text(log)

    # ------------- TAB 4: QUYẾT TOÁN PO -------------
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
