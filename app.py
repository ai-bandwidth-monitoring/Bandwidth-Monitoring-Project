import streamlit as st
import pandas as pd
import subprocess
import os
import json
from datetime import datetime

# ตั้งค่าหน้าจอ
st.set_page_config(page_title="AI Bandwidth Monitoring", layout="wide")

# พาธไฟล์ (เช็คให้ชัวร์ว่าพาธถูกต้อง)
BASE_DIR = r'C:\Users\aroon\AI_Bandwidth_Project'
EXE_PATH = os.path.join(BASE_DIR, 'speedtest-cli')
CSV_PATH = os.path.join(BASE_DIR, 'bandwidth_data.csv')

st.title("🌐 AI Bandwidth Monitoring Dashboard")

# --- ฟังก์ชันสั่งรัน Speedtest ใหม่ ---
def run_manual_test():
    with st.spinner('กำลังทดสอบความเร็ว... กรุณารอประมาณ 30 วินาที'):
        try:
            result = subprocess.run(
                f'"{EXE_PATH}" --format=json --accept-license --accept-gdpr', 
                capture_output=True, text=True, shell=True
            )
            if result.stdout:
                data = json.loads(result.stdout)
                new_log = {
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "download_mbps": round(data['download']['bandwidth'] / 125000, 2),
                    "upload_mbps": round(data['upload']['bandwidth'] / 125000, 2),
                    "ping_ms": data['ping']['latency'],
                    "server_name": data['server']['name']
                }
                # บันทึกลง CSV ทันที
                df_new = pd.DataFrame([new_log])
                df_new.to_csv(CSV_PATH, mode='a', header=not os.path.exists(CSV_PATH), index=False)
                st.success(f"ทดสอบสำเร็จ! ความเร็วปัจจุบัน: {new_log['download_mbps']} Mbps")
            else:
                st.error("ไม่สามารถดึงข้อมูลได้ กรุณาลองใหม่")
        except Exception as e:
            st.error(f"เกิดข้อผิดพลาด: {e}")

# --- ส่วนปุ่มกด ---
st.sidebar.header("Control Panel")
if st.sidebar.button("🚀 Run Speedtest Now"):
    run_manual_test()

# --- ส่วนแสดงผล ---
if os.path.exists(CSV_PATH):
    df = pd.read_csv(CSV_PATH)
    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
    df = df.dropna(subset=['timestamp']).sort_values('timestamp', ascending=False)

    # Metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("Download (Avg)", f"{round(df['download_mbps'].mean(), 2)} Mbps")
    col2.metric("Upload (Avg)", f"{round(df['upload_mbps'].mean(), 2)} Mbps")
    col3.metric("Latest Ping", f"{df['ping_ms'].iloc[0]} ms")

    # Chart
    st.subheader("📈 สถิติความเร็วย้อนหลัง")
    st.line_chart(df.set_index('timestamp')[['download_mbps', 'upload_mbps']])

    # Table
    st.subheader("📄 ประวัติการทดสอบ")
    st.dataframe(df, use_container_width=True)
else:
    st.info("ยังไม่มีข้อมูลใน CSV กรุณากดปุ่มเพื่อเริ่มทดสอบครั้งแรก")

st.sidebar.write("---")
st.sidebar.caption(f"Last updated: {datetime.now().strftime('%H:%M:%S')}")

from sklearn.linear_model import LinearRegression
import numpy as np

st.write("---")
st.header("🤖 AI Bandwidth Forecasting (Beta)")

if len(df) > 5:  # ต้องมีข้อมูลอย่างน้อย 5 ชุดถึงจะพยากรณ์ได้
    # เตรียมข้อมูลสำหรับ AI
    df_ai = df.sort_values('timestamp')
    X = np.array(range(len(df_ai))).reshape(-1, 1) # ลำดับเวลา
    y = df_ai['download_mbps'].values # ค่าสปีด

    # สร้างและฝึก AI ตัวจิ๋ว
    model = LinearRegression()
    model.fit(X, y)

    # พยากรณ์รอบถัดไป
    next_index = np.array([[len(df_ai)]])
    prediction = model.predict(next_index)[0]
    
    # คำนวณแนวโน้ม
    trend = "📉 มีแนวโน้มลดลง" if prediction < y[-1] else "📈 มีแนวโน้มเพิ่มขึ้น"
    
    col_ai1, col_ai2 = st.columns(2)
    col_ai1.metric("Predicted Next Speed", f"{round(prediction, 2)} Mbps", delta=round(prediction - y[-1], 2))
    col_ai2.info(f"**AI Analysis:** {trend} ในรอบถัดไป")
    
    st.caption("หมายเหตุ: ระบบใช้ Linear Regression ในการวิเคราะห์แนวโน้มจากข้อมูลชุดปัจจุบัน")
else:
    st.warning("🤖 AI กำลังรอข้อมูลเพิ่มเติม... (ต้องมีข้อมูลอย่างน้อย 5 แถว)")
    
import streamlit as st
import pandas as pd

# --- 1. อ่านข้อมูลจาก CSV ---
df = pd.read_csv('bandwidth_data.csv')

# --- 2. แปลงคอลัมน์เวลาให้เป็นรูปแบบที่ Python เข้าใจ (สำคัญมาก!) ---
df['timestamp'] = pd.to_datetime(df['timestamp'])

# --- 3. เพิ่มตัวเลือกวันที่ (วางไว้ที่แถบด้านข้าง หรือส่วนบนของหน้าจอ) ---
st.sidebar.header("ตัวเลือกการกรองข้อมูล")
# สร้างตัวเลือกวันที่ โดยค่าเริ่มต้นให้เป็นวันที่ล่าสุดที่มีข้อมูล
selected_date = st.sidebar.date_input(
    "เลือกวันที่ที่ต้องการดูข้อมูล", 
    df['timestamp'].dt.date.max()
)

# --- 4. กรองข้อมูลตามวันที่เลือก ---
# สร้างข้อมูลชุดใหม่ (Filtered Data) ที่มีเฉพาะวันที่เราเลือก
mask = (df['timestamp'].dt.date == selected_date)
day_data = df.loc[mask]

# --- 5. นำข้อมูลที่กรองแล้ว (day_data) ไปแสดงผลในกราฟหรือตาราง ---
st.title(f"รายงานผลวันที่ {selected_date}")

if not day_data.empty:
    # เอากราฟมาโชว์โดยใช้ข้อมูล day_data แทน df ตัวเก่า
    st.line_chart(day_data.set_index('timestamp')[['download_mbps', 'upload_mbps']])
    
    # ใส่ส่วน Average 
    col1, col2 = st.columns(2)
    col1.metric("เฉลี่ยดาวน์โหลด", f"{day_data['download_mbps'].mean():.2f} Mbps")
    col2.metric("ค่าปิงสูงสุด", f"{day_data['ping_ms'].max():.2f} ms")
else:
    st.warning("⚠️ ไม่มีข้อมูลการทดสอบในวันที่เลือก")
    
min_speed = 10.0  # Mbps
max_ping = 100.0  # ms

# หาช่วงเวลาที่สัญญาณมีปัญหา
bad_signal = day_data[(day_data['download_mbps'] < min_speed) | (day_data['ping_ms'] > max_ping)]

st.subheader("⚠️ บันทึกช่วงเวลาสัญญาณไม่ดี")
if not bad_signal.empty:
    # แสดงตารางเฉพาะช่วงที่มีปัญหา
    st.write(f"พบปัญหาทั้งหมด {len(bad_signal)} ครั้ง ในวันที่เลือก")
    st.dataframe(bad_signal[['timestamp', 'download_mbps','upload_mbps','ping_ms','server_name']])
else:
    st.success("สัญญาณปกติดีตลอดทั้งวัน!")