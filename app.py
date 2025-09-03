import re
from collections import defaultdict
from datetime import datetime
import streamlit as st
import pandas as pd
from io import BytesIO

st.title("Expense Tracker TH")

data = st.text_area(
    "Enter your data (format: '7 Jul: rice-meal 60 coffee-drink 50 notebook-shop 100')", height=200
)

YEAR = 2025

def is_weekend(date_str):
    dt = datetime.strptime(f"{date_str} {YEAR}", "%d %b %Y")
    return dt.weekday() >= 5

CATEGORY_EMOJI = {
    "meal": "🥞",
    "drink": "🧋",
    "shop": "💵",
    "misc": "📦",
}

if st.button("Calculate"):
    totals_weekday = defaultdict(float)
    totals_weekend = defaultdict(float)
    all_rows = []

    for line in data.strip().split('\n'):
        date_part = line.split(':')[0].strip()
        items_part = line.split(':', 1)[1] if ':' in line else ''
        weekend = is_weekend(date_part)
        day_type = "Weekend" if weekend else "Weekday"

        # จับ items
        items = re.findall(r'(\S+?)(?:-(\w+))?\s+(\d+(?:\.\d+)?)', items_part)

        for item, category, amount in items:
            amount = float(amount)

            # ถ้าไม่ระบุ category → ใช้ misc
            if not category:
                category = "misc"

            # แปลง category ตามคำพิเศษ
            if category == "food":
                category = "meal"
            elif category == "shopping":
                category = "shop"

            # รวมยอดตามวัน
            if weekend:
                totals_weekend[category] += amount
            else:
                totals_weekday[category] += amount

            # เก็บ row สำหรับ Excel
            all_rows.append({
                "Date": f"{date_part} {YEAR}",
                "Item": item,
                "Category": category,
                "Amount": amount,
                "Type": day_type
            })

    # แสดงผลสรุป
    st.subheader("Summary Weekday:")
    for category in CATEGORY_EMOJI.keys():
        amt = totals_weekday.get(category, 0)
        if amt:
            emoji = CATEGORY_EMOJI[category]
            st.write(f"{emoji} **{category.capitalize()}**: {round(amt, 2)}")

    st.subheader("Summary Weekend:")
    for category in CATEGORY_EMOJI.keys():
        amt = totals_weekend.get(category, 0)
        if amt:
            emoji = CATEGORY_EMOJI[category]
            st.write(f"{emoji} **{category.capitalize()}**: {round(amt, 2)}")

    grand_total = sum(totals_weekday.values()) + sum(totals_weekend.values())
    st.subheader(f"💵 Grand Total: {round(grand_total, 2)}")

    # สร้าง Excel
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

    st.download_button(
        label="📥 Download Excel",
        data=output,
        file_name="expenses_report.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

