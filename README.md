# 🎥 Active Translation Assistant
This project is a Python-based helper tool that captures text from a selected area on the screen (especially YouTube subtitles, in-game texts, or technical documents) in real time and translates it into Turkish.

## ​🤌🏼 Key Features

The project offers the user two different usage experiences:

* **Simple Mode (Stable):** A pure and reliable mode that avoids unnecessary processing load and directly translates the text it sees on the screen.
* **Advanced Mode:** An experimental mode that prevents delay (Lag Control) in fast-flowing videos, removes noise with image processing filters, and tries to preserve sentence integrity.

## 🛠️ Installation

Python must be installed on your system for the project to run.

1.  **Install Required Libraries:**
    ```bash
    pip install mss pytesseract Pillow googletrans==4.0.0-rc1
    ```

2.  **Install Tesseract OCR:**
    * Make sure the Tesseract engine is installed on your system.
    * [Tesseract OCR Download Page](https://github.com/UB-Mannheim/tesseract/wiki)
    * *Note: If you are using Windows, do not forget to add the Tesseract path to the system variables (PATH).*

## 💻 Usage

1.  Start the application with the command `python Translate.py`.
2.  Choose your mode on the screen that appears:
    * `1`: A calm and stable translation experience.
    * `2`: For fast-flowing videos and noisy (complex) backgrounds.
3.  Select the area you want to translate on the screen by dragging with your mouse.
4.  A transparent translation panel will open right below the selected area.
5.  **Exit:** You can terminate the process by pressing `Ctrl+C` in the terminal or pressing the `ESC` key while selecting the area.

## ⚙️ Technical Details

* **Screen Capture:** Taking screenshots with the `mss` library.
* **Text Recognition:** `pytesseract` (Google Tesseract OCR) engine.
* **Translation Engine:** `googletrans` API.
* **Interface:** Lightweight and transparent layer (Overlay) with `tkinter`.
* **Image Processing:** Increasing contrast and noise filtering using `Pillow` in advanced mode.

## ⚠️ Tip
For the best results, I recommend using **"Background Opacity: 100%"** and **"Edge Style: None"** options in YouTube subtitle settings. This way, the OCR engine will read the letters much more clearly.

---


# 🎥 Aktif Çeviri Asistanı
Bu proje, ekranda seçilen bir alandaki (özellikle YouTube altyazıları, oyun içi metinler veya teknik dökümanlar) metinleri anlık olarak yakalayıp Türkçeye çeviren, Python tabanlı bir yardımcı araçtır.



## ​🤌🏼 Öne Çıkan Özellikler



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
