# AI Real-Time Translator

![Python](https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python)
![EasyOCR](https://img.shields.io/badge/AI-EasyOCR-green?style=for-the-badge)
![CUDA](https://img.shields.io/badge/NVIDIA-CUDA%20Supported-orange?style=for-the-badge&logo=nvidia)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)

This project is a high-performance desktop tool that captures English text from a selected area on the screen (games, movies, videos, etc.) in real-time and translates it into Turkish using Deep Learning.

It is developed with a zero-latency goal using GPU support.

## 🚀 Key Features

* **EasyOCR Engine:** Unlike traditional OCR methods, it provides much more accurate character recognition using deep learning-based artificial intelligence.
* **Real-Time "Lag Saver" System:** Runs image capture and translation processes asynchronously (in separate channels) to avoid falling behind the video.
* **Turbo Film Mode:** A dynamic timing mechanism that quickly processes accumulated sentences to keep up with the screen flow.
* **Flexible Area Selection:** Select any part of the screen and let the AI handle the rest.
* **NVIDIA GPU Support:** Uses CUDA cores to run extremely fast without putting load on the CPU.

## 🛠️ Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/OmerFaruk025/Translate_Screen.git
    cd Translate_Screen
    ```

2.  **Create and activate a virtual environment (venv):**
    ```bash
    python -m venv venv
    
    # For Windows:
    venv\Scripts\activate
    # For Linux:
    source venv/bin/activate
    ```

3.  **Install required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## 🎮 Usage

1.  Start the application: `python Translate.py`
2.  Click the **SELECT AREA** button and mark the region on the screen you want to translate (such as subtitles).
3.  Choose your mode:
    * **Fast Mode:** Instant translation for short texts and menus.
    * **Film Mode:** Smart tracking for long dialogues and flowing videos.
4.  Press the **START** button and enjoy!

## 📦 Requirements

* Python 3.8+
* NVIDIA GPU (recommended for CUDA support)
* Active internet connection (for Google Translate API)

---
## Developed by **[Omer Faruk](https://github.com/OmerFaruk025)**






---







# AI Real-Time Translator

![Python](https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python)
![EasyOCR](https://img.shields.io/badge/AI-EasyOCR-green?style=for-the-badge)
![CUDA](https://img.shields.io/badge/NVIDIA-CUDA%20Supported-orange?style=for-the-badge&logo=nvidia)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)

Bu proje, ekranda seçilen belirli bir alandaki İngilizce metinleri (oyun, film, video vb.) gerçek zamanlı olarak yakalayan ve Deep Learning (Derin Öğrenme) kullanarak Türkçe'ye çeviren yüksek performanslı bir masaüstü aracıdır. GPU desteğiyle sıfır gecikme hedeflenerek geliştirilmiştir.

## 🚀 Öne Çıkan Özellikler

* **EasyOCR Motoru:** Geleneksel OCR yöntemlerinden farklı olarak, derin öğrenme tabanlı yapay zeka ile çok daha isabetli karakter tanıma.
* **Real-Time "Lag-Savar" Sistemi:** Görüntü yakalama ve çeviri işlemlerini asenkron (ayrı kanallarda) yürüterek videonun gerisinde kalmaz.
* **Turbo Film Modu:** Biriken cümleleri hızla eriterek ekran akışını yakalayan dinamik zamanlama mekanizması.
* **Esnek Alan Seçimi:** Ekranın istediğiniz kısmını seçin, gerisini AI halletsin.
* **NVIDIA GPU Desteği:** CUDA çekirdeklerini kullanarak CPU'yu yormadan mermi gibi çalışır.

## 🛠️ Kurulum

1.  **Depoyu klonlayın:**
    ```bash
    git clone https://github.com/OmerFaruk025/Translate_Screen.git
    cd Translate_Screen
    ```

2.  **Sanal ortam (venv) oluşturun ve aktif edin:**
    ```bash
    python -m venv venv
    
    # Windows için:
    venv\Scripts\activate
    # Linux için:
    source venv/bin/activate
    ```

3.  **Gerekli kütüphaneleri kurun:**
    ```bash
    pip install -r requirements.txt
    ```

## 🎮 Kullanım

1.  Uygulamayı başlatın: `python Translate.py`
2.  **ALAN SEÇ** butonuna tıklayarak ekranda çevrilmesini istediğiniz bölgeyi (altyazı alanı gibi) işaretleyin.
3.  Modunuzu seçin:
    * **Hızlı Mod:** Kısa metinler ve menüler için anlık çeviri.
    * **Film Modu:** Uzun diyaloglar ve akıcı videolar için akıllı takip.
4.  **BAŞLAT** butonuna basın ve keyfinize bakın!

## 📦 Gereksinimler

* Python 3.8+
* NVIDIA GPU (CUDA desteği için önerilir)
* Aktif internet bağlantısı (Google Translate API için)

---
## Developed by **[Omer Faruk](https://github.com/OmerFaruk025)**
