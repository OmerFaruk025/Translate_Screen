import mss
import pytesseract
from PIL import Image, ImageTk, ImageOps
from googletrans import Translator
import tkinter as tk
import threading
import time
import re
import difflib

# --- 1. AREA SELECTOR ---
class AreaSelector:
    def __init__(self, master):
        self.top = tk.Toplevel(master)
        self.top.attributes('-fullscreen', True, "-topmost", True)
        
        try:
            with mss.mss() as sct:
                monitor = sct.monitors[1]
                screenshot = sct.grab(monitor)
                self.bg_img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
                self.tk_bg_img = ImageTk.PhotoImage(self.bg_img, master=master)
        except Exception as e:
            print(f"[SEÇİM HATASI]: {e}")

        self.canvas = tk.Canvas(self.top, cursor="cross", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.create_image(0, 0, anchor="nw", image=self.tk_bg_img)
        self.canvas.create_rectangle(0, 0, self.top.winfo_screenwidth(), self.top.winfo_screenheight(), 
                                     fill="black", stipple="gray50")

        self.start_x = self.start_y = self.rect = self.selection = None
        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_move_press)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)
        self.top.bind("<Escape>", lambda e: self.top.destroy())

    def on_button_press(self, event):
        self.start_x, self.start_y = event.x, event.y
        if self.rect: self.canvas.delete(self.rect)
        self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, 1, 1, outline='cyan', width=3)

    def on_move_press(self, event):
        self.canvas.coords(self.rect, self.start_x, self.start_y, event.x, event.y)

    def on_button_release(self, event):
        end_x, end_y = event.x, event.y
        self.selection = {
            "top": min(self.start_y, end_y), 
            "left": min(self.start_x, end_x), 
            "width": max(10, abs(self.start_x - end_x)), 
            "height": max(10, abs(self.start_y - end_y))
        }
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
        x, y = area["left"], area["top"] + area["height"] + 15
        self.window.geometry(f"{area['width']}x80+{x}+{y}")
        
        self.label = tk.Label(self.window, text="Sistem Hazır...", fg="#00FF00", bg="#121212", 
                              font=("Verdana", 11, "bold"), wraplength=area["width"]-20)
        self.label.pack(fill="both", expand=True)

    def update_text(self, text):
        if self.window.winfo_exists():
            self.label.config(text=text)

    def destroy(self):
        if self.window.winfo_exists():
            self.window.destroy()

# --- 3. ANA UYGULAMA ---
class MainApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Noblewolf Translator")
        self.root.geometry("300x400")
        self.root.configure(bg="#1c1c1c")
        
        self.translator = Translator()
        self.is_running = False
        self.area = None
        self.overlay = None
        self.buffer = ""
        self.next_update_time = 0
        
        self.setup_ui()

    def setup_ui(self):
        tk.Label(self.root, text="KONTROL PANELİ", fg="#00FF00", bg="#1c1c1c", font=("Verdana", 12, "bold")).pack(pady=20)
        tk.Button(self.root, text="1. ALAN SEÇ", command=self.select_area, bg="#333", fg="white", width=20).pack(pady=10)
        
        self.mode_var = tk.StringVar(value="1")
        tk.Radiobutton(self.root, text="Basit Mod", variable=self.mode_var, value="1", bg="#1c1c1c", fg="white", selectcolor="#444").pack()
        tk.Radiobutton(self.root, text="Gelişmiş Mod", variable=self.mode_var, value="2", bg="#1c1c1c", fg="white", selectcolor="#444").pack()

        self.btn_toggle = tk.Button(self.root, text="BAŞLAT", command=self.toggle, bg="#008800", fg="white", font=("bold"), width=15)
        self.btn_toggle.pack(pady=30)

    # --- BURASI EKSİKTİ ---
    def run(self):
        self.root.mainloop()

    def select_area(self):
        self.root.withdraw()
        time.sleep(0.3)
        selector = AreaSelector(self.root)
        self.area = selector.get_selection()
        self.root.deiconify()

    def toggle(self):
        if not self.is_running:
            if not self.area: return
            self.is_running = True
            self.overlay = OverlayWindow(self.root, self.area)
            self.btn_toggle.config(text="DURDUR", bg="#880000")
            
            target = self.simple_loop if self.mode_var.get() == "1" else self.advanced_loop
            threading.Thread(target=target, daemon=True).start()
        else:
            self.is_running = False
            if self.overlay:
                temp_overlay = self.overlay
                self.overlay = None
                temp_overlay.destroy()
            self.btn_toggle.config(text="BAŞLAT", bg="#008800")

    def simple_loop(self):
        last_text = ""
        with mss.mss() as sct:
            while self.is_running:
                try:
                    sct_img = sct.grab(self.area)
                    img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
                    raw_text = pytesseract.image_to_string(img).strip()
                    
                    if raw_text and raw_text != last_text and len(raw_text) > 2:
                        clean = " ".join(raw_text.split())
                        tr = self.translator.translate(clean, dest='tr')
                        print(f"[OKUNAN]: {clean} -> [TR]: {tr.text}")
                        if self.is_running and self.overlay:
                            self.root.after(0, self.overlay.update_text, tr.text)
                        last_text = raw_text
                    time.sleep(0.5)
                except: break

    def advanced_loop(self):
        def preprocess(pil_img):
            img = ImageOps.grayscale(pil_img)
            img = img.point(lambda p: 255 if p > 160 else 0)
            return img
        
        last_raw_text = ""
        with mss.mss() as sct:
            while self.is_running:
                try:
                    sct_img = sct.grab(self.area)
                    raw_img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
                    processed = preprocess(raw_img)
                    current_raw = " ".join(re.sub(r'[^a-zA-Z0-9\s.,!?\'"-]', '', pytesseract.image_to_string(processed, config='--psm 6')).split())
                    
                    if len(current_raw) > 2 and current_raw != last_raw_text:
                        last_raw_text = current_raw
                        s = difflib.SequenceMatcher(None, self.buffer, current_raw)
                        match = s.find_longest_match(0, len(self.buffer), 0, len(current_raw))
                        if match.size > 3: self.buffer += current_raw[match.b + match.size:]
                        else: self.buffer += " " + current_raw

                        sentences = re.findall(r'([^.!?]+[.!?])', self.buffer)
                        if sentences:
                            is_lagging = len(sentences) > 2
                            to_translate = " ".join(sentences[-2:]).strip() if is_lagging else sentences[0].strip()
                            if time.time() >= self.next_update_time or is_lagging:
                                tr = self.translator.translate(to_translate, dest='tr')
                                if self.is_running and self.overlay:
                                    self.root.after(0, self.overlay.update_text, tr.text)
                                self.next_update_time = time.time() + (0.6 if is_lagging else 2.0)
                                if is_lagging: self.buffer = ""
                                else:
                                    m = re.search(re.escape(to_translate), self.buffer)
                                    if m: self.buffer = self.buffer[m.end():].strip()
                    time.sleep(0.1)
                except: break

if __name__ == "__main__":
    MainApp().run()