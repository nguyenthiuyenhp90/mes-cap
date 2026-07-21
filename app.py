import streamlit as st
import pandas as pd
import qrcode
from io import BytesIO
from PIL import Image

# ----------------------------------------------------
# 1. CẤU HÌNH TRANG WEB STREAMLIT
# ----------------------------------------------------
st.set_page_config(
    page_title="Hệ Thống MES - Quản Lý Sản Xuất Cáp Mạng",
    page_icon="⚡",
    layout="wide"
)

# ----------------------------------------------------
# 2. HÀM TẠO MÃ QR CODE CHO TEM BTP / TP
# ----------------------------------------------------
def create_qr_code(data_string):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=6,
        border=2,
    )
    qr.add_data(data_string)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

# ----------------------------------------------------
# 3. SIDEBAR ĐIỀU HƯỚNG MODULE
# ----------------------------------------------------
st.sidebar.title("🏭 HỆ THỐNG MES CÁP MẠNG")
st.sidebar.caption("Chuyển đổi số & Quản lý Sản xuất Chi tiết")

module_choice = st.sidebar.radio(
    "CHỌN MÔ-ĐUN LÀM VIỆC:",
    [
        "1. Quản lý BOM Master & Định mức Chi tiết",
        "2. Tách PO & Lập Lệnh Sản Xuất (LSX)",
        "3. Nhật ký & Quyết toán / Chốt PO"
    ]
)

st.sidebar.divider()
st.sidebar.info(
    "💡 **Nguyên tắc hệ thống:**\n"
    "- 1 Thành phẩm (TP) = 1 BOM chuẩn.\n"
    "- Nhiều PO chung công đoạn đầu sẽ GOM tạo LSX BTP xoắn tổng.\n"
    "- Công thức: Mét Lõi = Mét TP × HS Bọc × HS XT × HS XD × HS Lõi"
)

# ====================================================
# MODULE 1: QUẢN LÝ BOM MASTER & ĐỊNH MỨC CHI TIẾT
# ====================================================
if module_choice == "1. Quản lý BOM Master & Định mức Chi tiết":
    st.header("📋 MODULE 1: BOM CHUẨN — ĐỊNH MỨC CHI TIẾT THEO MÉT / MÃ HÀNG")
    st.caption("Nguồn: Định mức kỹ thuật cung cấp cho mã 0.55BC (Đơn vị tính: KG/mét, trừ khi có ghi chú khác)")
    st.markdown("---")

    # Tạo 5 Tab giao diện chi tiết như bảng gốc
    tab0, tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "0. Đơn Hàng & Quy Đổi Mét",
        "1. Định Mức Bọc Vỏ",
        "2. Định Mức Xoắn Tổng",
        "3. Định Mức Xoắn Đôi",
        "4. Chi Tiết 8 Lõi Dây",
        "5. Tổng Hợp NVL & In Tem QR"
    ])

    # ---------------- TAB 0 ----------------
    with tab0:
        st.subheader("0. THÔNG TIN ĐƠN HÀNG & QUY ĐỔI ĐƠN VỊ")
        c1, c2, c3 = st.columns(3)
        with c1:
            code_bl = st.text_input("Đơn hàng mã SCP.BL", "SCP.BL.0.55BC")
            pcs_bl = st.number_input("Số lượng SCP.BL (PCS)", value=900)
            code_wt = st.text_input("Đơn hàng mã SCP.WT", "SCP.WT.0.55BC")
            pcs_wt = st.number_input("Số lượng SCP.WT (PCS)", value=396)
        with c2:
            pcs_to_m = st.number_input("Quy đổi 1 PCS = (Mét)", value=305.0)
            pct_du_phong = st.number_input("Hao hụt dự phòng (%)", value=4.0) / 100
        with c3:
            met_bl = pcs_bl * pcs_to_m
            met_wt = pcs_wt * pcs_to_m
            met_chua_hh = met_bl + met_wt
            met_hh = met_chua_hh * pct_du_phong
            met_tong_kh = met_chua_hh + met_hh

            st.metric("Mét mã SCP.BL", f"{met_bl:,.1f} m")
            st.metric("Mét mã SCP.WT", f"{met_wt:,.1f} m")
            st.metric("Mét hao hụt dự phòng", f"{met_hh:,.1f} m")
            st.metric("🎯 TỔNG SỐ MÉT TP KẾ HOẠCH", f"{met_tong_kh:,.1f} m")

    # ---------------- TAB 1 ----------------
    with tab1:
        st.subheader("1. ĐỊNH MỨC BỌC (Tính cho 1 mét Thành phẩm)")
        b1, b2 = st.columns(2)
        with b1:
            tl_pvc = st.number_input("Vỏ PVC (KG/mét)", value=0.013838, format="%.6f")
            tl_4cap = st.number_input("4 cặp màu - BTP Xoắn tổng (KG/mét)", value=0.021084, format="%.6f")
            tl_vach_boc = st.number_input("Nhựa vách (KG/mét)", value=0.003951, format="%.6f")
            tl_chi = st.number_input("Chỉ dệt/xé (KG/mét)", value=0.000149, format="%.6f")
        with b2:
            od_vo = st.number_input("Đường kính ngoài OD (mm)", value=6.1)
            hs_boc = st.number_input("Hệ số mét bọc quy đổi", value=1.0)
            tl_tong_boc = tl_pvc + tl_4cap + tl_vach_boc + tl_chi
            st.metric("Tổng T.L Bọc (KG/mét)", f"{tl_tong_boc:.6f}")

    # ---------------- TAB 2 ----------------
    with tab2:
        st.subheader("2. ĐỊNH MỨC XOẮN TỔNG (BTP.XT.068)")
        xt1, xt2 = st.columns(2)
        with xt1:
            st.text_input("Mã BTP Xoắn Tổng:", "BTP.XT.068", disabled=True)
            tl_4cap_xt = st.number_input("4 cặp màu (KG/m)", value=0.021084, format="%.6f", key="xt_4cap")
            tl_vach_xt = st.number_input("Nhựa vách chữ thập (KG/m)", value=0.003951, format="%.6f", key="xt_vach")
        with xt2:
            hs_xt = st.number_input("Hệ số mét xoắn tổng", value=1.005, format="%.3f")
            tl_tong_xt = tl_4cap_xt + tl_vach_xt
            st.metric("Tổng T.L Xoắn Tổng (KG/m)", f"{tl_tong_xt:.6f}")

    # ---------------- TAB 3 ----------------
    with tab3:
        st.subheader("3. ĐỊNH MỨC XOẮN ĐÔI (Theo từng cặp màu)")
        data_xd = {
            "Cặp màu": ["XD.140.GRWH (Xanh lá - Trắng)", "XD.141.BLWH (Xanh dương - Trắng)", "XD.142.ORWH (Cam - Trắng)", "XD.143.BRWH (Nâu - Trắng)"],
            "T.L (KG/mét)": [0.005352, 0.005350, 0.005208, 0.005174],
            "Tỉ lệ (%)": [25.4, 25.4, 24.7, 24.5],
            "Hệ số mét": [1.035, 1.045, 1.030, 1.025]
        }
        df_xd = st.data_editor(pd.DataFrame(data_xd), num_rows="dynamic", use_container_width=True)

    # ---------------- TAB 4 ----------------
    with tab4:
        st.subheader("4. ĐỊNH MỨC LÕI CHI TIẾT (8 Màu Lõi)")
        data_loi = {
            "Mã màu lõi": ["LOI.262.GR", "LOI.263.KẺ XANH LÁ", "LOI.259.BL", "LOI.264.KẺ XANH DƯƠNG", "LOI.261.OR", "LOI.265.KẺ CAM", "LOI.260.BR", "LOI.266.KẺ NÂU"],
            "T.L Đồng (KG/m)": [0.002157, 0.002157, 0.002159, 0.002159, 0.002133, 0.002133, 0.002113, 0.002113],
            "T.L Nhựa (KG/m)": [0.000519, 0.000519, 0.000516, 0.000516, 0.000471, 0.000471, 0.000474, 0.000474],
            "OD (mm)": [0.977, 0.977, 0.967, 0.967, 0.950, 0.950, 0.955, 0.955],
            "Hệ số mét Lõi": [1.040, 1.040, 1.050, 1.050, 1.035, 1.035, 1.030, 1.030],
            "Thuộc Cặp Xoắn": [0, 0, 1, 1, 2, 2, 3, 3] # Chỉ số ứng với 4 cặp ở Tab Xoắn đôi
        }
        df_loi = st.data_editor(pd.DataFrame(data_loi), num_rows="dynamic", use_container_width=True)

    # ---------------- TAB 5 ----------------
    with tab5:
        st.subheader("5. TỔNG HỢP NGUYÊN VẬT LIỆU CHO ĐƠN HÀNG KẾ HOẠCH")
        
        # Tính toán chi tiết
        met_boc_act = met_tong_kh * hs_boc
        met_xt_act = met_boc_act * hs_xt
        
        # Lặp tính toán cho từng lõi
        met_loi_list, kg_dong_list, kg_nhua_loi_list = [], [], []
        for idx, row in df_loi.iterrows():
            cap_idx = int(row["Thuộc Cặp Xoắn"])
            hs_xd = df_xd.iloc[cap_idx]["Hệ số mét"]
            
            # Công thức tích lũy hệ số mét
            m_loi = met_xt_act * hs_xd * row["Hệ số mét Lõi"]
            kg_d = m_loi * row["T.L Đồng (KG/m)"]
            kg_n = m_loi * row["T.L Nhựa (KG/m)"]
            
            met_loi_list.append(m_loi)
            kg_dong_list.append(kg_d)
            kg_nhua_loi_list.append(kg_n)

        df_loi_calc = df_loi.copy()
        df_loi_calc["Sản lượng Mét Lõi (m)"] = met_loi_list
        df_loi_calc["Tổng Đồng (KG)"] = kg_dong_list
        df_loi_calc["Tổng Nhựa Lõi (KG)"] = kg_nhua_loi_list

        sum_dong = sum(kg_dong_list)
        sum_nhua_loi = sum(kg_nhua_loi_list)
        sum_nhua_vach = met_xt_act * tl_vach_xt
        sum_pvc = met_boc_act * tl_pvc
        sum_chi = met_boc_act * tl_chi
        sum_total_nvl = sum_dong + sum_nhua_loi + sum_nhua_vach + sum_pvc + sum_chi

        st.markdown("#### A. Bảng Nhu Cầu NVL Quy Ra KG Theo Đơn Hàng")
        df_nvl_sum = pd.DataFrame({
            "Loại Nguyên Vật Liệu": ["Đồng 0.55BC", "Nhựa Lõi 1101", "Nhựa Vách 221 WT", "Nhựa Bọc (PVC)", "Chỉ Dệt/Xé"],
            "Tổng KG (Dự phòng)": [sum_dong, sum_nhua_loi, sum_nhua_vach, sum_pvc, sum_chi],
            "Tỷ Lệ Thành Phần (%)": [
                (sum_dong/sum_total_nvl)*100,
                (sum_nhua_loi/sum_total_nvl)*100,
                (sum_nhua_vach/sum_total_nvl)*100,
                (sum_pvc/sum_total_nvl)*100,
                (sum_chi/sum_total_nvl)*100
            ]
        })
        st.dataframe(df_nvl_sum.style.format({
            "Tổng KG (Dự phòng)": "{:,.2f}",
            "Tỷ Lệ Thành Phần (%)": "{:.2f}%"
        }), use_container_width=True)

        st.success(f"⚖️ **TỔNG KHỐI LƯỢNG NVL NGUYÊN TẮC CẦN XUẤT KHO:** **{sum_total_nvl:,.2f} KG**")

        st.divider()
        st.markdown("#### B. In Tem QR Quản Lý Bán Thành Phẩm (BTP)")
        qr_col1, qr_col2 = st.columns([2, 1])
        with qr_col1:
            qr_btp_code = st.selectbox("Chọn Mã BTP/TP cần tạo mã QR:", ["BTP.XT.068", "SCP.BL.0.55BC", "SCP.WT.0.55BC"])
            qr_lot = st.text_input("Mã Lô sản xuất (Lot No):", "LOT-20260330-01")
            qr_qty = st.number_input("Số mét cuộn BTP:", value=3000.0)
        with qr_col2:
            payload = f"CODE:{qr_btp_code}|LOT:{qr_lot}|QTY:{qr_qty}M"
            qr_bytes = create_qr_code(payload)
            st.image(qr_bytes, caption=f"Tem QR: {qr_btp_code}", width=160)
            st.download_button("⬇️ Tải Tem QR Code (PNG)", data=qr_bytes, file_name=f"QR_{qr_btp_code}.png", mime="image/png")

# ====================================================
# MODULE 2: TÁCH PO & LẬP LỆNH SẢN XUẤT (LSX)
# ====================================================
elif module_choice == "2. Tách PO & Lập Lệnh Sản Xuất (LSX)":
    st.header("⚙️ MODULE 2: TÁCH PO & LẬP LỆNH SẢN XUẤT (LSX)")
    st.markdown("---")

    st.subheader("1. Danh Sách Đơn Hàng (PO) Tiếp Nhận")
    po_c1, po_c2 = st.columns(2)
    with po_c1:
        po1_pcs = st.number_input("PO-01: Cat6 Xanh Dương (SCP.BL) - Số cuộn (PCS):", value=900)
    with po_c2:
        po2_pcs = st.number_input("PO-02: Cat6 Trắng (SCP.WT) - Số cuộn (PCS):", value=396)

    pcs_m = 305.0
    buffer = 0.04
    m_po1 = po1_pcs * pcs_m * (1 + buffer)
    m_po2 = po2_pcs * pcs_m * (1 + buffer)

    if st.button("🔄 PHÂN TÍCH TÁCH PO & PHÁT HÀNH LSX", type="primary"):
        st.divider()
        st.success("✅ Đã tách và gom Lệnh Sản Xuất theo đúng công đoạn xưởng!")

        st.subheader("🔵 A. Lệnh Sản Xuất BTP Gom (Cho Xưởng Kéo & Xoắn)")
        m_btp_gom = (m_po1 + m_po2) * 1.005 # Nhân hệ số xoắn tổng

        df_lsx_btp = pd.DataFrame({
            "Mã LSX BTP": ["LSX-BTP-2026-01"],
            "Mã BTP Chạy": ["BTP.XT.068"],
            "Tên BTP": ["Cáp xoắn tổng 4 cặp + Vách chữ thập"],
            "Gom Từ Các PO": ["PO-01 (BL) + PO-02 (WT)"],
            "Tổng Mét BTP Chạy (m)": [m_btp_gom],
            "Nhu cầu Đồng (kg)": [m_btp_gom * 0.017120],
            "Nhu cầu Nhựa Lõi (kg)": [m_btp_gom * 0.003964],
            "Nhu cầu Nhựa Vách (kg)": [m_btp_gom * 0.003951]
        })
        st.dataframe(df_lsx_btp.style.format({
            "Tổng Mét BTP Chạy (m)": "{:,.1f}",
            "Nhu cầu Đồng (kg)": "{:,.2f}",
            "Nhu cầu Nhựa Lõi (kg)": "{:,.2f}",
            "Nhu cầu Nhựa Vách (kg)": "{:,.2f}"
        }), use_container_width=True)

        st.subheader("🟢 B. Lệnh Sản Xuất Thành Phẩm Tách (Cho Xưởng Bọc Vỏ)")
        df_lsx_tp = pd.DataFrame({
            "Mã LSX Bọc": ["LSX-TP-BL-01", "LSX-TP-WT-02"],
            "Thuộc PO": ["PO-01", "PO-02"],
            "Mã Thành Phẩm": ["SCP.BL.0.55BC", "SCP.WT.0.55BC"],
            "Loại Vỏ Bọc": ["PVC Xanh Dương", "PVC Trắng"],
            "Mục tiêu Mét Bọc (m)": [m_po1, m_po2],
            "BTP Xoắn Cấp Vào (m)": [m_po1, m_po2],
            "Nhu cầu Nhựa PVC (kg)": [m_po1 * 0.013838, m_po2 * 0.013838]
        })
        st.dataframe(df_lsx_tp.style.format({
            "Mục tiêu Mét Bọc (m)": "{:,.1f}",
            "BTP Xoắn Cấp Vào (m)": "{:,.1f}",
            "Nhu cầu Nhựa PVC (kg)": "{:,.2f}"
        }), use_container_width=True)

# ====================================================
# MODULE 3: QUYẾT TOÁN & CHỐT PO
# ====================================================
elif module_choice == "3. Nhật ký & Quyết toán / Chốt PO":
    st.header("🔒 MODULE 3: BÁO CÁO QUYẾT TOÁN & CHỐT PO")
    st.markdown("---")

    po_id = st.selectbox("Chọn PO cần chốt quyết toán:", ["PO-01 (SCP.BL - Xanh Dương)", "PO-02 (SCP.WT - Trắng)"])

    st.subheader("1. Nhập Số Liệu Báo Cáo Báo Về Từ Nhà Xưởng")
    sc1, sc2, sc3 = st.columns(3)
    with sc1:
        tp_m = st.number_input("Thành phẩm đạt QA nhập kho (m):", value=274500.0)
    with sc2:
        dong_xuat = st.number_input("Đồng thực xuất dùng (kg):", value=4820.0)
        pvc_xuat = st.number_input("Nhựa PVC thực xuất dùng (kg):", value=3880.0)
    with sc3:
        phe_dong = st.number_input("Phế Đồng cân thu hồi (kg):", value=85.5)
        phe_pvc = st.number_input("Phế PVC cân thu hồi (kg):", value=62.0)

    st.divider()

    if st.button("🔴 BẤM CHỐT PO & XUẤT BÁO CÁO", type="primary"):
        # Tính toán đối soát
        dong_bom = tp_m * 1.005 * 0.017120
        dong_tp_chua = tp_m * 0.017120
        hao_hut_dong_tong = dong_xuat - dong_bom
        hao_hut_dong_vo_hinh = dong_xuat - (dong_tp_chua + phe_dong)

        pvc_bom = tp_m * 0.013838
        hao_hut_pvc_tong = pvc_xuat - pvc_bom
        hao_hut_pvc_vo_hinh = pvc_xuat - (pvc_bom + phe_pvc)

        st.subheader(f"📊 Báo Cáo Quyết Toán Vật Tư Chi Tiết - {po_id}")

        res_df = pd.DataFrame({
            "Loại NVL": ["Đồng 0.55BC", "Nhựa Vỏ PVC"],
            "Định Mức BOM (kg)": [dong_bom, pvc_bom],
            "Thực Xuất Kho (kg)": [dong_xuat, pvc_xuat],
            "Phế Cân Thu Hồi (kg)": [phe_dong, phe_pvc],
            "Hao Hụt Vô Hình / Mất Mát (kg)": [hao_hut_dong_vo_hinh, hao_hut_pvc_vo_hinh],
            "Chênh Lệch So BOM (kg)": [hao_hut_dong_tong, hao_hut_pvc_tong],
            "Tỷ Lệ Hao Hụt Total (%)": [(hao_hut_dong_tong/dong_xuat)*100, (hao_hut_pvc_tong/pvc_xuat)*100]
        })

        st.dataframe(res_df.style.format({
            "Định Mức BOM (kg)": "{:,.2f}",
            "Thực Xuất Kho (kg)": "{:,.2f}",
            "Phế Cân Thu Hồi (kg)": "{:,.2f}",
            "Hao Hụt Vô Hình / Mất Mát (kg)": "{:,.2f}",
            "Chênh Lệch So BOM (kg)": "{:,.2f}",
            "Tỷ Lệ Hao Hụt Total (%)": "{:.2f}%"
        }), use_container_width=True)

        st.warning(
            "💡 **Giải thích chỉ số:**\n"
            "- **Hao hụt vô hình:** Lượng NVL bị mất đi không thu hồi được dạng phế (cháy nhựa, sai số cân, dôi hao chiều dài kéo lõi).\n"
            "- **Chênh lệch so BOM:** Mức độ vượt/hụt so với định mức phòng kỹ thuật."
        )
