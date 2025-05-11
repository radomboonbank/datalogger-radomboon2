import streamlit as st
import pandas as pd
import gspread
import json
from datetime import datetime

from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials


# Load credentials from Streamlit secrets
creds_dict = json.loads(st.secrets["GOOGLE_SERVICE_ACCOUNT"])
scopes = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]
credentials = Credentials.from_service_account_info(creds_dict, scopes=scopes)
credentials.refresh(Request())

try:
    credentials.refresh(Request())
    st.success("✅ Token refresh ผ่านแล้ว")
except Exception as e:
    st.error(f"Refresh error: {e}")


from google.auth.transport.requests import Request

try:
    credentials.refresh(Request())
    st.success("✅ Token refresh สำเร็จ")
except Exception as e:
    st.error(f"❌ Token refresh ล้มเหลว: {e}")

client = gspread.authorize(credentials)

# Constants
SHEET_ID = "1bZbgTztJiYz2iIucxOZhTVILhn2ArhIg_38143su0uE"

SHEET_NAME = "checklist_records"


# Open worksheet
sheet = client.open_by_key(SHEET_ID).worksheet(SHEET_NAME)

# Ensure headers exist
headers = sheet.row_values(1)
expected_headers = ["Event ID", "วันที่", "เวลา", "ชื่อพนักงาน", "ชื่อผู้รับกะ", "ช่วงเวลา", "ข้อมูลแผนกที่ตรวจสอบ", "หมายเหตุหรือปัญหา"] +     [f"หัวข้อ{i+1}" for i in range(10)] + [f"สถานะ{i+1}" for i in range(10)] + [f"หมายเหตุ{i+1}" for i in range(10)]

if headers != expected_headers:
    sheet.insert_row(expected_headers, 1)

# Streamlit UI
st.title("📋 บันทึกการทำงานประจำวัน")

with st.form("log_form"):
    date = st.date_input("📅 วันที่ทำงาน", value=datetime.today())
    time = st.time_input("⏰ เวลา", value=datetime.now().time())
    employee = st.selectbox("🙋‍♀️ ชื่อพนักงาน", ["รดมบุญ ทักษณา"])
    receiver = st.selectbox("🙋‍♂️ ชื่อผู้รับกะ", ["รดมบุญ ทักษณา"])
    shift = st.selectbox("🗂️ ช่วงเวลาตลอดสอบ", ["ตรวจละ 00.00 - 08.00 น.", "ตรวจละ 08.00 - 16.00 น.", "ตรวจละ 16.00 - 24.00 น."])
    department = st.selectbox("🏢 ข้อมูลแผนกที่ตรวจสอบ", ["แผนก หถก1และ2", "แผนก หถก3และ4", "แผนก หถก5และ6"])
    note = st.text_area("❗ หมายเหตุหรือปัญหา", "ถ้ามี")

    st.subheader("🔍 รายการตรวจสอบสถานะ")
    topics = [
        "ตรวจสอบ Alarm All (202)",
        "ตรวจสอบ RTU down",
        "ตรวจสอบ Voltage Deviation (1001)",
        "ตรวจสอบ AVC ต้องเป็น A",
        "ตรวจสอบ การส่งต่อ Switching Order",
        "ตรวจสอบ Tag Summary (301)",
        "ตรวจสอบ Manual Replace",
        "ตรวจสอบ Low Gas Alarm ที่ Breaker",
        "ตรวจสอบ เหตุการณ์ ทริป ที่ CBD-BESS",
        "ตรวจสอบ Log Book on Web",
    ]
    
    statuses = []
    reasons = []

    for idx, topic in enumerate(topics):
        st.write(f"{idx+1}. {topic}")
        col1, col2 = st.columns([2, 5])
        with col1:
            status = st.radio("สถานะ", ["ปกติ", "ผิดปกติ"], key=f"status_{idx}", horizontal=True)
        with col2:
            reason = st.text_input("รายละเอียดสิ่งผิดปกติ", key=f"reason_{idx}")
        statuses.append(status)
        reasons.append(reason)

    submitted = st.form_submit_button("✅ บันทึกข้อมูล")

if submitted:
    event_id = datetime.now().strftime("%Y%m%d%H%M%S")
    row_data = {
        "Event ID": event_id,
        "วันที่": str(date),
        "เวลา": str(time),
        "ชื่อพนักงาน": employee,
        "ชื่อผู้รับกะ": receiver,
        "ช่วงเวลา": shift,
        "ข้อมูลแผนกที่ตรวจสอบ": department,
        "หมายเหตุหรือปัญหา": note
    }
    for i in range(10):
        row_data[f"หัวข้อ{i+1}"] = topics[i]
        row_data[f"สถานะ{i+1}"] = statuses[i]
        row_data[f"หมายเหตุ{i+1}"] = reasons[i]

    sheet.append_row([row_data.get(h, "") for h in expected_headers])
    st.success("✅ บันทึกข้อมูลเรียบร้อยแล้ว")