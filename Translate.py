import mss
import pytesseract
from PIL import Image, ImageTk, ImageOps, ImageFilter
from googletrans import Translator
import tkinter as tk
import time
import re
import difflib

# --- GENEL YARDIMCI SINIFLAR ---

class AreaSelector:
    def __init__(self):
        self.root = tk.Tk()
        self.root.attributes('-fullscreen', True, "-topmost", True)
        with mss.mss() as sct:
            screenshot = sct.grab(sct.monitors[1])
            self.bg_img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
            self.tk_bg_img = ImageTk.PhotoImage(self.bg_img)
        self.canvas = tk.Canvas(self.root, cursor="cross", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.create_image(0, 0, anchor="nw", image=self.tk_bg_img)
        self.canvas.create_rectangle(0, 0, self.root.winfo_screenwidth(), self.root.winfo_screenheight(), fill="black", stipple="gray50")
        self.start_x = self.start_y = self.rect = self.selection = None
        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_move_press)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)
        self.root.bind("<Escape>", lambda e: self.root.destroy())

    def on_button_press(self, event):
        self.start_x, self.start_y = event.x, event.y
        if self.rect: self.canvas.delete(self.rect)
        self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, 1, 1, outline='cyan', width=3)

    def on_move_press(self, event):
        self.canvas.coords(self.rect, self.start_x, self.start_y, event.x, event.y)

    def on_button_release(self, event):
        end_x, end_y = event.x, event.y
        self.selection = {"top": min(self.start_y, end_y), "left": min(self.start_x, end_x), 
                          "width": abs(self.start_x - end_x), "height": abs(self.start_y - end_y)}
        self.root.destroy()

    def get_selection(self):
        self.root.mainloop()
        return self.selection

class OverlayWindow:
    def __init__(self, area):
        self.root = tk.Tk()
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True, "-alpha", 0.85)
        x, y = area["left"], area["top"] + area["height"] + 15
        self.root.geometry(f"{area['width']}x80+{x}+{y}")
        self.label = tk.Label(self.root, text="Sistem Hazır...", fg="#00FF00", bg="#121212", 
                              font=("Verdana", 11, "bold"), wraplength=area["width"]-20, justify="center")
        self.label.pack(fill="both", expand=True)

    def update_text(self, text):
        self.label.config(text=text)
        self.root.update()

# --- ANA MOTOR ---

class ScreenTranslator:
    def __init__(self):
        self.mss_instance = mss.mss()
        self.translator = Translator()
        self.buffer = ""
        self.next_update_time = 0

    def run(self):
        print("\n--- ÇEVİRİ KONSOLU v4.5 ---")
        print("1 - BASİT MOD (Favori - Stabil)")
        print("2 - GELİŞMİŞ MOD (Agresif - Senkronize)")
        secim = input("Mod seç kanka (1/2): ")

        selector = AreaSelector()
        area = selector.get_selection()
        if not area or area["width"] < 10: return

        if secim == "1":
            self.simple_mode(area)
        else:
            self.advanced_mode(area)

    def simple_mode(self, area):
        """Senin dokunulmasını istemediğin o saf ve güzel versiyon"""
        overlay = OverlayWindow(area)
        last_text = ""
        print("Basit Mod Aktif...")
        try:
            while True:
                sct_img = self.mss_instance.grab(area)
                img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
                raw_text = pytesseract.image_to_string(img).strip()
                
                if raw_text and raw_text != last_text:
                    try:
                        clean_text = " ".join(raw_text.split())
                        tr = self.translator.translate(clean_text, dest='tr')
                        overlay.update_text(tr.text)
                        last_text = raw_text
                    except Exception as e:
                        print(f"Hata: {e}")
                
                overlay.root.update()
                time.sleep(0.5)
        except: print("Basit Mod Durdu.")

    def advanced_mode(self, area):
        """Turbo senkronizasyon ve görüntü işleme içeren agresif mod"""
        overlay = OverlayWindow(area)
        last_raw_text = ""
        print("Gelişmiş Mod Aktif (Turbo + Filtre)...")
        
        def preprocess(pil_img):
            img = ImageOps.grayscale(pil_img)
            img = img.point(lambda p: 255 if p > 160 else 0) # Sert kontrast
            return img

        def clean_junk(text):
            return " ".join(re.sub(r'[^a-zA-Z0-9\s.,!?\'"-]', '', text).split())

        try:
            while True:
                sct_img = self.mss_instance.grab(area)
                raw_img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
                
                # Gelişmiş Filtreleme
                processed = preprocess(raw_img)
                current_raw = clean_junk(pytesseract.image_to_string(processed, config='--psm 6'))
                
                if len(current_raw) < 3:
                    overlay.root.update(); time.sleep(0.1); continue

                if current_raw and current_raw != last_raw_text:
                    last_raw_text = current_raw
                    
                    # Kelime dikme (Overlap Check)
                    s = difflib.SequenceMatcher(None, self.buffer, current_raw)
                    match = s.find_longest_match(0, len(self.buffer), 0, len(current_raw))
                    if match.size > 3:
                        self.buffer += current_raw[match.b + match.size:]
                    else:
                        self.buffer += " " + current_raw

                    sentences = re.findall(r'([^.!?]+[.!?])', self.buffer)
                    
                    if sentences:
                        is_lagging = len(sentences) > 2
                        # Lag varsa son iki cümleyi birleştir, yoksa ilkini al
                        to_translate = " ".join(sentences[-2:]).strip() if is_lagging else sentences[0].strip()

                        if time.time() >= self.next_update_time or is_lagging:
                            try:
                                tr = self.translator.translate(to_translate, dest='tr')
                                overlay.update_text(tr.text)
                                # Lag varsa bekleme süresini daralt
                                self.next_update_time = time.time() + (0.6 if is_lagging else 2.0)
                                
                                if is_lagging:
                                    self.buffer = "" 
                                else:
                                    match = re.search(re.escape(to_translate), self.buffer)
                                    if match: self.buffer = self.buffer[match.end():].strip()
                            except: pass
                
                overlay.root.update()
                time.sleep(0.1) # Agresif tarama hızı
        except: print("Gelişmiş Mod Durdu.")

if __name__ == "__main__":
    app = ScreenTranslator()
    app.run()