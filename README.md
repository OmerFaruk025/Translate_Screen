Bu proje, ekranda seçilen bir alandaki (özellikle YouTube altyazıları, oyun içi metinler veya teknik dökümanlar) metinleri anlık olarak yakalayıp Türkçeye çeviren, Python tabanlı bir yardımcı araçtır.

## 🚀 Öne Çıkan Özellikler

Proje, kullanıcıya iki farklı kullanım deneyimi sunar:

* **Basit Mod (Stabil):** Gereksiz işlem yükünden kaçınan, ekranda gördüğü metni doğrudan çeviren saf ve güvenilir mod.
* **Gelişmiş Mod:** Hızlı akan videolarda gecikmeyi önleyen (Lag Control), görüntü işleme filtreleri ile gürültüyü silen ve cümle bütünlüğünü korumaya çalışan deneysel mod.

## 🛠️ Kurulum

Projenin çalışması için sisteminizde Python yüklü olmalıdır.

1.  **Gerekli Kütüphaneleri Yükleyin:**
    ```bash
    pip install mss pytesseract Pillow googletrans==4.0.0-rc1
    ```

2.  **Tesseract OCR Yükleyin:**
    * Sisteminizde Tesseract motorunun yüklü olduğundan emin olun.
    * [Tesseract OCR İndirme Sayfası](https://github.com/UB-Mannheim/tesseract/wiki)
    * *Not: Windows kullanıyorsanız Tesseract yolunu sistem değişkenlerine (PATH) eklemeyi unutmayın.*

## 💻 Kullanım

1.  `python Translate.py` komutuyla uygulamayı başlatın.
2.  Gelen ekranda mod seçiminizi yapın:
    * `1`: Sakin ve stabil bir çeviri deneyimi.
    * `2`: Hızlı akan videolar ve gürültülü (karmaşık) arka planlar için.
3.  Ekranda çevrilmesini istediğiniz alanı farenizle sürükleyerek seçin.
4.  Seçilen alanın hemen altında şeffaf bir çeviri paneli açılacaktır.
5.  **Çıkış:** Terminalde `Ctrl+C` yaparak veya alanı seçerken `ESC` tuşuna basarak işlemi sonlandırabilirsiniz.

## ⚙️ Teknik Detaylar

* **Ekran Yakalama:** `mss` kütüphanesi ile ekran görüntüsü alma.
* **Metin Tanıma:** `pytesseract` (Google Tesseract OCR) motoru.
* **Çeviri Motoru:** `googletrans` API.
* **Arayüz:** `tkinter` ile hafif ve şeffaf katman (Overlay).
* **Görüntü İşleme:** Gelişmiş modda `Pillow` kullanarak kontrast artırma ve gürültü filtreleme.

## ⚠️ İpucu
En iyi sonuçlar için YouTube altyazı ayarlarından **"Arka Plan Opaklığı: %100"** ve **"Kenar Stili: Yok"** seçeneklerini kullanmanızı öneririm. Bu sayede OCR motoru harfleri çok daha net okuyacaktır.

---
*Developed with ☕ and Ömer Faruk*