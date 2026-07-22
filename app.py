# -*- coding: utf-8 -*-
"""
app.py
------
Trang chủ của App MES - Quản lý Sản xuất Cáp.
Chức năng: Đăng nhập đơn giản (username/password lưu trong SQLite) +
hiển thị thông tin tổng quan hệ thống.

Chạy app bằng lệnh:
    streamlit run app.py
"""

import streamlit as st
from db import init_db, kiem_tra_dang_nhap, lay_danh_sach_po, lay_nhat_ky

st.set_page_config(
    page_title="MES - Quản lý Sản xuất Cáp",
    page_icon="🏭",
    layout="wide",
)

# Khởi tạo database (tạo bảng nếu chưa có) - chạy 1 lần khi app khởi động
init_db()


def man_hinh_dang_nhap():
    """Hiển thị form đăng nhập, chặn không cho vào app nếu chưa đăng nhập."""
    st.title("🏭 MES - Hệ thống Quản lý Sản xuất Cáp")
    st.caption("Vui lòng đăng nhập để tiếp tục")

    with st.form("form_dang_nhap"):
        col1, col2 = st.columns(2)
        with col1:
            username = st.text_input("Tên đăng nhập")
        with col2:
            mat_khau = st.text_input("Mật khẩu", type="password")
        submitted = st.form_submit_button("Đăng nhập", use_container_width=True)

    if submitted:
        try:
            thong_tin = kiem_tra_dang_nhap(username.strip(), mat_khau)
            if thong_tin:
                st.session_state["dang_nhap"] = True
                st.session_state["user_info"] = thong_tin
                st.success(f"Xin chào {thong_tin['ho_ten'] or thong_tin['username']}!")
                st.rerun()
            else:
                st.error("❌ Sai tên đăng nhập hoặc mật khẩu.")
        except Exception as e:
            st.error(f"Có lỗi xảy ra khi đăng nhập: {e}")

    st.info(
        "🔑 Tài khoản mặc định: **admin** / **admin123** "
        "(nên đổi mật khẩu sau khi đăng nhập lần đầu — xem mục "
        "*Quản trị tài khoản* bên dưới sau khi đăng nhập)."
    )


def man_hinh_trang_chu():
    """Trang chủ sau khi đăng nhập thành công - hiển thị tổng quan nhanh."""
    user = st.session_state["user_info"]

    col_title, col_logout = st.columns([5, 1])
    with col_title:
        st.title("🏭 MES - Hệ thống Quản lý Sản xuất Cáp")
        st.caption(f"Xin chào **{user['ho_ten'] or user['username']}** ({user['vai_tro']})")
    with col_logout:
        st.write("")
        if st.button("Đăng xuất", use_container_width=True):
            st.session_state["dang_nhap"] = False
            st.session_state.pop("user_info", None)
            st.rerun()

    st.divider()
    st.markdown(
        """
        ### 👋 Chào mừng đến với hệ thống MES

        Sử dụng menu bên trái để điều hướng:
        - **📥 Nhập liệu**: nhập nhanh nhật ký sản xuất theo PO/công đoạn, hoặc upload file Excel.
        - **📊 Dashboard**: theo dõi sản lượng, tỷ lệ phế, tiến độ công đoạn theo từng PO.
        - **🔍 Tra cứu & Báo cáo**: lọc dữ liệu và xuất báo cáo Excel, hoặc chốt PO.
        """
    )

    st.divider()
    st.subheader("📌 Tổng quan nhanh")

    try:
        df_po = lay_danh_sach_po()
        df_log = lay_nhat_ky()

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Tổng số PO", len(df_po))
        c2.metric(
            "PO đang chạy",
            int((df_po["trang_thai"] == "Đang chạy").sum()) if not df_po.empty else 0,
        )
        c3.metric("Tổng số dòng nhật ký", len(df_log))
        if not df_log.empty:
            tong_phe_kg = df_log.loc[df_log["loai_gd"] == "Phế liệu", "so_luong_kg"].sum()
            c4.metric("Tổng phế (kg)", f"{tong_phe_kg:,.1f}")
        else:
            c4.metric("Tổng phế (kg)", "0")

        if df_po.empty:
            st.warning(
                "⚠️ Chưa có PO nào trong hệ thống. Vào trang **📥 Nhập liệu** để "
                "khai báo PO mới trước khi nhập nhật ký sản xuất."
            )
    except Exception as e:
        st.error(f"Không thể tải dữ liệu tổng quan: {e}")


# ============================================================
# ĐIỀU HƯỚNG CHÍNH
# ============================================================
if "dang_nhap" not in st.session_state:
    st.session_state["dang_nhap"] = False

if not st.session_state["dang_nhap"]:
    man_hinh_dang_nhap()
else:
    man_hinh_trang_chu()
