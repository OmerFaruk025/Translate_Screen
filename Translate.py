import mss
import pytesseract
from PIL import Image, ImageTk
from googletrans import Translator
import tkinter as tk
import time
import re

# AreaSelector sınıfı aynı kalıyor (O kısım zaten kusursuz)
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
        self.label = tk.Label(self.root, text="Altyazı bekleniyor...", fg="#00FF00", bg="#121212", 
                              font=("Verdana", 11, "bold"), wraplength=area["width"]-20, justify="center")
        self.label.pack(fill="both", expand=True)

    def update_text(self, text):
        self.label.config(text=text)
        self.root.update()

class ScreenTranslator:
    def __init__(self):
        self.mss_instance = mss.mss()
        self.translator = Translator()

    def run(self):
        print("\n--- Ömer'in Çeviri Asistanı v2.1 ---")
        print("1 - Normal Ekran Çevirisi (Tek seferlik)")
        print("2 - YouTube Canlı Altyazı Modu (Akıllı Çeviri)")
        secim = input("Seçiminizi yapın (1/2): ")

        selector = AreaSelector()
        area = selector.get_selection()
        if not area or area["width"] < 10: return

        if secim == "1":
            self.normal_mode(area, selector.bg_img)
        else:
            self.live_mode(area)

    def normal_mode(self, area, full_img):
        img = full_img.crop((area["left"], area["top"], area["left"] + area["width"], area["top"] + area["height"]))
        text = pytesseract.image_to_string(img).strip()
        if text:
            tr = self.translator.translate(text, dest='tr')
            print(f"\n[Orijinal]: {text}\n{'-'*20}\n[Türkçe]: {tr.text}")

    def live_mode(self, area):
        overlay = OverlayWindow(area)
        last_full_text = "" # Ekranda o an gördüğümüz tüm metin
        
        print("Canlı takip aktif. Çıkmak için terminalde Ctrl+C yapın.")
        try:
            while True:
                sct_img = self.mss_instance.grab(area)
                img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
                
                # OCR metni al ve tek satıra indir
                current_raw = pytesseract.image_to_string(img).strip()
                current_raw = " ".join(current_raw.split()) 
                
                # Eğer ekrandaki metin değiştiyse işlemlere başla
                if current_raw and current_raw != last_full_text:
                    last_full_text = current_raw
                    
                    # Cümle bitiş işaretlerine göre böl (. ! ?)
                    # Bu regex, işaretleri cümlenin sonunda tutarak böler
                    sentences = re.findall(r'[^.!?]+[.!?]?', current_raw)
                    
                    if sentences:
                        # En son biten cümleyi bul (Noktalama ile biten son tam parça)
                        last_complete = ""
                        for s in reversed(sentences):
                            if any(mark in s for mark in ".!?"):
                                last_complete = s.strip()
                                break
                        
                        # Eğer bitmiş yeni bir cümle bulduysak ve bu bir öncekiyle aynı değilse çevir
                        if last_complete:
                            try:
                                tr = self.translator.translate(last_complete, dest='tr')
                                # ESKİSİNİ SİL: Sadece bu son cümleyi ekranda göster
                                overlay.update_text(tr.text)
                            except Exception as e:
                                print(f"Çeviri hatası: {e}")
                
                overlay.root.update()
                time.sleep(0.4)
        except Exception as e:
            print(f"Canlı mod kapatıldı: {e}")

if __name__ == "__main__":
    app = ScreenTranslator()
    app.run()