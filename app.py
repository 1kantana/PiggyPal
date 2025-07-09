import re
from collections import defaultdict
from datetime import datetime
import streamlit as st
import pandas as pd
from io import BytesIO
import streamlit as st

PASSWORD = st.secrets["APP_PASSWORD"]

def login():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        st.title("🔐 เข้าสู่ระบบ")

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("### กรุณากรอกรหัสผ่าน")
            password = st.text_input("รหัสผ่าน", type="password", label_visibility="collapsed")
            if st.button("เข้าสู่ระบบ"):
                if password == PASSWORD:
                    st.session_state.logged_in = True
                    st.success("เข้าสู่ระบบสำเร็จ ✅")
                else:
                    st.error("รหัสผ่านไม่ถูกต้อง ❌")
        st.stop()  # หยุดไม่ให้ไปต่อ ถ้ายังไม่ login

login()

st.title("บันทึกรายจ่าย Happy 💰😊")

data = st.text_area("Enter your data (format: '7 Jul: rice-meal 60 coffee-meal 50')", height=200)

YEAR = 2025

def is_weekend(date_str):
    dt = datetime.strptime(f"{date_str} {YEAR}", "%d %b %Y")
    return dt.weekday() >= 5

CATEGORY_EMOJI = {
    "meal": "🍚",
    "shopping": "🛍️",
    "misc": "📦",
    "snack": "🍪",
    "health": "💊",
}

# 👇 วางโค้ดใหม่ตรงนี้ แทน if st.button("Calculate") เดิมทั้งหมด
if st.button("Calculate"):
    totals_weekday = defaultdict(float)
    totals_weekend = defaultdict(float)
    all_rows = []

    for line in data.strip().split('\n'):
        date_part = line.split(':')[0].strip()
        weekend = is_weekend(date_part)
        day_type = "Weekend" if weekend else "Weekday"
        items = re.findall(r'(\S+?)(?:-(\w+))?\s+(\d+(?:\.\d+)?)', line)
        for item, category, amount in items:
            amount = float(amount)
            if not category:
                category = "misc"
            if weekend:
                totals_weekend[category] += amount
            else:
                totals_weekday[category] += amount
            all_rows.append({
                "Date": f"{date_part} {YEAR}",
                "Item": item,
                "Category": category,
                "Amount": amount,
                "Type": day_type
            })

    # 👉 แสดงผลรวมบนหน้าจอ
    st.subheader("Summary Weekday:")
    for category, amt in totals_weekday.items():
        emoji = CATEGORY_EMOJI.get(category, "❓")
        st.write(f"{emoji} **{category.capitalize()}**: {round(amt, 2)}")

    st.subheader("Summary Weekend:")
    for category, amt in totals_weekend.items():
        emoji = CATEGORY_EMOJI.get(category, "❓")
        st.write(f"{emoji} **{category.capitalize()}**: {round(amt, 2)}")

    grand_total = sum(totals_weekday.values()) + sum(totals_weekend.values())
    st.subheader(f"💵 Grand Total: {round(grand_total, 2)}")

    # 👉 สร้างไฟล์ Excel
    df = pd.DataFrame(all_rows)
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Expenses')
        summary_df = pd.concat([
            pd.DataFrame(totals_weekday.items(), columns=['Category', 'Weekday Total']),
            pd.DataFrame(totals_weekend.items(), columns=['Category', 'Weekend Total'])
        ], axis=1)
        summary_df.to_excel(writer, index=False, sheet_name='Summary')
    output.seek(0)

    # 👉 ปุ่มดาวน์โหลด
    st.download_button(
        label="📥 Download Excel",
        data=output,
        file_name="expenses_report.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
