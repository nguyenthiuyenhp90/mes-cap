import streamlit as st
import pandas as pd
import qrcode
from io import BytesIO
from PIL import Image

# ----------------------------------------------------
# CONFIG TRANG STREAMLIT
# ----------------------------------------------------
st.set_page_config(
    page_title="Hệ Thống MES - Quản Lý Sản Xuất Cáp Mạng",
    page_icon="🔌",
    layout="wide"
)

# ----------------------------------------------------
# HÀM BỔ TRỢ: TẠO MÃ QR CODE CHO BTP & TP
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
# SIDEBAR NGUYÊN TẮC VẬN HÀNH & CHỌN MODULE
# ----------------------------------------------------
st.sidebar.title("🏭 MES CÁP MẠNG v2.0")
st.sidebar.caption("Hệ thống Điều hành Sản xuất & Quyết toán Vật tư")

module_choice = st.sidebar.radio(
    "CHỌN MÔ-ĐUN CHỨC NĂNG:",
    [
        "1. Quản lý BOM Multi-Level & Tem QR",
        "2. Tách PO & Lập Lệnh Sản Xuất (LSX)",
        "3. Nhật ký & Quyết toán / Chốt PO"
    ]
)

st.sidebar.divider()
st.sidebar.info("📌 **Quy tắc MES chuẩn:**\n- 1 Thành phẩm = 1 BOM riêng.\n- Các PO chung công đoạn đầu sẽ GOM tạo 1 LSX BTP xoắn tổng.")

# ====================================================
# MODULE 1: QUẢN LÝ BOM MULTI-LEVEL & TEM MÃ QR
# ====================================================
if module_choice == "1. Quản lý BOM Multi-Level & Tem QR":
    st.header("📦 MODULE 1: DẠNH MỤC BOM MULTI-LEVEL & TEM QR")
    st.markdown("---")

    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.subheader("1. Danh mục Bán Thành Phẩm (BTP) Dùng Chung")
        btp_data = {
            "Mã BTP": ["BTP.XT.068"],
            "Tên BTP": ["Cáp xoắn tổng 4 cặp + Vách chữ thập (Chưa bọc vỏ)"],
            "Định mức Đồng (KG/m)": [0.017120],
            "Định mức Nhựa Lõi (KG/m)": [0.003964],
            "Định mức Nhựa Vách (KG/m)": [0.003951],
            "Hệ số mét Xoắn": [1.005]
        }
        st.dataframe(pd.DataFrame(btp_data), use_container_width=True)

        st.subheader("2. Danh mục Thành Phẩm (1 TP = 1 BOM)")
        tp_data = {
            "Mã TP": ["SCP.BL.0.55BC", "SCP.WT.0.55BC"],
            "Tên Thành Phẩm": ["Cat6 UTP Xanh Dương", "Cat6 UTP Trắng"],
            "Mã BTP Cấp Vào": ["BTP.XT.068", "BTP.XT.068"],
            "Loại Nhựa Vỏ": ["PVC Xanh Dương", "PVC Trắng"],
            "Định mức Vỏ (KG/m)": [0.013838, 0.013838],
            "Định mức Chỉ (KG/m)": [0.000149, 0.000149]
        }
        st.dataframe(pd.DataFrame(tp_data), use_container_width=True)

    with col_right:
        st.subheader("🖨️ In Tem QR Bán Thành Phẩm")
        btp_code_select = st.selectbox("Chọn Mã BTP tạo Tem:", ["BTP.XT.068", "SCP.BL.0.55BC", "SCP.WT.0.55BC"])
        lot_no = st.text_input("Nhập Số Lô / Ca chạy máy:", value="LOT-20260722-01")
        len_m = st.number_input("Chiều dài cuộn (mét):", value=3050.0)

        qr_payload = f"CODE:{btp_code_select}|LOT:{lot_no}|QTY:{len_m}M"
        qr_img_bytes = create_qr_code(qr_payload)

        st.image(qr_img_bytes, caption=f"Tem QR: {btp_code_select}", width=180)
        st.download_button(
            label="⬇️ Tải Tem QR (PNG)",
            data=qr_img_bytes,
            file_name=f"QR_{btp_code_select}_{lot_no}.png",
            mime="image/png"
        )

# ====================================================
# MODULE 2: TÁCH PO & LẬP LỆNH SẢN XUẤT (LSX)
# ====================================================
elif module_choice == "2. Tách PO & Lập Lệnh Sản Xuất (LSX)":
    st.header("⚙️ MODULE 2: TÁCH PO & TẠO LỆNH SẢN XUẤT (LSX)")
    st.markdown("---")

    st.subheader("1. Tiếp Nhận Đơn Hàng (PO) Từ Kinh Doanh")
    c1, c2 = st.columns(2)
    with c1:
        po1_pcs = st.number_input("PO-01: Cat6 Xanh Dương (SCP.BL) - Số cuộn:", value=900)
    with c2:
        po2_pcs = st.number_input("PO-02: Cat6 Trắng (SCP.WT) - Số cuộn:", value=396)

    pcs_m = 305.0
    buffer_rate = 0.04 # Dự phòng phế bọc 4%

    met_po1 = po1_pcs * pcs_m * (1 + buffer_rate)
    met_po2 = po2_pcs * pcs_m * (1 + buffer_rate)

    if st.button("🔄 PHÂN TÍCH TÁCH PO & GOM LỆNH BTP", type="primary"):
        st.success("✅ Đã tính toán và tách Lệnh sản xuất theo từng xưởng thành công!")

        # A. LSX BTP GOM CHUNG
        st.subheader("🔵 A. Lệnh Sản Xuất BTP (Gom Chung Cho Xưởng Kéo & Xoắn)")
        met_btp_tong = (met_po1 + met_po2) * 1.005

        df_lsx_btp = pd.DataFrame({
            "Mã LSX BTP": ["LSX-BTP-2026-01"],
            "Mã BTP Cần Chạy": ["BTP.XT.068"],
            "Nguồn Gom PO": ["PO-01 + PO-02"],
            "Tổng Mét BTP Chạy (m)": [met_btp_tong],
            "Nhu cầu Đồng (kg)": [met_btp_tong * 0.017120],
            "Nhu cầu Nhựa Lõi (kg)": [met_btp_tong * 0.003964],
            "Nhu cầu Nhựa Vách (kg)": [met_btp_tong * 0.003951]
        })
        st.dataframe(df_lsx_btp.style.format({
            "Tổng Mét BTP Chạy (m)": "{:,.1f}",
            "Nhu cầu Đồng (kg)": "{:,.2f}",
            "Nhu cầu Nhựa Lõi (kg)": "{:,.2f}",
            "Nhu cầu Nhựa Vách (kg)": "{:,.2f}"
        }), use_container_width=True)

        # B. LSX THÀNH PHẨM TÁCH RIÊNG
        st.subheader("🟢 B. Lệnh Sản Xuất Thành Phẩm (Tách Riêng Cho Xưởng Bọc Vỏ)")
        df_lsx_tp = pd.DataFrame({
            "Mã LSX Bọc": ["LSX-TP-BL-01", "LSX-TP-WT-02"],
            "Thuộc PO": ["PO-01", "PO-02"],
            "Mã TP": ["SCP.BL.0.55BC", "SCP.WT.0.55BC"],
            "Màu Vỏ": ["Xanh Dương", "Trắng"],
            "Mục tiêu Mét Bọc (m)": [met_po1, met_po2],
            "BTP Cần Xuất Dùng (m)": [met_po1, met_po2],
            "Nhu cầu Nhựa PVC (kg)": [met_po1 * 0.013838, met_po2 * 0.013838]
        })
        st.dataframe(df_lsx_tp.style.format({
            "Mục tiêu Mét Bọc (m)": "{:,.1f}",
            "BTP Cần Xuất Dùng (m)": "{:,.1f}",
            "Nhu cầu Nhựa PVC (kg)": "{:,.2f}"
        }), use_container_width=True)

# ====================================================
# MODULE 3: QUYẾT TOÁN & CHỐT PO
# ====================================================
elif module_choice == "3. Nhật ký & Quyết toán / Chốt PO":
    st.header("🔒 MODULE 3: BÁO CÁO QUYẾT TOÁN & CHỐT PO")
    st.markdown("---")

    po_select = st.selectbox("Chọn PO cần chốt quyết toán:", ["PO-01 (SCP.BL - Xanh Dương)", "PO-02 (SCP.WT - Trắng)"])

    st.subheader("1. Nhập Số Liệu Báo Cáo Thực Tế Từ Nhà Xưởng")
    ca1, ca2, ca3 = st.columns(3)
    with ca1:
        tp_m = st.number_input("Thành phẩm nhập kho đạt QA (m):", value=274500.0)
    with ca2:
        dong_xuat = st.number_input("Đồng thực xuất dùng (kg):", value=4820.0)
        pvc_xuat = st.number_input("Nhựa PVC thực xuất dùng (kg):", value=3880.0)
    with ca3:
        phe_dong = st.number_input("Phế Đồng cân thu hồi (kg):", value=85.5)
        phe_pvc = st.number_input("Phế PVC cân thu hồi (kg):", value=62.0)

    st.divider()

    if st.button("🔴 BẤM CHỐT PO & XUẤT BÁO CÁO", type="primary"):
        # Tính toán
        dong_bom = tp_m * 1.005 * 0.017120
        dong_tp_chua = tp_m * 0.017120
        hao_hut_dong_tong = dong_xuat - dong_bom
        hao_hut_dong_vo_hinh = dong_xuat - (dong_tp_chua + phe_dong)

        pvc_bom = tp_m * 0.013838
        hao_hut_pvc_tong = pvc_xuat - pvc_bom
        hao_hut_pvc_vo_hinh = pvc_xuat - (pvc_bom + phe_pvc)

        st.subheader(f"📊 Kết Quả Quyết Toán Nguyên Vật Liệu - {po_select}")

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

        st.warning("💡 **Giải thích chỉ số:**\n- **Hao hụt vô hình:** Số kg vật tư bị mất đi không đong đếm được (cháy nhựa, sai số cân, dôi hao chiều dài).\n- **Chênh lệch so BOM:** Mức độ tiêu hao vượt hoặc hụt so với chuẩn phòng kỹ thuật đặt ra.")
