import streamlit as st
import pandas as pd
import sqlite3
import qrcode
from io import BytesIO
import datetime

# --- 1. CẤU HÌNH TRANG & GIAO DIỆN ---
st.set_page_config(page_title="MES CÁP ĐIỆN - HỆ THỐNG QUẢN LÝ SẢN XUẤT", layout="wide", page_icon="🏭")

# Custom CSS cho giao diện chuyên nghiệp
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] { background-color: #ffffff; border-radius: 6px; padding: 10px 20px; font-weight: bold; }
    .stTabs [aria-selected="true"] { background-color: #0d6efd !important; color: white !important; }
    </style>
""", unsafe_allow_html=True)

def get_connection():
    return sqlite3.connect("mes_cable_v6.db", check_same_thread=False)

conn = get_connection()
cursor = conn.cursor()

# --- 2. KHỞI TẠO CƠ SỞ DỮ LIỆU ---
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
        created_date TEXT,
        status TEXT
    )''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS production_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        log_date TEXT,
        shift_name TEXT,
        machine_code TEXT,
        worker_name TEXT,
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

    # Dữ liệu BOM mẫu chuẩn
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

# --- 3. TIÊU ĐỀ ỨNG DỤNG ---
col_head1, col_head2 = st.columns([4, 1])
with col_head1:
    st.title("🏭 MES CÁP ĐIỆN - HỆ THỐNG DIỀU HÀNH SẢN XUẤT")
    st.caption("Phiên bản V6 Chuyên Nghiệp | Quản lý BOM, PO, Nhật ký Ca, Tồn Kho BTP & Báo cáo Excel")
with col_head2:
    st.image("https://img.icons8.com/color/96/factory.png", width=70)

st.markdown("---")

# --- 4. CÁC PHÂN HỆ CHÍNH ---
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📋 1. Quản Lý BOM Master", 
    "📦 2. Đơn Hàng PO & Bung BOM", 
    "🏷️ 3. Nhật Ký Ca & Mã QR (Auto Mét)", 
    "📊 4. Dashboard Tiến Độ & Floor Stock",
    "📁 5. Báo Cáo & Xuất File Excel"
])

# ==========================================
# TAB 1: QUẢN LÝ BOM MASTER
# ==========================================
with tab1:
    st.subheader("📋 Định Mức Vật Tư & Quy Cách Cáp (BOM Master)")
    df_bom = pd.read_sql_query("SELECT tp_code AS [Mã TP], stage AS [Công Đoạn], btp_code AS [Mã BTP], kg_per_m AS [Kg/Mét Chuẩn], shrinkage AS [Hệ Số Co Ngót], scrap_std*100 AS [Tỷ Lệ Phế %], nvl_main AS [Vật Tư Chính] FROM bom_master", conn)
    st.dataframe(df_bom, use_container_width=True)
    
    with st.expander("➕ Thêm Mã Thành Phẩm / Công Đoạn BOM Mới"):
        col1, col2, col3 = st.columns(3)
        with col1:
            new_tp = st.text_input("Mã Thành Phẩm (TP)", "TP-CAT6A-SHIELD")
            new_stage = st.selectbox("Công đoạn", ["1. Kéo Lõi", "2. Xoắn Đôi", "3. Bọc Vỏ"])
            new_btp = st.text_input("Mã BTP đầu ra", "BTP-LOI-085")
        with col2:
            new_kg_m = st.number_input("Trọng lượng chuẩn (kg/m)", value=0.0220, format="%.4f")
            new_shrink = st.number_input("Hệ số co ngót/xoắn", value=1.030, format="%.3f")
        with col3:
            new_scrap = st.number_input("Phế tiêu chuẩn (%)", value=1.5) / 100
            new_nvl = st.text_input("Vật tư chính tiêu hao", "Đồng 0.85mm + HDPE")
            
        if st.button("💾 Lưu BOM Sản Phẩm"):
            cursor.execute('''
            INSERT INTO bom_master (tp_code, stage, btp_code, kg_per_m, shrinkage, scrap_std, nvl_main)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (new_tp, new_stage, new_btp, new_kg_m, new_shrink, new_scrap, new_nvl))
            conn.commit()
            st.success(f"Đã lưu thành công quy cách BOM cho {new_tp}!")
            st.rerun()

# ==========================================
# TAB 2: ĐƠN HÀNG PO & BUNG BOM
# ==========================================
with tab2:
    st.subheader("📦 Quản Lý Lệnh Sản Xuất (PO) & Nhu Cầu Vật Tư")
    
    tp_options = [t[0] for t in cursor.execute("SELECT DISTINCT tp_code FROM bom_master").fetchall()]
    
    c1, c2, c3 = st.columns(3)
    with c1:
        po_code_input = st.text_input("Mã Đơn Hàng PO", f"PO-{datetime.date.today().strftime('%Y%m')}-01")
    with c2:
        selected_tp = st.selectbox("Chọn Mã Thành Phẩm", tp_options)
    with c3:
        plan_meters_input = st.number_input("Số Lượng Kế Hoạch (Mét)", value=100000, step=10000)
        
    if st.button("🚀 Khởi Tạo PO & Tính Nhu Cầu NVL"):
        cursor.execute("INSERT OR REPLACE INTO po_orders VALUES (?, ?, ?, ?, ?)",
                       (po_code_input, selected_tp, plan_meters_input, str(datetime.date.today()), "Đang Sản Xuất"))
        conn.commit()
        st.success(f"Đã lập đơn hàng {po_code_input} thành công!")
        
    st.markdown("---")
    st.write(f"### 📄 Chi Tiết Kế Hoạch BTP & Cấp NVL Cho PO: **{po_code_input}**")
    
    df_tp_bom = pd.read_sql_query("SELECT * FROM bom_master WHERE tp_code = ?", conn, params=(selected_tp,))
    if not df_tp_bom.empty:
        bom_calc = []
        for _, row in df_tp_bom.iterrows():
            target_m = plan_meters_input * row["shrinkage"] * (1 + row["scrap_std"])
            target_kg = target_m * row["kg_per_m"]
            bom_calc.append({
                "Công Đoạn": row["stage"],
                "Mã BTP Cần Chạy": row["btp_code"],
                "Hệ Số Co Ngót": row["shrinkage"],
                "KH Mét BTP": f"{round(target_m, 0):,} m",
                "KH Trọng Lượng BTP": f"{round(target_kg, 1):,} kg",
                "NVL Cần Cấp Cho Kho": row["nvl_main"]
            })
        st.table(pd.DataFrame(bom_calc))

# ==========================================
# TAB 3: NHẬT KÝ CA & IN TEM QR AUTO MÉT
# ==========================================
with tab3:
    st.subheader("📝 Nhập Nhật Ký Ca Chạy & In Tem Mã QR BTP")
    
    po_list = [p[0] for p in cursor.execute("SELECT po_code FROM po_orders WHERE status = 'Đang Sản Xuất'").fetchall()]
    
    if not po_list:
        st.warning("Chưa có PO nào ở trạng thái 'Đang Sản Xuất'. Vui lòng tạo PO ở Tab 2!")
    else:
        col_f1, col_f2 = st.columns([3, 2])
        
        with col_f1:
            st.write("##### 1. Thông Tin Ca & Máy Sản Xuất")
            cc1, cc2, cc3 = st.columns(3)
            with cc1:
                log_shift = st.selectbox("Chọn Ca", ["Ca 1 (Day)", "Ca 2 (Night)", "Ca 3"])
            with cc2:
                log_machine = st.selectbox("Mã Máy Running", ["MÁY KÉO-01", "MÁY KÉO-02", "MÁY XOẮN-01", "MÁY XOẮN-02", "MÁY BỌC VỎ-01"])
            with cc3:
                log_worker = st.text_input("Tên Công Nhân / Trưởng Ca", "Nguyễn Văn A")
                
            st.write("##### 2. Chi Tiết Sản Lượng Thực Tế")
            sel_po = st.selectbox("Chọn Mã PO", po_list)
            tp_of_po = cursor.execute("SELECT tp_code FROM po_orders WHERE po_code = ?", (sel_po,)).fetchone()[0]
            
            btp_rows = cursor.execute("SELECT btp_code, kg_per_m FROM bom_master WHERE tp_code = ?", (tp_of_po,)).fetchall()
            btp_dict = {b[0]: b[1] for b in btp_rows}
            
            sel_btp = st.selectbox("Mã BTP / Thành Phẩm Cân Được", list(btp_dict.keys()))
            kg_per_m_std = btp_dict[sel_btp]
            
            entry_type = st.radio("Phân loại nguồn BTP", ["Sản xuất mới (Tính tiêu hao vào PO)", "Nhập điều chuyển (Tồn cuộn/bin đơn cũ)"], horizontal=True)
            
            st.info(f"⚖️ Định mức BOM chuẩn của **{sel_btp}** là: **{kg_per_m_std} kg/m**")
            
            # CÂN TỰ ĐỘNG HOẶC NHẬP TAY KG
            input_kg = st.number_input("Mức Cân Trọng Lượng BTP (KG)", value=414.0, step=1.0)
            
            # TỰ ĐỘNG nhảy mét từ BOM
            auto_meters = round(input_kg / kg_per_m_std) if kg_per_m_std > 0 else 0
            
            st.markdown(f"### 📏 Số Mét Tự Động Quy Đổi: <span style='color:#0d6efd;'>{auto_meters:,} Mét</span>", unsafe_allow_html=True)
            
            c_nvl1, c_nvl2 = st.columns(2)
            with c_nvl1:
                nvl_used = st.number_input("NVL / BTP Cấp Thực Dùng (kg)", value=input_kg + 3.0)
            with c_nvl2:
                scrap_kg = st.number_input("Phế Cân Được (kg)", value=1.5)
                
            error_code = st.selectbox("Mã Lý Do Phế Liệu", ["- Không lỗi", "K - Kẹt nhựa/nghẹt đùn", "D - Đứt dây đồng", "C - Cắt đầu đuôi công nghệ", "S - Lệch màu nhựa", "L - Lệch đường kính OD"])

        with col_f2:
            st.write("##### 🏷️ Khởi Tạo Tem Mã QR Dán Bin BTP")
            qr_text = f"PO:{sel_po}|BTP:{sel_btp}|KG:{input_kg}|M:{auto_meters}|MÁY:{log_machine}|DATE:{datetime.date.today()}"
            
            qr = qrcode.QRCode(version=1, box_size=8, border=2)
            qr.add_data(qr_text)
            qr.make(fit=True)
            img_qr = qr.make_image(fill_color="#000000", back_color="#ffffff")
            
            buf = BytesIO()
            img_qr.save(buf, format="PNG")
            st.image(buf.getvalue(), caption=f"Tem QR mã hóa: {qr_text}", width=220)
            
            if st.button("💾 Bấm Lưu Nhật Ký & Xã Tem QR", use_container_width=True):
                cursor.execute('''
                INSERT INTO production_logs (log_date, shift_name, machine_code, worker_name, po_code, entry_type, btp_code, weight_kg, calc_meters, nvl_used_kg, scrap_kg, error_code)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (str(datetime.date.today()), log_shift, log_machine, log_worker, sel_po, entry_type, sel_btp, input_kg, auto_meters, nvl_used, scrap_kg, error_code))
                conn.commit()
                st.balloons()
                st.success(f"Đã lưu nhật ký ca: {auto_meters:,}m ({input_kg}kg) BTP thành công!")

# ==========================================
# TAB 4: DASHBOARD TIẾN ĐỘ & FLOOR STOCK
# ==========================================
with tab4:
    st.subheader("📊 Báo Cáo Tiến Độ PO Real-Time & Tồn Dở Dang Tại Máy")
    
    all_pos = [p[0] for p in cursor.execute("SELECT po_code FROM po_orders").fetchall()]
    if all_pos:
        dash_po = st.selectbox("Chọn Đơn Hàng PO Cần Giám Sát Tiến Độ", all_pos)
        
        po_meta = cursor.execute("SELECT tp_code, plan_meters, status FROM po_orders WHERE po_code = ?", (dash_po,)).fetchone()
        tp_code_po, plan_m, po_status = po_meta[0], po_meta[1], po_meta[2]
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Kế Hoạch PO (Thành Phẩm)", f"{plan_m:,} m")
        m2.metric("Mã Quy Cách", tp_code_po)
        m3.metric("Trạng Thái PO", po_status)
        
        st.markdown("---")
        st.write("##### 📌 Tiến Độ Hoàn Thành Theo Từng Công Đoạn (So Với BOM Kế Hoạch)")
        
        df_logs_po = pd.read_sql_query("SELECT * FROM production_logs WHERE po_code = ?", conn, params=(dash_po,))
        df_bom_po = pd.read_sql_query("SELECT stage, btp_code, shrinkage, scrap_std FROM bom_master WHERE tp_code = ?", conn, params=(tp_code_po,))
        
        dash_table = []
        for _, b_row in df_bom_po.iterrows():
            btp = b_row["btp_code"]
            target_m = plan_m * b_row["shrinkage"] * (1 + b_row["scrap_std"])
            
            actual_m = df_logs_po[df_logs_po["btp_code"] == btp]["calc_meters"].sum() if not df_logs_po.empty else 0
            actual_kg = df_logs_po[df_logs_po["btp_code"] == btp]["weight_kg"].sum() if not df_logs_po.empty else 0
            
            rem_m = target_m - actual_m
            pct = round((actual_m / target_m) * 100, 1) if target_m > 0 else 0
            
            dash_table.append({
                "Công Đoạn": b_row["stage"],
                "Mã BTP": btp,
                "KH Mục Tiêu (Mét)": f"{round(target_m, 0):,}",
                "Thực Tế Đạt (Mét)": f"{actual_m:,}",
                "Còn Lại (Mét)": f"{round(max(0, rem_m), 0):,}",
                "Tổng Sản Lượng (KG)": f"{actual_kg:,.1f}",
                "% Tiến Độ": f"{pct}%"
            })
            
        st.table(pd.DataFrame(dash_table))
        
        st.write("##### ⚠️ Đối Soát Thất Thoát Vật Tư Dở Dang (Floor Stock Audit)")
        if not df_logs_po.empty:
            tot_nvl = df_logs_po["nvl_used_kg"].sum()
            tot_btp_kg = df_logs_po["weight_kg"].sum()
            tot_scrap = df_logs_po["scrap_kg"].sum()
            unseen_scrap = tot_nvl - tot_btp_kg - tot_scrap
            
            cm1, cm2, cm3, cm4 = st.columns(4)
            cm1.metric("Tổng Vật Tư Xuất Chạy", f"{tot_nvl:,.1f} kg")
            cm2.metric("Tổng BTP/TP Đạt Cân Được", f"{tot_btp_kg:,.1f} kg")
            cm3.metric("Tổng Phế Cân Được", f"{tot_scrap:,.1f} kg")
            cm4.metric("Hao Hụt Vô Hình (Chênh lệch)", f"{unseen_scrap:,.1f} kg", delta_color="inverse")
        else:
            st.info("Chưa có dữ liệu nhật ký ca nào được nhập cho PO này.")

# ==========================================
# TAB 5: BÁO CÁO & XUẤT FILE EXCEL
# ==========================================
with tab5:
    st.subheader("📁 Xuất Báo Cáo Nhật Ký Sản Xuất Ra File Excel")
    
    df_all_logs = pd.read_sql_query('''
    SELECT 
        log_date AS [Ngày SX],
        shift_name AS [Ca Chạy],
        machine_code AS [Mã Máy],
        worker_name AS [Công Nhân],
        po_code AS [Mã PO],
        entry_type AS [Nguồn BTP],
        btp_code AS [Mã BTP],
        weight_kg AS [Sản Lượng KG],
        calc_meters AS [Quy Đổi Mét],
        nvl_used_kg AS [NVL Thực Dùng KG],
        scrap_kg AS [Phế Cân Được KG],
        error_code AS [Mã Lỗi Phế]
    FROM production_logs ORDER BY id DESC
    ''', conn)
    
    st.dataframe(df_all_logs, use_container_width=True)
    
    # Nút bấm xuất file Excel
    if not df_all_logs.empty:
        output_excel = BytesIO()
        with pd.ExcelWriter(output_excel, engine='openpyxl') as writer:
            df_all_logs.to_excel(writer, index=False, sheet_name='Nhat_Ky_San_Xuat')
        
        st.download_button(
            label="📥 Tải Báo Cáo Nhật Ký SX dạng File Excel (.xlsx)",
            data=output_excel.getvalue(),
            file_name=f"Bao_Cao_MES_Cable_{datetime.date.today()}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
