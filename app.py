import streamlit as st
import pandas as pd
import subprocess
import os
import json
import numpy as np
from datetime import datetime
from sklearn.linear_model import LinearRegression

# --- 1. การตั้งค่าเบื้องต้น ---
st.set_page_config(page_title="AI Bandwidth Monitoring", layout="wide")

# ตั้งค่า Path ให้ทำงานได้ทั้ง Windows และ Linux Cloud
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, 'bandwidth_data.csv')

# --- 2. ฟังก์ชันหลัก ---
def run_manual_test():
    """ฟังก์ชันสั่งรัน Speedtest"""
    with st.spinner('กำลังทดสอบความเร็ว... กรุณารอประมาณ 30 วินาที'):
        try:
            # ตรวจสอบว่ารันบน Cloud หรือ Windows
            # ถ้าบน Cloud ต้องมีคำว่า speedtest-cli ใน packages.txt
            command = 'speedtest-cli --json' if os.name != 'nt' else 'speedtest-cli.exe --format=json'
            
            result = subprocess.run(command, capture_output=True, text=True, shell=True)
            
            if result.stdout:
                data = json.loads(result.stdout)
                # จัดการโครงสร้างข้อมูลให้เข้ากับ CSV
                new_log = {
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "download_mbps": round(data['download']['bandwidth'] / 125000, 2) if 'download' in data else 0,
                    "upload_mbps": round(data['upload']['bandwidth'] / 125000, 2) if 'upload' in data else 0,
                    "ping_ms": data['ping']['latency'] if 'ping' in data else 0,
                    "server_name": data['server']['name'] if 'server' in data else "Unknown"
                }
                
                # บันทึกลง CSV
                df_new = pd.DataFrame([new_log])
                df_new.to_csv(CSV_PATH, mode='a', header=not os.path.exists(CSV_PATH), index=False)
                st.success(f"ทดสอบสำเร็จ! ความเร็ว: {new_log['download_mbps']} Mbps")
                st.rerun() # รีโหลดหน้าเว็บเพื่ออัปเดตกราฟ
            else:
                st.error("ไม่สามารถดึงข้อมูลได้ (ตรวจสอบว่าติดตั้ง speedtest-cli หรือยัง)")
        except Exception as e:
            st.error(f"เกิดข้อผิดพลาด: {e}")

# --- 3. ส่วน UI Dashboard ---
st.title("🌐 AI Bandwidth Monitoring Dashboard")

# Sidebar
st.sidebar.header("Control Panel")
if st.sidebar.button("🚀 Run Speedtest Now"):
    run_manual_test()

# --- 4. ส่วนดึงข้อมูลและแสดงผล ---
if os.path.exists(CSV_PATH):
    df = pd.read_csv(CSV_PATH)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values('timestamp', ascending=False)

    # Metrics
    col1, col2, col3 = st.columns(3)
    if not df.empty:
        col1.metric("Download (Avg)", f"{df['download_mbps'].mean():.2f} Mbps")
        col2.metric("Upload (Avg)", f"{df['upload_mbps'].mean():.2f} Mbps")
        col3.metric("Latest Ping", f"{df['ping_ms'].iloc[0]} ms")

        # กราฟแสดงแนวโน้ม
        st.subheader("📈 สถิติความเร็วย้อนหลัง")
        st.line_chart(df.set_index('timestamp')[['download_mbps', 'upload_mbps']])

        # ส่วน AI Forecasting
        st.write("---")
        st.header("🤖 AI Bandwidth Forecasting")
        
        if len(df) >= 5:
            df_ai = df.sort_values('timestamp')
            X = np.array(range(len(df_ai))).reshape(-1, 1)
            y = df_ai['download_mbps'].values
            
            model = LinearRegression()
            model.fit(X, y)
            
            prediction = model.predict(np.array([[len(df_ai)]]))[0]
            trend = "📈 แนวโน้มดีขึ้น" if prediction > y[-1] else "📉 แนวโน้มลดลง"
            
            c1, c2 = st.columns(2)
            c1.metric("Predicted Next Speed", f"{prediction:.2f} Mbps", delta=f"{prediction - y[-1]:.2f}")
            c2.info(f"**AI Analysis:** {trend}")
        else:
            st.warning("🤖 AI ต้องการข้อมูลอย่างน้อย 5 ชุดเพื่อเริ่มพยากรณ์")

        # ตารางข้อมูล
        st.subheader("📄 ประวัติการทดสอบทั้งหมด")
        st.dataframe(df, use_container_width=True)
    else:
        st.info("ไฟล์ข้อมูลยังว่างเปล่า")
else:
    st.info("🏠 ยินดีต้อนรับ! ยังไม่พบไฟล์ข้อมูล (bandwidth_data.csv) กรุณากดปุ่มด้านซ้ายเพื่อทดสอบครั้งแรก")

st.sidebar.write("---")
st.sidebar.caption(f"Last updated: {datetime.now().strftime('%H:%M:%S')}")