import speedtest
import csv
import os
import time
from datetime import datetime

BASE_DIR = r'C:\Users\aroon\AI_Bandwidth_Project'
CSV_PATH = os.path.join(BASE_DIR, 'bandwidth_data.csv')

def run_speedtest():
    try:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] กำลังเริ่มทดสอบ...")
        
        # ตั้งค่า Speedtest
        st = speedtest.Speedtest(secure=True) # ใช้ secure=True เพื่อป้องกันการโดนบล็อก
        
        print("🔍 กำลังหา Server ที่ดีที่สุด...")
        st.get_best_server()
        
        print("⬇️ กำลังเทส Download...")
        st.download()
        
        print("⬆️ กำลังเทส Upload...")
        st.upload()
        
        results = st.results.dict()
        
        log_data = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "download_mbps": round(results['download'] / 1_000_000, 2),
            "upload_mbps": round(results['upload'] / 1_000_000, 2),
            "ping_ms": results['ping'],
            "server_name": results['server']['name'],
            "location": f"{results['server']['name']} ({results['server']['country']})", # เพิ่มจังหวัด/ประเทศ
            "isp": results['client']['isp'],
            "external_ip": results['client']['ip']
        }

        # เขียนลง CSV
        file_exists = os.path.isfile(CSV_PATH)
        with open(CSV_PATH, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=log_data.keys())
            if not file_exists or os.stat(CSV_PATH).st_size == 0:
                writer.writeheader()
            writer.writerow(log_data)
            
        print(f"✅ สำเร็จ! | DL: {log_data['download_mbps']} | Ping: {log_data['ping_ms']}")

    except Exception as e:
        print(f"❌ พลาดรอบนี้: {e}")
        # ถ้าพลาดเพราะโดนแบน ให้เว้นระยะนานขึ้นนิดนึง
        time.sleep(10)

if __name__ == "__main__":
    print("--- ระบบ AI Bandwidth Logger (Super Stable) ---")
    while True:
        run_speedtest()
        print("⏳ รออีก 1 นาทีเพื่อความปลอดภัยของ IP...")
        time.sleep(60)