import mss
import pytesseract
from PIL import Image, ImageTk
from googletrans import Translator
import tkinter as tk

class AreaSelector:
    def __init__(self):
        self.root = tk.Tk()
        self.root.attributes('-fullscreen', True)
        self.root.attributes("-topmost", True)
        
        # 1. ADIM: Ekranın o anki görüntüsünü al (Hileyi burada yapıyoruz)
        with mss.mss() as sct:
            screenshot = sct.grab(sct.monitors[1]) # Ana ekranı yakala
            self.bg_img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
            self.tk_bg_img = ImageTk.PhotoImage(self.bg_img)

        # 2. ADIM: Bu görüntüyü arka plana koy
        self.canvas = tk.Canvas(self.root, cursor="cross", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.create_image(0, 0, anchor="nw", image=self.tk_bg_img)
        
        # Ekranı biraz karartmak için üzerine yarı şeffaf bir siyah katman atalım
        self.canvas.create_rectangle(0, 0, self.root.winfo_screenwidth(), self.root.winfo_screenheight(), fill="black", stipple="gray50")

        self.start_x = None
        self.start_y = None
        self.rect = None
        self.selection = None

        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_move_press)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)
        self.root.bind("<Escape>", lambda e: self.root.destroy())

    def on_button_press(self, event):
        self.start_x, self.start_y = event.x, event.y
        if self.rect: self.canvas.delete(self.rect)
        self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, 1, 1, outline='red', width=3)

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

class ScreenTranslator:
    def __init__(self):
        self.mss_instance = mss.mss()
        self.translator = Translator()

    def run(self):
        print("Çevrilecek alanı seçin (ESC: İptal)...")
        selector = AreaSelector()
        area = selector.get_selection()

        if area and area["width"] > 5:
            # Seçilen koordinatlara göre kırpma yapıyoruz
            img = selector.bg_img.crop((area["left"], area["top"], area["left"] + area["width"], area["top"] + area["height"]))
            
            raw_text = pytesseract.image_to_string(img)
            if raw_text.strip():
                print(f"\n[Orijinal]:\n{raw_text.strip()}")
                try:
                    translation = self.translator.translate(raw_text, dest='tr')
                    print("-" * 30 + f"\n[Türkçe]:\n{translation.text}\n" + "-" * 30)
                except Exception as e:
                    print(f"Çeviri hatası: {e}")
            else:
                print("Metin bulunamadı.")

if __name__ == "__main__":
    app = ScreenTranslator()
    app.run()