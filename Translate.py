import mss
import pytesseract
from PIL import Image, ImageTk
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
        self.next_update_time = 0 # Yeni çeviri için beklenen minimum zaman

    def calculate_display_time(self, text, is_lagging=False):
        """Metnin uzunluğuna ve lag durumuna göre kalma süresi belirler."""
        base_time = 1.2 # Minimum kalma süresi
        char_bonus = len(text) * 0.04 # Her harf için 0.04 saniye ekle
        
        total_time = base_time + char_bonus
        
        # Eğer arkada birikmiş cümleler varsa süreyi %50 kısalt ki yetişelim
        if is_lagging:
            total_time *= 0.5
            
        return min(total_time, 4.5) # Ne olursa olsun bir cümle 4.5 saniyeden fazla kalmasın

    def find_overlap_and_stitch(self, new_text):
        if not self.buffer: return new_text
        s = difflib.SequenceMatcher(None, self.buffer, new_text)
        match = s.find_longest_match(0, len(self.buffer), 0, len(new_text))
        if match.size > 3:
            return self.buffer + new_text[match.b + match.size:]
        else:
            return self.buffer + " " + new_text

    def run(self):
        print("\n--- Ömer'in Akıllı Çeviri Asistanı v2.4 ---")
        print("1 - Normal Ekran Çevirisi")
        print("2 - YouTube Kusursuz Hafıza Modu (Akıllı Zamanlama)")
        secim = input("Seçim (1/2): ")
        
        selector = AreaSelector()
        area = selector.get_selection()
        if not area or area["width"] < 10: return
        if secim == "1": self.normal_mode(area, selector.bg_img)
        else: self.live_mode(area)

    def normal_mode(self, area, full_img):
        img = full_img.crop((area["left"], area["top"], area["left"] + area["width"], area["top"] + area["height"]))
        text = pytesseract.image_to_string(img).strip()
        if text:
            tr = self.translator.translate(text, dest='tr')
            print(f"\n[TR]: {tr.text}")

    def live_mode(self, area):
        overlay = OverlayWindow(area)
        last_raw_text = ""
        
        try:
            while True:
                sct_img = self.mss_instance.grab(area)
                img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
                current_raw = " ".join(pytesseract.image_to_string(img).strip().split())
                
                if current_raw and current_raw != last_raw_text:
                    last_raw_text = current_raw
                    self.buffer = self.find_overlap_and_stitch(current_raw)
                    
                    # Bitmiş tüm cümleleri bul
                    sentences = re.findall(r'([^.!?]+[.!?])', self.buffer)
                    
                    if sentences:
                        # LAG KONTROLÜ: Eğer kumbarada 1'den fazla cümle varsa geri kalıyoruz demektir
                        is_lagging = len(sentences) > 1
                        
                        # Eğer güncelleme vaktimiz geldiyse veya çok geri kaldıysak hemen bas
                        if time.time() >= self.next_update_time or len(sentences) > 2:
                            # İlk biten cümleyi al (FIFO mantığı - İlk giren ilk çıkar)
                            full_sentence = sentences[0].strip()
                            
                            try:
                                tr = self.translator.translate(full_sentence, dest='tr')
                                overlay.update_text(tr.text)
                                
                                # Bir sonraki cümle için "bekleme süresi" ata
                                display_duration = self.calculate_display_time(tr.text, is_lagging)
                                self.next_update_time = time.time() + display_duration
                                
                                # Hafızadan sadece bu cümleyi sil
                                match = re.search(re.escape(full_sentence), self.buffer)
                                if match:
                                    self.buffer = self.buffer[match.end():].strip()
                            except: pass
                
                overlay.root.update()
                time.sleep(0.3)
        except:
            print("Canlı mod durduruldu.")

if __name__ == "__main__":
    app = ScreenTranslator()
    app.run()