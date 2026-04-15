import mss
import easyocr
import numpy as np
from PIL import Image, ImageTk, ImageOps
from googletrans import Translator
import tkinter as tk
import threading
import time
import re

# --- 1. AREA SELECTOR ---
class AreaSelector:
    def __init__(self, master):
        self.top = tk.Toplevel(master)
        self.top.attributes('-fullscreen', True, "-topmost", True)
        self.tk_bg_img = None
        
        try:
            with mss.mss() as sct:
                monitor = sct.monitors[1]
                screenshot = sct.grab(monitor)
                # EasyOCR için görüntüyü hazırla
                self.bg_img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
                self.tk_bg_img = ImageTk.PhotoImage(self.bg_img, master=master)
        except Exception as e:
            print(f"[EKRAN HATASI]: {e}")
            self.tk_bg_img = ImageTk.PhotoImage(Image.new("RGB", (1920, 1080), (0,0,0)), master=master)

        self.canvas = tk.Canvas(self.top, cursor="cross", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.create_image(0, 0, anchor="nw", image=self.tk_bg_img)
        self.canvas.create_rectangle(0, 0, self.top.winfo_screenwidth(), self.top.winfo_screenheight(), fill="black", stipple="gray50")

        self.start_x = self.start_y = self.rect = self.selection = None
        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_move_press)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)

    def on_button_press(self, event):
        self.start_x, self.start_y = event.x, event.y
        if self.rect: self.canvas.delete(self.rect)
        self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, 1, 1, outline='cyan', width=3)

    def on_move_press(self, event):
        self.canvas.coords(self.rect, self.start_x, self.start_y, event.x, event.y)

    def on_button_release(self, event):
        end_x, end_y = event.x, event.y
        self.selection = {"top": min(self.start_y, end_y), "left": min(self.start_x, end_x), 
                          "width": max(10, abs(self.start_x - end_x)), "height": max(10, abs(self.start_y - end_y))}
        self.top.destroy()

    def get_selection(self):
        self.top.wait_window()
        return self.selection

# --- 2. OVERLAY WINDOW ---
class OverlayWindow:
    def __init__(self, master, area):
        self.window = tk.Toplevel(master)
        self.window.overrideredirect(True)
        self.window.attributes("-topmost", True, "-alpha", 0.9)
        self.window.geometry(f"{area['width']}x100+{area['left']}+{area['top'] + area['height'] + 10}")
        
        self.label = tk.Label(self.window, text="AI Başlatılıyor...", fg="#00FF00", bg="#121212", 
                              font=("Verdana", 11, "bold"), wraplength=area["width"]-20, justify="center")
        self.label.pack(fill="both", expand=True)
        self.label.bind("<Button-1>", self.start_drag)
        self.label.bind("<B1-Motion>", self.do_drag)

    def start_drag(self, event): self.x, self.y = event.x, event.y
    def do_drag(self, event):
        dx, dy = event.x - self.x, event.y - self.y
        self.window.geometry(f"+{self.window.winfo_x() + dx}+{self.window.winfo_y() + dy}")

    def update_text(self, text):
        if self.window.winfo_exists(): self.label.config(text=text)

# --- 3. MAIN ENGINE ---
class MainApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Noblewolf AI Translator")
        self.root.geometry("300x400")
        self.root.configure(bg="#1c1c1c")
        
        # EasyOCR Reader (Sadece İngilizce)
        print("[INFO] AI Modeli Yükleniyor... (İlk seferde biraz sürebilir)")
        self.reader = easyocr.Reader(['en'], gpu=True) # NVIDIA varsa GPU uçurur
        self.translator = Translator()
        
        self.is_running = False
        self.area = None
        self.overlay = None
        self.setup_ui()

    def setup_ui(self):
        tk.Label(self.root, text="AI KONTROL PANELİ", fg="#00FF00", bg="#1c1c1c", font=("Verdana", 12, "bold")).pack(pady=20)
        tk.Button(self.root, text="ALAN SEÇ", command=self.select_area, bg="#333", fg="white", width=20).pack(pady=10)
        self.btn_toggle = tk.Button(self.root, text="BAŞLAT", command=self.toggle, bg="#008800", fg="white", font="bold", width=15)
        self.btn_toggle.pack(pady=30)

    def select_area(self):
        if self.is_running: self.toggle()
        self.root.withdraw()
        time.sleep(0.4)
        self.area = AreaSelector(self.root).get_selection()
        self.root.deiconify()

    def toggle(self):
        if not self.is_running:
            if not self.area: return
            self.is_running = True
            self.overlay = OverlayWindow(self.root, self.area)
            self.btn_toggle.config(text="DURDUR", bg="#880000")
            threading.Thread(target=self.ai_loop, daemon=True).start()
        else:
            self.is_running = False
            if self.overlay: self.overlay.window.destroy(); self.overlay = None
            self.btn_toggle.config(text="BAŞLAT", bg="#008800")

    def ai_loop(self):
        last_text = ""
        with mss.mss() as sct:
            while self.is_running:
                try:
                    # Görüntü yakala ve EasyOCR için formatla
                    sct_img = sct.grab(self.area)
                    img_np = np.array(sct_img)
                    
                    # EasyOCR okuma yap (Detail=0 sadece metni verir)
                    results = self.reader.readtext(img_np)
                    
                    # Güven skoru kontrolü ve metin birleştirme
                    valid_texts = [res[1] for res in results if res[2] > 0.45] # %45 güven altını çöpe at
                    full_text = " ".join(valid_texts).strip()
                    
                    # Temizlik
                    full_text = re.sub(r'[^a-zA-Z0-9\s.,!?\']', '', full_text)

                    if len(full_text) > 2 and full_text != last_text:
                        tr = self.translator.translate(full_text, dest='tr')
                        print(f"[AI OKUDU]: {full_text} -> [TR]: {tr.text}")
                        if self.is_running and self.overlay:
                            self.root.after(0, self.overlay.update_text, tr.text)
                        last_text = full_text
                    
                    time.sleep(0.6)
                except Exception as e:
                    print(f"[AI DÖNGÜ HATASI]: {e}")
                    break

    def run(self): self.root.mainloop()

if __name__ == "__main__":
    MainApp().run()