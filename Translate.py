import mss
import easyocr
import numpy as np
from PIL import Image, ImageTk
from googletrans import Translator
import tkinter as tk
import threading
import time
import re
import difflib
from queue import Queue

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
                self.bg_img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
                self.tk_bg_img = ImageTk.PhotoImage(self.bg_img, master=master)
        except Exception as e:
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
        self.label = tk.Label(self.window, text="AI Hazır...", fg="#00FF00", bg="#121212", 
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

# --- 3. MAIN APP ---
class MainApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Omer Faruk AI Translator")
        self.root.geometry("300x450")
        self.root.configure(bg="#1c1c1c")
        
        print("[INFO] EasyOCR Modeli Yükleniyor...")
        self.reader = easyocr.Reader(['en'], gpu=True) 
        self.translator = Translator()
        
        self.is_running = False
        self.area = None
        self.overlay = None
        self.queue = Queue() 
        self.setup_ui()

    def setup_ui(self):
        tk.Label(self.root, text="KONTROL PANELİ", fg="#00FF00", bg="#1c1c1c", font=("Verdana", 12, "bold")).pack(pady=20)
        tk.Button(self.root, text="ALAN SEÇ", command=self.select_area, bg="#333", fg="white", width=20).pack(pady=10)
        self.mode_var = tk.StringVar(value="2") # Varsayılan Film Modu
        tk.Radiobutton(self.root, text="Hızlı Mod (Anlık)", variable=self.mode_var, value="1", bg="#1c1c1c", fg="white", selectcolor="#444").pack()
        tk.Radiobutton(self.root, text="Film Modu (Turbo)", variable=self.mode_var, value="2", bg="#1c1c1c", fg="white", selectcolor="#444").pack()
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
            if self.mode_var.get() == "1":
                threading.Thread(target=self.simple_loop, daemon=True).start()
            else:
                threading.Thread(target=self.capture_loop, daemon=True).start()
                threading.Thread(target=self.display_worker, daemon=True).start()
        else:
            self.is_running = False
            with self.queue.mutex: self.queue.queue.clear() 
            if self.overlay: self.overlay.window.destroy(); self.overlay = None
            self.btn_toggle.config(text="BAŞLAT", bg="#008800")

    def clean_text(self, text):
        return " ".join(re.sub(r'[^a-zA-Z0-9\s.,!?\']', '', text).split()).strip()

    def simple_loop(self):
        last_text = ""
        with mss.mss() as sct:
            while self.is_running:
                try:
                    results = self.reader.readtext(np.array(sct.grab(self.area)))
                    current_text = self.clean_text(" ".join([res[1] for res in results if res[2] > 0.4]))
                    if len(current_text) > 2 and current_text != last_text:
                        tr = self.translator.translate(current_text, dest='tr')
                        if self.is_running and self.overlay:
                            self.root.after(0, self.overlay.update_text, tr.text)
                        last_text = current_text
                    time.sleep(0.4)
                except: break

    def capture_loop(self):
        last_raw_text = ""
        buffer = ""
        with mss.mss() as sct:
            while self.is_running:
                try:
                    results = self.reader.readtext(np.array(sct.grab(self.area)))
                    current_raw = self.clean_text(" ".join([res[1] for res in results if res[2] > 0.45]))
                    
                    if len(current_raw) > 3 and current_raw != last_raw_text:
                        if difflib.SequenceMatcher(None, last_raw_text, current_raw).ratio() > 0.85:
                            continue
                        last_raw_text = current_raw
                        s = difflib.SequenceMatcher(None, buffer, current_raw)
                        match = s.find_longest_match(0, len(buffer), 0, len(current_raw))
                        
                        if match.size > 3: buffer += current_raw[match.b + match.size:]
                        else: buffer += " " + current_raw

                        sentences = re.findall(r'([^.!?]+[.!?])', buffer)
                        if sentences:
                            for s_text in sentences:
                                self.queue.put(s_text.strip()) 
                                buffer = buffer.replace(s_text, "").strip()
                    time.sleep(0.2)
                except: break

    # --- MOD 2: GÖSTERİCİ (ASLA SİLMEZ, GEREKİRSE TURBOYA GEÇER) ---
    def display_worker(self):
        while self.is_running:
            if not self.queue.empty():
                q_size = self.queue.qsize()
                to_translate = self.queue.get()
                
                try:
                    tr = self.translator.translate(to_translate, dest='tr')
                    if self.is_running and self.overlay:
                        self.root.after(0, self.overlay.update_text, tr.text)
                    
                    # Normal Bekleme Süresi (1.5x ayarın)
                    word_count = len(to_translate.split())
                    wait_duration = 0.7 + (word_count * 0.25)
                    
                    # --- TURBO MODU: Eğer kuyruk birikmişse gaza bas ---
                    if q_size > 1:
                        # Kuyrukta ne kadar çok cümle varsa o kadar hızlan
                        # 0.3 alt limit olsun ki en azından bir anlık görünsün
                        speed_factor = max(0.2, 1.0 - (q_size * 0.15))
                        wait_duration *= speed_factor
                        print(f"[TURBO] Kuyruk: {q_size} | Bekleme: {wait_duration:.2f}s")
                    
                    # Bekleme yaparken thread durdurulabilir olsun
                    start_time = time.time()
                    while time.time() - start_time < wait_duration:
                        if not self.is_running: break
                        time.sleep(0.05)
                        
                except Exception as e:
                    print(f"Display Error: {e}")
            else:
                time.sleep(0.1)

    def run(self): self.root.mainloop()

if __name__ == "__main__":
    MainApp().run()