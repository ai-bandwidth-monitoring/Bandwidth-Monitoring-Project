import speedtest
import csv
import os
import time
from datetime import datetime

# --- 1. ตั้งค่า Path ให้ยืดหยุ่น ---
# ใช้คำสั่งนี้เพื่อให้โปรแกรมหาตำแหน่งโฟลเดอร์ปัจจุบันเองอัตโนมัติ
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, 'bandwidth_data.csv')

def run_speedtest():
    try:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 🚀 กำลังเริ่มทดสอบ...")
        
        # ตั้งค่า Speedtest พร้อมโหมดปลอดภัย
        st_client = speedtest.Speedtest(secure=True)
        
        print("🔍 กำลังหา Server ที่ดีที่สุด...")
        st_client.get_best_server()
        
        print("⬇️ กำลังเทส Download...")
        st_client.download()
        
        print("⬆️ กำลังเทส Upload...")
        st_client.upload()
        
        results = st_client.results.dict()
        
        # เตรียมข้อมูลสำหรับบันทึก (คัดเฉพาะคอลัมน์ที่แอป app.py ต้องใช้)
        log_data = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "download_mbps": round(results['download'] / 1_000_000, 2),
            "upload_mbps": round(results['upload'] / 1_000_000, 2),
            "ping_ms": round(results['ping'], 2),
            "server_name": results['server']['name'],
            "location": f"{results['server']['name']} ({results['server']['country']})",
            "isp": results['client']['isp'],
            "external_ip": results['client']['ip']
        }

        # --- 2. เขียนลง CSV (จัดการเรื่อง Header อัตโนมัติ) ---
        file_exists = os.path.isfile(CSV_PATH)
        with open(CSV_PATH, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=log_data.keys())
            
            # ถ้ายังไม่มีไฟล์ หรือไฟล์ว่าง ให้เขียน Header ก่อน
            if not file_exists or os.stat(CSV_PATH).st_size == 0:
                writer.writeheader()
                
            writer.writerow(log_data)
            
        print(f"✅ บันทึกเรียบร้อย! | DL: {log_data['download_mbps']} Mbps | Ping: {log_data['ping_ms']} ms")

    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")
        # หากเกิดข้อผิดพลาด (เช่น เน็ตหลุด) ให้รอสักพักก่อนเริ่มใหม่
        time.sleep(20)

if __name__ == "__main__":
    print("="*40)
    print("🛰️  AI Bandwidth Logger (Super Stable Mode)")
    print(f"📂 บันทึกข้อมูลไปที่: {CSV_PATH}")
    print("="*40)
    
    try:
        while True:
            run_speedtest()
            print(f"⏳ รออีก 60 วินาที เพื่อรักษาสุขภาพ IP และความแม่นยำ...")
            time.sleep(60)
    except KeyboardInterrupt:
        print("\n🛑 หยุดการทำงานโดยผู้ใช้")