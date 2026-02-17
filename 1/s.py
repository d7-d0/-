import tkinter as tk
from tkinter import ttk 
import threading
import os
import requests

# --- الجزء الخاص بالروابط (دمج 1.txt) ---
# يمكنك إضافة أي عدد من الروابط هنا بين القوسين [ ] وكل رابط بين علامتي " " وفصل بينهما بفاصلة ,
URLS_LIST = [
    "https://example.com/file1.zip",
    "https://example.com/image.jpg",
    "https://example.com/video.mp4",
    # أضف الروابط الإضافية هنا بنفس التنسيق
]

def download_file(url, status_label, progress_bar):
    try:
        response = requests.get(url, stream=True, timeout=20)
        response.raise_for_status() 
        
        total_size = int(response.headers.get('content-length', 0))
        filename = url.split("/")[-1] if url.split("/")[-1] else "file_downloaded"
        
        if not os.path.exists("downloads"):
            os.makedirs("downloads")
        
        filepath = os.path.join("downloads", filename)

        downloaded = 0
        with open(filepath, "wb") as f:
            for chunk in response.iter_content(chunk_size=1024 * 16):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        percent = (downloaded / total_size) * 100
                        progress_bar['value'] = percent
                        status_label.config(text=f"جاري تحميل: {filename} ({int(percent)}%)")
                        root.update_idletasks()
        return True
    except Exception as e:
        status_label.config(text=f"فشل تحميل: {url.split('/')[-1]}\nالسبب: {str(e)}")
        return False

def run_task():
    btn.config(state="disabled")
    
    if not URLS_LIST:
        status_label.config(text="⚠️ لا توجد روابط مدمجة في الكود!")
        btn.config(state="normal")
        return

    for i, url in enumerate(URLS_LIST):
        status_label.config(text=f"بدء الملف {i+1} من {len(URLS_LIST)}...")
        success = download_file(url, status_label, progress_bar)
        if not success:
            continue
            
    status_label.config(text="✅ اكتمل تحميل القائمة المدمجة!")
    progress_bar['value'] = 100
    btn.config(state="normal")

def start_download():
    threading.Thread(target=run_task, daemon=True).start()

# --- إعدادات الواجهة ---
root = tk.Tk()
root.title("محمل الروابط المدمجة")
root.geometry("500x250")

style = ttk.Style()
style.theme_use('clam')

tk.Label(root, text="برنامج التحميل المباشر (الروابط داخل الكود)", font=("Arial", 12, "bold")).pack(pady=10)

progress_bar = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate")
progress_bar.pack(pady=10)

status_label = tk.Label(root, text="اضغط ابدأ لتحميل القائمة المدمجة", font=("Arial", 9), fg="#555")
status_label.pack(pady=10)

btn = tk.Button(root, text="ابدأ التحميل الآن", command=start_download, bg="#2ecc71", fg="white", font=("Arial", 10, "bold"))
btn.pack(pady=10)

root.mainloop()