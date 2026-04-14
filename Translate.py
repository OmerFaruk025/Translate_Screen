import mss
import pytesseract
from PIL import Image, ImageTk, ImageOps, ImageFilter
from googletrans import Translator
import tkinter as tk
import time
import re
import difflib

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

class ScreenTranslator:
    def __init__(self):
        self.mss_instance = mss.mss()
        self.translator = Translator()
        self.buffer = ""
        self.next_update_time = 0

    def preprocess_image(self, pil_img):
        """Görüntüyü OCR için cam gibi yapar."""
        img = ImageOps.grayscale(pil_img) # Griye çevir
        img = ImageOps.autocontrast(img)  # Kontrastı patlat
        # Threshold: 160 değerinin altını siyah, üstünü beyaz yap (Net harfler)
        img = img.point(lambda p: 255 if p > 160 else 0)
        img = img.filter(ImageFilter.SHARPEN) # Keskinleştir
        return img

    def clean_text(self, text):
        """Garip karakterleri ( { [ | _ ) temizler."""
        cleaned = re.sub(r'[^a-zA-Z0-9\s.,!?\'"-]', '', text)
        return " ".join(cleaned.split())

    def calculate_display_time(self, text, is_lagging=False):
        if is_lagging: return 0.6
        return min(max(1.2 + (len(text) * 0.04), 1.5), 4.5)

    def find_overlap_and_stitch(self, new_text):
        if not self.buffer: return new_text
        s = difflib.SequenceMatcher(None, self.buffer, new_text)
        match = s.find_longest_match(0, len(self.buffer), 0, len(new_text))
        if match.size > 3:
            return self.buffer + new_text[match.b + match.size:]
        return self.buffer + " " + new_text

    def run(self):
        print("\n--- Ömer'in Akıllı Çeviri v2.6 (Kristal Mod) ---")
        print("1 - Normal Ekran Çevirisi")
        print("2 - YouTube Kusursuz Hafıza & Senkron Modu")
        secim = input("Seçim: ")
        selector = AreaSelector(); area = selector.get_selection()
        if not area or area["width"] < 10: return
        if secim == "1": self.normal_mode(area, selector.bg_img)
        else: self.live_mode(area)

    def normal_mode(self, area, full_img):
        img = full_img.crop((area["left"], area["top"], area["left"] + area["width"], area["top"] + area["height"]))
        text = self.clean_text(pytesseract.image_to_string(img))
        if text:
            tr = self.translator.translate(text, dest='tr')
            print(f"\n[TR]: {tr.text}")

    def live_mode(self, area):
        overlay = OverlayWindow(area)
        last_raw_text = ""
        
        print("Kusursuz Senkronizasyon Aktif. (Ctrl+C ile durdurun)")
        try:
            while True:
                sct_img = self.mss_instance.grab(area)
                raw_img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
                
                # ÖNCE TEMİZLE, SONRA OKU
                processed_img = self.preprocess_image(raw_img)
                current_raw = self.clean_text(pytesseract.image_to_string(processed_img, config='--psm 6'))
                
                if len(current_raw) < 3: # Çöp metinleri atla
                    overlay.root.update(); time.sleep(0.1); continue

                if current_raw and current_raw != last_raw_text:
                    last_raw_text = current_raw
                    self.buffer = self.find_overlap_and_stitch(current_raw)
                    sentences = re.findall(r'([^.!?]+[.!?])', self.buffer)
                    
                    if sentences:
                        num_sentences = len(sentences)
                        is_lagging = num_sentences > 2
                        
                        # --- AGRESİF SENKRONİZASYON ---
                        if is_lagging:
                            # Çok geriysek son iki cümleyi birleştir, eskileri çöpe at
                            to_translate = " ".join(sentences[-2:]).strip()
                            self.buffer = "" # Arkayı temizle ki yetişelim
                        else:
                            to_translate = sentences[0].strip()

                        if time.time() >= self.next_update_time or is_lagging:
                            try:
                                tr = self.translator.translate(to_translate, dest='tr')
                                overlay.update_text(tr.text)
                                
                                # Bekleme süresini ayarla
                                self.next_update_time = time.time() + self.calculate_display_time(tr.text, is_lagging)
                                
                                if not is_lagging:
                                    match = re.search(re.escape(to_translate), self.buffer)
                                    if match: self.buffer = self.buffer[match.end():].strip()
                            except: pass
                
                overlay.root.update()
                time.sleep(0.1) # Maksimum tarama hızı
        except:
            print("Kapatıldı.")

if __name__ == "__main__":
    app = ScreenTranslator()
    app.run()