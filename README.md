
# Beijing Air Quality Dashboard - Dicoding / IDCamp 2026

![Air Quality Dashboard](dashboard.gif)

[Air Quality Dashboard Streamlit App](https://air-quality-dashboard-idcamp-nuraidah.streamlit.app/)

## Daftar Isi
- [Deskripsi Proyek](#deskripsi-proyek)
- [Struktur Proyek](#struktur-proyek)
- [Instalasi](#instalasi)
- [Cara Penggunaan](#cara-penggunaan)
- [Sumber Data](#sumber-data)
- [Analisis Data Eksploratif (EDA)](#analisis-data-eksploratif-eda)
- [Visualisasi Dashboard](#visualisasi-dashboard)
- [Kredit](#kredit)

## Deskripsi Proyek
Proyek ini merupakan analisis data dan visualisasi yang berfokus pada kualitas udara dari 12 stasiun pemantauan di Beijing (2013-2017). Proyek ini mencakup proses persiapan data (*data wrangling*) yang komprehensif, *Exploratory Data Analysis* (EDA) menggunakan teknik lanjutan seperti *binning* dan visualisasi distribusi tingkat lanjut (*Boxplot* & *Violin Plot*), serta pembuatan *dashboard* interaktif menggunakan Streamlit. Tujuannya adalah untuk memberikan *insight* yang dapat ditindaklanjuti terkait pola polusi musiman, dampak kondisi cuaca, dan ketimpangan kualitas udara secara geografis.

## Struktur Proyek
- `dashboard/`: Berisi file aplikasi utama (`dashboard.py`) dan dataset bersih yang digunakan untuk *dashboard* Streamlit.
- `data/`: Direktori yang berisi file data mentah (CSV) dari 12 stasiun pemantauan.
- `notebook.ipynb`: File Jupyter/Google Colab Notebook yang berisi tahapan lengkap mulai dari pengumpulan data (*gathering*), penilaian (*assessing*), pembersihan (*cleaning*), hingga analisis data eksploratif (EDA).
- `requirements.txt`: Daftar pustaka (*library*) Python yang dibutuhkan untuk menjalankan proyek ini.
- `README.md`: File dokumentasi ini.
- `url.txt`: Berisi tautan (*link*) aktif menuju *dashboard* Streamlit yang telah di-*deploy*.

## Instalasi
1. Setup Environment - Anaconda
```bash
conda create --name main-ds python=3.9
conda activate main-ds
pip install -r requirements.txt

```

2. Setup Environment - Shell/Terminal

```bash
mkdir air-quality-dashboard
cd air-quality-dashboard
pipenv install
pipenv shell
pip install -r requirements.txt

```

3. Run streamlit app

```bash
streamlit run dashboard.py

```
Akses dashboard melalui web browser Anda, biasanya pada tautan http://localhost:8501.

## Sumber Data
Proyek ini menggunakan dataset PRSA (Beijing Multi-Site Air-Quality Data) yang disediakan dalam kelas "Belajar Analisis Data dengan Python" oleh Dicoding. (https://drive.google.com/file/d/1RhU3gJlkteaAQfyn9XOVAz7a5o1-etgr/view)

## Analisis Data Eksploratif (EDA)
Proyek ini mengimplementasikan tahapan EDA yang komprehensif (Univariate, Multivariate, Temporal, Numerikal, dan Kategorikal) untuk menggali insight mendalam:
1. Analisis Distribusi (Univariate & Numerikal)
Visualisasi Histogram, KDE, dan Q-Q Plot membuktikan bahwa data polutan (PM2.5, PM10) tidak berdistribusi normal. Analisis Skewness dan Kurtosis menunjukkan distribusi yang Right-Skewed dan Leptokurtic (sangat runcing), mengindikasikan frekuensi terjadinya anomali/lonjakan polusi ekstrem (outlier) yang sangat tinggi di Beijing.

2. Korelasi Cuaca (Multivariate)
Melalui Correlation Matrix Heatmap, Pairplot, dan Scatter Plot yang dilengkapi garis regresi, ditemukan korelasi linear negatif yang kuat antara Kecepatan Angin (WSPM) dan PM2.5. Angin bertindak sebagai pembersih alami yang efektif.

3. Pola Temporal (Musiman & Harian)
Boxplot dan Violin Plot bulanan mengungkap bahwa musim dingin (Oktober-Februari) memiliki varian polusi yang paling ekstrem akibat pemanas batu bara. Sementara itu, analisis *Heatmap* jam vs hari membuktikan bahwa akhir pekan mencatat rata-rata polusi malam hari yang lebih tinggi (pukul 20:00 - 02:00) dibandingkan hari kerja.

4. Uji Signifikansi (Kategorikal)
Berdasarkan pengujian statistik Chi-Square antara lokasi stasiun dan kategori kualitas udara hasil binning, didapatkan p-value < 0.05. Hal ini membuktikan secara absolut bahwa faktor geografis/lokasi stasiun memiliki pengaruh yang sangat signifikan terhadap tingkat keparahan polusi udara.

## Visualisasi Dashboard
Dashboard Streamlit menyediakan antarmuka interaktif untuk mengeksplorasi:

1. Garis tren deret waktu untuk konsentrasi polutan bulanan dan tahunan

2. Pola polusi harian dengan filter Hari Kerja (Weekday) dan Akhir Pekan (Weekend), dilengkapi Heatmap distribusi jam vs hari.

3. Analisis perbandingan geografis dari 12 stasiun (Pusat Kota vs Pinggiran) dan komposisi polutan (SO2, NO2 dan O3).

4. Proporsi kategori Indeks Kualitas Udara (AQI) menggunakan Pie Chart.

## Kredit
Proyek ini dikembangkan sebagai tugas akhir untuk kelas "Belajar Analisis Data dengan Python" di Dicoding Academy (IDCamp). Terima kasih khusus kepada Dicoding Academy karena telah menyediakan sumber daya, panduan, dan platform pembelajaran yang luar biasa.
