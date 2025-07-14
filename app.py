import re
from collections import defaultdict
from datetime import datetime
import streamlit as st
import pandas as pd
from io import BytesIO

st.title("Expense Tracker TH 🛍️")

data = st.text_area("Enter your data (format: '7 Jul: rice-meal 60 coffee-meal 50')", height=200)

YEAR = 2025

def is_weekend(date_str):
    dt = datetime.strptime(f"{date_str} {YEAR}", "%d %b %Y")
    return dt.weekday() >= 5

CATEGORY_EMOJI = {
    "meal": "🍚",
    "shopping": "🛍️",
    "misc": "📦",
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
st.subheader("Weekday")
for category in CATEGORY_EMOJI.keys():
    amt = totals_weekday.get(category, 0)
    if amt:
        emoji = CATEGORY_EMOJI.get(category, "❓")
        amt_display = f"{amt:.0f}" if amt.is_integer() else f"{amt:.2f}"
        st.write(f"{emoji} **{category.capitalize()}**: {amt_display}")

st.subheader("Weekend")
for category in CATEGORY_EMOJI.keys():
    amt = totals_weekend.get(category, 0)
    if amt:
        emoji = CATEGORY_EMOJI.get(category, "❓")
        amt_display = f"{amt:.0f}" if amt.is_integer() else f"{amt:.2f}"
        st.write(f"{emoji} **{category.capitalize()}**: {amt_display}")

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
