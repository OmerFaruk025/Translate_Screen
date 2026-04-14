import mss
import pytesseract
from PIL import Image, ImageTk
from googletrans import Translator
import tkinter as tk
import time
import threading

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
        left, top = min(self.start_x, end_x), min(self.start_y, end_y)
        width, height = abs(self.start_x - end_x), abs(self.start_y - end_y)
        self.selection = {"top": top, "left": left, "width": width, "height": height}
        self.root.destroy()

    def get_selection(self):
        self.root.mainloop()
        return self.selection

class OverlayWindow:
    """Çeviriyi ekranda gösterecek şeffaf panel"""
    def __init__(self, area):
        self.root = tk.Tk()
        self.root.overrideredirect(True) # Çerçevesiz pencere
        self.root.attributes("-topmost", True)
        self.root.attributes("-alpha", 0.8) # Hafif şeffaf
        
        # Seçilen alanın hemen altına yerleştir
        x = area["left"]
        y = area["top"] + area["height"] + 10
        self.root.geometry(f"{area['width']}x60+{x}+{y}")
        
        self.label = tk.Label(self.root, text="Başlatılıyor...", fg="white", bg="#1e1e1e", 
                              font=("Arial", 12, "bold"), wraplength=area["width"]-10)
        self.label.pack(fill="both", expand=True)

    def update_text(self, text):
        self.label.config(text=text)
        self.root.update()

class ScreenTranslator:
    def __init__(self):
        self.mss_instance = mss.mss()
        self.translator = Translator()
        self.is_running = True

    def run(self):
        print("Çevrilecek alanı seçin (ESC: İptal)...")
        selector = AreaSelector()
        area = selector.get_selection()

        if not area or area["width"] < 10:
            print("Seçim geçersiz.")
            return

        overlay = OverlayWindow(area)
        last_text = ""

        print("Canlı takip moduna geçildi. Çıkmak için terminali kapatın.")
        
        try:
            while self.is_running:
                # 1. Alanı yakala
                sct_img = self.mss_instance.grab(area)
                img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
                
                # 2. OCR yap
                raw_text = pytesseract.image_to_string(img).strip()
                
                # 3. Metin değiştiyse çevir
                if raw_text and raw_text != last_text:
                    try:
                        # Gereksiz boşlukları temizle
                        clean_text = " ".join(raw_text.split())
                        translation = self.translator.translate(clean_text, dest='tr')
                        overlay.update_text(translation.text)
                        last_text = raw_text
                    except Exception as e:
                        print(f"API Hatası: {e}")
                
                overlay.root.update()
                time.sleep(0.5) # İşlemciyi yormayalım
                
        except (tk.TclError, KeyboardInterrupt):
            print("Canlı mod sonlandırıldı.")

if __name__ == "__main__":
    app = ScreenTranslator()
    app.run()