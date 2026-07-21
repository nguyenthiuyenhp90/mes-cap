import streamlit as st
import pandas as pd
import sqlite3
import qrcode
from io import BytesIO
from PIL import Image
import datetime

# --- 1. CẤU HÌNH TRANG & KẾT NỐI DATABASE ---
st.set_page_config(page_title="Hệ Thống MES Quản Lý Sản Xuất Dây Cáp", layout="wide")

def get_connection():
    conn = sqlite3.connect("mes_cable_factory.db", check_same_thread=False)
    return conn

conn = get_connection()
cursor = conn.cursor()

# Khởi tạo các bảng dữ liệu nếu chưa có
def init_db():
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS bom_master (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tp_code TEXT,
        stage TEXT,
        btp_code TEXT,
        kg_per_m REAL,
        shrinkage REAL,
        scrap_std REAL,
        nvl_main TEXT
    )''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS po_orders (
        po_code TEXT PRIMARY KEY,
        tp_code TEXT,
        plan_meters REAL,
        created_date TEXT
    )''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS production_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        log_date TEXT,
        po_code TEXT,
        entry_type TEXT,
        btp_code TEXT,
        weight_kg REAL,
        calc_meters REAL,
        nvl_used_kg REAL,
        scrap_kg REAL,
        error_code TEXT
    )''')
    conn.commit()

    # Thêm dữ liệu BOM mẫu nếu bảng BOM trống
    cursor.execute("SELECT COUNT(*) FROM bom_master")
    if cursor.fetchone()[0] == 0:
        sample_bom = [
            ("TP-CAT6-GR", "1. Kéo Lõi", "BTP-LOI-081", 0.0207, 1.025, 0.015, "Đồng + HDPE"),
            ("TP-CAT6-GR", "2. Xoắn Đôi", "BTP-XD-CAT6", 0.0450, 1.005, 0.005, "BTP-LOI-081"),
            ("TP-CAT6-GR", "3. Bọc Vỏ", "TP-CAT6-GR", 0.0150, 1.000, 0.010, "Nhựa PVC vỏ"),
            ("TP-CAT5E-UTP", "1. Kéo Lõi", "BTP-LOI-078", 0.0185, 1.020, 0.015, "Đồng + PE"),
            ("TP-CAT5E-UTP", "2. Xoắn Đôi", "BTP-XD-CAT5", 0.0380, 1.005, 0.005, "BTP-LOI-078"),
            ("TP-CAT5E-UTP", "3. Bọc Vỏ", "TP-CAT5E-UTP", 0.0135, 1.000, 0.010, "Nhựa PVC vỏ")
        ]
        cursor.executemany('''
        INSERT INTO bom_master (tp_code, stage, btp_code, kg_per_m, shrinkage, scrap_std, nvl_main)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', sample_bom)
        conn.commit()

init_db()

st.title("🏭 HỆ THỐNG MES QUẢN LÝ SẢN XUẤT DÂY CÁP - V5")
st.markdown("---")

# --- 2. TẠO TABS CHỨC NĂNG ---
tab1, tab2, tab3, tab4 = st.tabs([
    "📋 1. Quản Lý BOM Master", 
    "📦 2. Tạo PO & Bung BOM", 
    "🏷️ 3. Nhật Ký SX & In Tem QR (Cân Auto Mét)", 
    "📊 4. Dashboard & Cảnh Báo Tồn Máy"
])

# ==========================================
# TAB 1: QUẢN LÝ BOM MASTER
# ==========================================
with tab1:
    st.header("Danh Mục Định Mức BOM Chuẩn Cho Từng Thành Phẩm")
    df_bom = pd.read_sql_query("SELECT tp_code, stage, btp_code, kg_per_m, shrinkage, scrap_std, nvl_main FROM bom_master", conn)
    st.dataframe(df_bom, use_container_width=True)
    
    with st.expander("➕ Thêm / Cập nhật BOM cho mã Thành Phẩm mới"):
        col1, col2, col3 = st.columns(3)
        with col1:
            new_tp = st.text_input("Mã Thành Phẩm (TP)", "TP-CAT6-NEW")
            new_stage = st.selectbox("Công đoạn", ["1. Kéo Lõi", "2. Xoắn Đôi", "3. Bọc Vỏ"])
            new_btp = st.text_input("Mã BTP đầu ra", "BTP-LOI-081")
        with col2:
            new_kg_m = st.number_input("Trọng lượng chuẩn (kg/m)", value=0.0207, format="%.4f")
            new_shrink = st.number_input("Hệ số co ngót/xoắn", value=1.025, format="%.3f")
        with col3:
            new_scrap = st.number_input("Tỷ lệ phế tiêu chuẩn (%)", value=1.5) / 100
            new_nvl = st.text_input("Vật tư chính tiêu hao", "Đồng 7/0.150")
            
        if st.button("Lưu Quy Cách BOM"):
            cursor.execute('''
            INSERT INTO bom_master (tp_code, stage, btp_code, kg_per_m, shrinkage, scrap_std, nvl_main)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (new_tp, new_stage, new_btp, new_kg_m, new_shrink, new_scrap, new_nvl))
            conn.commit()
            st.success(f"Đã thêm thành công BOM cho {new_tp}!")
            st.rerun()

# ==========================================
# TAB 2: TẠO PO & BUNG BOM TỰ ĐỘNG
# ==========================================
with tab2:
    st.header("Tạo Đơn Hàng PO & Tự Động Tính Nhu Cầu BTP / Vật Tư")
    
    # Lấy danh sách TP từ BOM Master
    tp_list = cursor.execute("SELECT DISTINCT tp_code FROM bom_master").fetchall()
    tp_options = [t[0] for t in tp_list]
    
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        po_code_input = st.text_input("Mã Đơn Hàng PO", "PO-202607-01")
    with col_b:
        selected_tp = st.selectbox("Chọn Mã Thành Phẩm (TP)", tp_options)
    with col_c:
        plan_meters_input = st.number_input("Số lượng Kế hoạch (Mét)", value=100000, step=5000)
        
    if st.button("🚀 Tạo PO & Bung BOM Tự Động"):
        # Lưu PO vào database
        cursor.execute("INSERT OR REPLACE INTO po_orders VALUES (?, ?, ?, ?)",
                       (po_code_input, selected_tp, plan_meters_input, str(datetime.date.today())))
        conn.commit()
        st.success(f"Đã tạo PO {po_code_input} thành công!")
        
    st.subheader(f"📄 Chi Tiết Mẫu Bung BOM Cho PO: {po_code_input}")
    
    # Bung BOM tự động
    df_tp_bom = pd.read_sql_query("SELECT * FROM bom_master WHERE tp_code = ?", conn, params=(selected_tp,))
    if not df_tp_bom.empty:
        bom_calc = []
        for idx, row in df_tp_bom.iterrows():
            target_m = plan_meters_input * row["shrinkage"] * (1 + row["scrap_std"])
            target_kg = target_m * row["kg_per_m"]
            bom_calc.append({
                "Công Đoạn": row["stage"],
                "Mã BTP Đầu Ra": row["btp_code"],
                "Hệ Số Co Ngót": row["shrinkage"],
                "Mục Tiêu Mét (BTP)": round(target_m, 0),
                "Mục Tiêu KG (BTP)": round(target_kg, 2),
                "Vật Tư Chính Cần Cấp": row["nvl_main"]
            })
        st.table(pd.DataFrame(bom_calc))

# ==========================================
# TAB 3: NHẬT KÝ SẢN XUẤT & QUY ĐỔI KÝ -> MÉT TỰ ĐỘNG
# ==========================================
with tab3:
    st.header("Ghi Nhận Sản Lượng Ca Running & In Tem QR")
    
    po_list = [p[0] for p in cursor.execute("SELECT po_code FROM po_orders").fetchall()]
    
    if not po_list:
        st.warning("Vui lòng tạo ít nhất 1 PO ở Tab 2 trước khi nhập nhật ký!")
    else:
        col_log1, col_log2 = st.columns(2)
        
        with col_log1:
            sel_po = st.selectbox("Chọn Mã PO", po_list, key="log_po")
            # Tìm TP của PO này
            tp_of_po = cursor.execute("SELECT tp_code FROM po_orders WHERE po_code = ?", (sel_po,)).fetchone()[0]
            
            # Tìm danh sách BTP của TP này
            btp_rows = cursor.execute("SELECT btp_code, kg_per_m FROM bom_master WHERE tp_code = ?", (tp_of_po,)).fetchall()
            btp_dict = {b[0]: b[1] for b in btp_rows}
            
            sel_btp = st.selectbox("Chọn BTP Sản Xuất", list(btp_dict.keys()))
            kg_per_m_std = btp_dict[sel_btp]
            
            st.info(f"💡 Trọng lượng BOM tiêu chuẩn: **{kg_per_m_std} kg/m**")
            
            entry_type = st.radio("Phân loại nhập", ["SX mới (Tính hao hụt vào PO)", "Nhập điều chuyển (BTP tồn đơn cũ)"])
            
            # --- CÂN TỰ ĐỘNG HOẶC NHẬP TAY KG ---
            input_kg = st.number_input("⚖️ Nhập Số KG Thực Tế (Cân Bàn)", value=414.0, step=1.0)
            
            # --- TỰ ĐỘNG NHẢY SỐ MÉT DỰA TRÊN BOM ---
            auto_calc_meters = round(input_kg / kg_per_m_std) if kg_per_m_std > 0 else 0
            
            st.metric(label="📏 Số Mét Tự Động Quy Đổi (Từ BOM)", value=f"{auto_calc_meters:,} m")
            
            nvl_used = st.number_input("NVL Thực Dùng (kg)", value=input_kg + 5.0)
            scrap_kg = st.number_input("Phế Liệu Cân Được (kg)", value=2.0)
            error_code = st.selectbox("Lý Do Phế", ["- Không lỗi", "K - Kẹt nhựa đùn", "D - Đứt dây đồng", "C - Cắt đầu đuôi cuộn", "S - Lệch màu nhựa"])

        with col_log2:
            st.subheader("🏷️ Xem Trước Tem Mã QR BTP")
            qr_data = f"PO:{sel_po}|BTP:{sel_btp}|KG:{input_kg}|M:{auto_calc_meters}|DATE:{datetime.date.today()}"
            
            # Tạo mã QR Image
            qr = qrcode.QRCode(version=1, box_size=6, border=2)
            qr.add_data(qr_data)
            qr.make(fit=True)
            img_qr = qr.make_image(fill_color="black", back_color="white")
            
            buf = BytesIO()
            img_qr.save(buf, format="PNG")
            st.image(buf.getvalue(), caption=f"Mã QR hóa: {qr_data}", width=200)
            
            if st.button("💾 Lưu Nhật Ký & In Tem QR"):
                cursor.execute('''
                INSERT INTO production_logs (log_date, po_code, entry_type, btp_code, weight_kg, calc_meters, nvl_used_kg, scrap_kg, error_code)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (str(datetime.date.today()), sel_po, entry_type, sel_btp, input_kg, auto_calc_meters, nvl_used, scrap_kg, error_code))
                conn.commit()
                st.success(f"Đã ghi nhận {auto_calc_meters:,} mét cho {sel_btp} vào PO {sel_po}!")

# ==========================================
# TAB 4: DASHBOARD & CẢNH BÁO TỒN DỞ DANG (FLOOR STOCK)
# ==========================================
with tab4:
    st.header("Báo Cáo Tiến Độ PO & Kiểm Soát Tồn Dở Dang Tại Máy")
    
    po_dash_list = [p[0] for p in cursor.execute("SELECT po_code FROM po_orders").fetchall()]
    if po_dash_list:
        sel_dash_po = st.selectbox("Chọn PO Cần Giám Sát", po_dash_list)
        
        # Lấy thông tin PO
        po_info = cursor.execute("SELECT tp_code, plan_meters FROM po_orders WHERE po_code = ?", (sel_dash_po,)).fetchone()
        tp_code_po, plan_m = po_info[0], po_info[1]
        
        st.subheader(f"📌 Tiến Độ Sản Xuất PO: {sel_dash_po} (Thành phẩm: {tp_code_po} - KH: {plan_m:,} m)")
        
        # Báo cáo theo từng công đoạn
        df_logs = pd.read_sql_query("SELECT * FROM production_logs WHERE po_code = ?", conn, params=(sel_dash_po,))
        df_bom_tp = pd.read_sql_query("SELECT stage, btp_code, shrinkage, scrap_std FROM bom_master WHERE tp_code = ?", conn, params=(tp_code_po,))
        
        dash_summary = []
        for _, b_row in df_bom_tp.iterrows():
            btp = b_row["btp_code"]
            target_m = plan_m * b_row["shrinkage"] * (1 + b_row["scrap_std"])
            
            # Tổng đã làm thực tế
            actual_m = df_logs[df_logs["btp_code"] == btp]["calc_meters"].sum() if not df_logs.empty else 0
            actual_kg = df_logs[df_logs["btp_code"] == btp]["weight_kg"].sum() if not df_logs.empty else 0
            
            remain_m = target_m - actual_m
            pct = round((actual_m / target_m) * 100, 1) if target_m > 0 else 0
            
            dash_summary.append({
                "Công Đoạn": b_row["stage"],
                "Mã BTP": btp,
                "Mục Tiêu (M)": round(target_m, 0),
                "Đã Đạt (M)": actual_m,
                "Còn Lại (M)": round(max(0, remain_m), 0),
                "Đã Đạt (KG)": actual_kg,
                "Tiến Độ (%)": f"{pct}%"
            })
            
        st.table(pd.DataFrame(dash_summary))
        
        st.subheader("⚠️ Kiểm Soát Thất Thoát & Hao Hụt Vô Hình Tại Phân Xưởng")
        if not df_logs.empty:
            total_nvl = df_logs["nvl_used_kg"].sum()
            total_btp_kg = df_logs["weight_kg"].sum()
            total_scrap_kg = df_logs["scrap_kg"].sum()
            unseen_scrap = total_nvl - total_btp_kg - total_scrap_kg
            
            col_m1, col_m2, col_m3, col_m4 = st.columns(4)
            col_m1.metric("Tổng NVL Xuất Chạy (kg)", f"{total_nvl:,.1f}")
            col_m2.metric("Tổng BTP Đạt (kg)", f"{total_btp_kg:,.1f}")
            col_m3.metric("Tổng Phế Cân Được (kg)", f"{total_scrap_kg:,.1f}")
            col_m4.metric("Hao Hụt Vô Hình (kg)", f"{unseen_scrap:,.1f}", delta_color="inverse")
        else:
            st.info("Chưa có nhật ký sản xuất cho PO này.")
