import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# --- 1. SETUP PAGE & KUSTOMISASI CSS ---
st.set_page_config(page_title="Beijing Air Quality Dashboard", layout="wide")

# Menambahkan Kustomisasi CSS agar tampilan lebih premium
st.markdown("""
    <style>
    .main {background-color: #f4f6f9;}
    h1, h2, h3 {color: #2c3e50; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;}
    .stTabs [data-baseweb="tab-list"] {gap: 24px;}
    .stTabs [data-baseweb="tab"] {height: 50px; white-space: pre-wrap; background-color: transparent; border-radius: 4px 4px 0 0; gap: 1px; padding-top: 10px; padding-bottom: 10px;}
    .stTabs [aria-selected="true"] {background-color: #ffffff; border-bottom: 2px solid #3498db !important; color: #3498db !important; font-weight: bold;}
    </style>
""", unsafe_allow_html=True)

# --- 2. LOAD DATA DARI GOOGLE SHEETS ---
sheet_url = 'https://docs.google.com/spreadsheets/d/1RZE0ftms_d1CafbFMAdjAQoDGXqif18NNWqpUiJ2adk/export?format=csv'

@st.cache_data
def load_data(url):
    df = pd.read_csv(url)
    if 'datetime' in df.columns:
        df['datetime'] = pd.to_datetime(df['datetime'])
        df['date'] = df['datetime'].dt.date
        df['Hour'] = df['datetime'].dt.hour
        df['day_type'] = df['datetime'].dt.dayofweek.apply(lambda x: 'Weekend' if x >= 5 else 'Weekday')
    
    numeric_cols = ['PM2.5', 'PM10', 'SO2', 'NO2', 'CO', 'O3', 'TEMP', 'PRES', 'DEWP', 'RAIN', 'WSPM']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            
    # 3. Kategori Kualitas Udara (Otomatis)
    if 'Category' not in df.columns and 'PM2.5' in df.columns:
        conditions = [
            (df['PM2.5'] <= 12.0),
            (df['PM2.5'] > 12.0) & (df['PM2.5'] <= 35.4),
            (df['PM2.5'] > 35.4) & (df['PM2.5'] <= 150.4),
            (df['PM2.5'] > 150.4) & (df['PM2.5'] <= 250.4),
            (df['PM2.5'] > 250.4)
        ]
        choices = ["Good", "Moderate", "Unhealthy", "Very Unhealthy", "Hazardous"]
        # Impor numpy di paling atas file app.py jika belum ada: import numpy as np
        df['Category'] = np.select(conditions, choices, default="Unknown")
        
    return df

data = load_data(sheet_url)

# Mengatur urutan kategori kualitas udara
custom_category_order = ["Good", "Moderate", "Unhealthy for Sensitive Groups", "Unhealthy", "Very Unhealthy", "Hazardous"]

# Mengambil daftar kolom polutan dan cuaca secara dinamis
pollutant_parameters = ['PM2.5', 'PM10', 'SO2', 'NO2', 'CO', 'O3']
weather_parameters = ['TEMP', 'PRES', 'DEWP', 'RAIN', 'WSPM']


# --- 3. SIDEBAR (FILTERS) ---
with st.sidebar:
    st.image("performance_9858055.png", width=100)
    st.title('Filter Panel')
    
    selected_stations = st.multiselect('Pilih Stasiun', ['Semua Stasiun'] + list(data['station'].unique()), default=['Semua Stasiun'])
    
    col_date1, col_date2 = st.columns(2)
    with col_date1:
        start_date = st.date_input('Mulai', min(data['date']))
    with col_date2:
        end_date = st.date_input('Akhir', max(data['date']))
        
    st.markdown("---")
    st.caption("Data Analyst Project\nNur Aidah K.S. | ID Camp 2026")

# --- 4. LOGIKA FILTERING DATA ---
filtered_data = data.copy()
if selected_stations and 'Semua Stasiun' not in selected_stations:
    filtered_data = filtered_data[filtered_data['station'].isin(selected_stations)]

filtered_data = filtered_data[
    (filtered_data['date'] >= start_date) & 
    (filtered_data['date'] <= end_date)
]

# --- 5. MAIN DASHBOARD HEADER ---
st.title('Beijing Air Quality Dashboard')
st.markdown('Dashboard interaktif ini menyajikan analisis mendalam mengenai kualitas udara, tren musiman, dan komposisi polutan di 12 stasiun pemantauan Beijing (2013-2017).')

# -- HIGHLIGHT METRICS (KARTU ATAS) --
col1, col2, col3, col4 = st.columns(4)
col1.metric("Rata-rata PM2.5", f"{filtered_data['PM2.5'].mean():.2f} µg/m³", help="Partikel sangat halus yang berbahaya bagi pernapasan.")
col2.metric("Rata-rata PM10", f"{filtered_data['PM10'].mean():.2f} µg/m³", help="Partikel kasar di udara.")
col3.metric("Rata-rata NO2", f"{filtered_data['NO2'].mean():.2f} µg/m³", help="Gas indikator emisi kendaraan bermotor.")
col4.metric("Total Data Perekaman", f"{len(filtered_data):,}", help="Jumlah baris data setelah difilter.")

st.markdown("---")

# --- 6. SISTEM TABS (NAVIGASI UI) ---
tab1, tab2, tab3 = st.tabs(["Analisis Tren & Waktu", "Analisis Wilayah & Stasiun", "Kategori Kualitas Udara"])

# ================= TAB 1: TREN & WAKTU =================
with tab1:
    st.header("Analisis Tren Berdasarkan Waktu")
    
    # Pertanyaan 1
	#Tren Interaktif (Line Chart)
    st.subheader("Tren Kualitas Udara & Pola Waktu")
    
    col_filter1, col_filter2 = st.columns(2)
    with col_filter1:
        # Filter Resolusi Waktu
        freq_options = {'Bulanan': 'ME', 'Tahunan': 'YE'} # ME = Month End, YE = Year End
        selected_freq = st.selectbox('Pilih Resolusi Waktu:', list(freq_options.keys()))
    with col_filter2:
        # Filter Jenis Polutan
        pol_options = ['PM2.5', 'PM10']
        sel_pol = st.selectbox('Pilih Parameter Polutan:', pol_options)
        
    # Proses pengelompokan (resampling) data berdasarkan filter interaktif
    resampled_df = filtered_data.groupby(['station', pd.Grouper(key='datetime', freq=freq_options[selected_freq])])[sel_pol].mean().reset_index()
    
    # Visualisasi Line Chart Plotly
    fig_line_trend = px.line(resampled_df, x='datetime', y=sel_pol, color='station', markers=True,
                             color_discrete_sequence=px.colors.qualitative.Set2)
    fig_line_trend.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                                 xaxis_title="Waktu", yaxis_title=f"Konsentrasi {sel_pol} (µg/m³)",
                                 legend_title_text='Stasiun')
    st.plotly_chart(fig_line_trend, use_container_width=True)
    
    with st.expander("Lihat Penjelasan Insight Tren Kualitas Udara"):
        st.write("Berdasarkan Tren Polusi Udara (PM2.5 dan PM10) di Beijing yang digambarkan dengan line chart, terlihat bahwa polusi PM2.5 dan PM10 menunjukan pola siklus yang berulang. Hal ini terlihat dari adanya pola gunung dan lembah yang konsisten. Contohnya lonjokan polusi atau pola gunung terjadi di 2016-01 dan 2017-01. selain itu pola lembah terjadi di 2015-07 dan 2016-07.")

    st.markdown("<br>", unsafe_allow_html=True) # Spasi


    st.subheader("Pola Musiman: Rata-rata Polusi per Bulan")
    monthly_trend = filtered_data.groupby(filtered_data['datetime'].dt.month)[['PM2.5', 'PM10']].mean().reset_index()
    monthly_trend.columns = ['Bulan', 'PM2.5', 'PM10']
    
    fig_month = px.bar(monthly_trend, x='Bulan', y=['PM2.5', 'PM10'], barmode='group',
                       color_discrete_sequence=['#ff4b4b', '#ffb44b'])
    fig_month.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", 
                            xaxis=dict(tickmode='linear', tick0=1, dtick=1), legend_title_text='Jenis Polutan')
    st.plotly_chart(fig_month, use_container_width=True)
    
    with st.expander("Lihat Penjelasan Insight Musiman"):
        st.write("Berdasarkan grafik pola musiman menunjukkan bahwa rata-rata polusi berdasarkan bulan yang digambarkan dengan bar chart menunjukan bahwa terjadi pola musiman dan terdapat lonjakan polusi. contohnya konsentrasi polutan memuncak pada bulan Oktober hingga Maret, dengan bulan Desember dan Maret sebagai titik terparah. Secara iklim, ini adalah periode Musim Dingin (Winter) di Tiongkok. Selain itu, kualitas udara mencapai titik terendah pada pertengahan tahun, khususnya di bulan Agustus (bulan 8). Pada musim panas, suhu udara yang lebih panas membuat partikel polusi lebih mudah menyebar ke atmosfer atas. Tambahan pula, kecepatan angin yang lebih tinggi di musim panas membantu mengurangi debu polusi dari udara.")

    st.markdown("<br>", unsafe_allow_html=True) # Spasi

    # Pertanyaan 2
    #LINE Chart
    st.subheader("Pola Harian: Hari Kerja vs Akhir Pekan")
    hourly_day_pattern = filtered_data.groupby(['Hour', 'day_type'])['PM2.5'].mean().reset_index()
    
    fig_hourly = px.line(hourly_day_pattern, x='Hour', y='PM2.5', color='day_type', markers=True,
                         color_discrete_sequence=['#2980b9', '#e74c3c'])
    fig_hourly.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                             xaxis_title="Jam (00:00 - 23:00)", yaxis_title="Konsentrasi PM2.5",
                             xaxis=dict(tickmode='linear', tick0=0, dtick=1), legend_title_text='Tipe Hari')
    st.plotly_chart(fig_hourly, use_container_width=True)
    
    with st.expander("Lihat Penjelasan Insight Pola Harian"):
        st.write("Berdasarkan grafik rata-rata pergerakan PM2.5 per jam, terbentuk pola U-shape baik pada hari kerja maupun akhir pekan. Titik terendah pada sore hari pukul 15.00-16.00 dan titik tertinggi terjadi pada dini hari pukul 21.00-02.00. \nGaris merah (Weekend) secara konsisten berada di atas garis biru (Weekday) pada hampir setiap jam. Artinya, kualitas udara di akhir pekan rata-rata selalu lebih buruk dibandingkan hari kerja biasa. Akhir pekan seringkali berarti mobilitas yang jauh lebih tinggi dan menyebar untuk rekreasi, hiburan, dan liburan keluarga. Kemacetan mungkin berpindah dari kawasan perkantoran ke pusat perbelanjaan atau tempat wisata sepanjang hari. \nGaris merah di jam 00:00 hingga 01:00 (tengah malam). Lonjakan polusinya sangat tinggi (di atas 90 µg/m³). Ini mengindikasikan tingginya aktivitas rekreasi malam (nightlife) atau kepadatan lalu lintas orang-orang yang pulang larut malam pada hari Jumat/Sabtu malam dibandingkan hari biasa.")

    #HEATMAP
    st.subheader("Heatmap Polusi Udara PM2.5: Jam vs Hari")
    
    # 1. Menyiapkan data
    df_time = filtered_data.copy()
    df_time['hour'] = df_time['datetime'].dt.hour
    df_time['day_name'] = df_time['datetime'].dt.day_name()
    
    # 2. Membuat Pivot (Langsung menggunakan 'PM2.5' secara spesifik)
    pivot_time = df_time.pivot_table(values='PM2.5', index='day_name', columns='hour', aggfunc='mean')
    days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    pivot_time = pivot_time.reindex(days_order)
    
    # 3. Membuat Plotting
    fig_heat, ax_heat = plt.subplots(figsize=(12, 5))
    sns.heatmap(pivot_time, cmap='RdBu_r', annot=False, ax=ax_heat, 
                cbar_kws={'label': 'Rata-rata PM2.5'})
    
    ax_heat.set_xlabel('Jam dalam Sehari (00:00 - 23:00)')
    ax_heat.set_ylabel('Hari')
    ax_heat.tick_params(axis='y', rotation=0)
    
    # 4. Menampilkan di Streamlit
    st.pyplot(fig_heat)

    with st.expander("Lihat Penjelasan Insight Pola Harian"):
        st.write("""Heatmap pola jam vs hari menunjukkan bahwa semakin merah maka semakin tinggi polusi dan semakin biru blok maka semakin rendah polusi. Pada hari Jumat (Friday), Sabtu (Saturday), dan Minggu (Sunday). Area berwarna merah paling gelap (konsentrasi PM2.5 mencapai >95 µg/m³) sangat pekat dan menumpuk pada malam hari (pukul 20:00 - 23:00) hingga berlanjut ke dini hari (pukul 00:00 - 02:00). Berkebalikan dengan akhir pekan, hari Senin (Monday) hingga Rabu (Wednesday) memiliki area biru gelap yang cukup luas, terutama pada siang hingga sore hari. Di hampir semua hari kecuali Saturday terdapat pola vertikal di mana rentang waktu pukul 13:00 hingga 16:00 didominasi oleh warna biru/terang.""")

# ================= TAB 2: WILAYAH & STASIUN =================
#Pertanyaan 3
with tab2:
    st.header("Perbandingan Antar Wilayah Berdasarkan Stasiun)")
    
    col_t2_1, col_t2_2 = st.columns(2)
    
    with col_t2_1:
        st.subheader("Peringkat Stasiun Terkotor Indikator Konsentrasi PM2.5")
        station_rank = filtered_data.groupby('station')['PM2.5'].mean().sort_values(ascending=True).reset_index()
        fig_rank = px.bar(station_rank, x='PM2.5', y='station', orientation='h',
                          color='PM2.5', color_continuous_scale='Reds')
        fig_rank.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", yaxis_title="")
        st.plotly_chart(fig_rank, use_container_width=True)

    with col_t2_2:
     st.subheader("Komposisi Gas (SO2, NO2, O3)")
     gas_comp = filtered_data.groupby('station')[['SO2', 'NO2', 'O3']].mean().reset_index()
     fig_gas = px.bar(gas_comp, x='station', y=['SO2', 'NO2', 'O3'], barmode='group',
                      color_discrete_sequence=['#d35400', '#f39c12', '#3498db'])
     fig_gas.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", 
                           xaxis_title="", legend_title_text='Gas')
     st.plotly_chart(fig_gas, use_container_width=True)

    with st.expander("Lihat Penjelasan Insight Perbandingan Antar Wilayah"):
        st.write('''Dari grafik Peringkat Stasiun, terlihat jelas adanya ketimpangan kualitas udara antar wilayah. Stasiun dengan kualitas udara terburuk terletak di Dongsi, Wanshouxigong, dan Nongzhanguan menempati posisi puncak dengan kadar rata-rata PM2.5 tertinggi (di atas 80 µg/m³). Stasiun-stasiun ini umumnya terletak di kawasan pusat kota Beijing yang sangat padat. Stasiun dengan kulitas udara yang baik seperti di Dingling, Huairou, dan Changping mencatat tingkat PM2.5 terendah (berkisar di angka 60-70 µg/m³). Wilayah-wilayah ini berada di area pinggiran (suburban) bagian utara atau dekat pegunungan yang jauh lebih asri dan berjarak dari pusat industri.
                 Pada grafik Komposisi Polutan Gas di Setiap Stasiun, perhatikan batang berwarna oranye (NO2). Stasiun-stasiun dengan udara yang kotor (seperti Wanliu, Nongzhanguan, dan Dongsi) memiliki kadar gas Nitrogen Dioksida (NO2) yang mendominasi. Karena NO2 adalah gas buang utama dari knalpot kendaraan bermotor, tingginya angka ini mengkonfirmasi bahwa kemacetan lalu lintas perkotaan adalah salah satu kontributor utama buruknya kualitas udara di wilayah tersebut.
                 Grafik polutan konsentrasi zat Ozon yang terbaik. Stasiun seperti Dingling dan Huairou memiliki konsentrasi PM2.5 dan NO2 yang rendah, namun kadar gas O3(batang berwarna biru) berada di titik tertinggi. Hal ini terjadi karena ozon di perkotaan bereaksi dengan Nitrogen Oksida sisa pembuangan kendaraan bermotor dan industri (proses scavenging atau tirasi), sehingga konsentrasi ozon berkurang secara lokal. Sebaliknya, di daerah pinggiran seperti Dingling yang jarang dilewati kendaraan, ozon dapat terakumulasi secara alami di siang hari tanpa ada banyak emisi gas buang yang menetralkannya.''')
# ================= TAB 3: KESIMPULAN & PROPORSI =================
with tab3:
    st.header("Proporsi Kategori Udara & Kesimpulan Akhir")
    
   
    
    st.subheader("Proporsi Kategori Kualitas Udara (PM2.5)")
        
    # Menghitung jumlah per kategori dari data yang difilter
    category_counts = filtered_data['Category'].value_counts().reset_index()
    category_counts.columns = ['Category', 'Count']
        
    # Menyiapkan warna standar untuk setiap kategori AQI agar lebih profesional
    color_map = {
        "Good": "#a8e6cf",                       # Hijau Pastel
        "Moderate": "#ffd3b6",                   # Oranye Pastel
        "Unhealthy for Sensitive Groups": "#ffaaa5", # Merah Muda Pastel
        "Unhealthy": "#ff8b94",                  # Merah Pastel
        "Very Unhealthy": "#dcedc1",             # Hijau Zaitun/Kuning
        "Hazardous": "#c3aed6",                  # Ungu Pastel
        "Unknown": "#d5d5d5"                     # Abu-abu
    }
        
    # Membuat Pie Chart
    fig_pie = px.pie(category_counts, values='Count', names='Category',
                     color='Category', color_discrete_map=color_map,
                     hole=0.1) # Memberikan sedikit lubang di tengah agar modern
        
    fig_pie.update_traces(textposition='inside', textinfo='percent+label')
    fig_pie.update_layout(showlegend=False, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", margin=dict(t=0, b=0, l=0, r=0))
    st.plotly_chart(fig_pie, use_container_width=True)
        
    with st.expander("Lihat Penjelasan Insight Proporsi Kategori"):
        st.write("""Berdasarkan grafik Proporsi Kategori Udara menggambarkan bahwa polusi udara adalah masalah konstan di Beijing. Mayoritas waktu yang terekam dihabiskan pada kategori Unhealthy (Tidak Sehat) sebesar 47.4% & Moderate (Sedang) sebesar 22.1%. Persentase kualitas udara yang Good (Baik) cukup rendah berada di peringkat ke-3 sebesar 15,2%, menunjukkan bahwa warga kota terus-menerus terpapar risiko kesehatan tingkat menengah hingga tinggi sepanjang tahun.
        """)
        
    st.markdown("<hr>", unsafe_allow_html=True) # Garis Pemisah
    
    # Bagian Penutup / Kesimpulan
    st.header("Kesimpulan (Conclution)")
    st.success("""
    Berdasarkan seluruh analisis data historis kualitas udara Beijing (2013-2017), berikut kesimpulan yang dapat diambil:
    
    1. Tren kualitas Udara dengan indikator PM2.5 dan PM10 menunjukkan pola musiman yang konsisten dalam beberapa tahun. Tingkat polusi udara selalu mencapai titik terburuknya pada bulan-bulan musim dingin (Desember, Januari, Februari, Maret) dan menyentuh titik terendah (paling bersih) pada musim panas (Agustus). Lonjakan tinggi di musim dingin utamanya disebabkan oleh peningkatan masif pembakaran batu bara untuk sistem pemanas di wilayah Beijing. Selain itu, cuaca musim dingin seringkali menciptakan fenomena inversi termal di mana udara dingin di dekat tanah memerangkap asap polusi sehingga tidak bisa terbang ke atas.
    2. Dalam satu hari, udara cenderung paling bersih pada sore hari (pukul 15:00 - 16:00), dan secara konsisten mulai memburuk sejak malam hari hingga mencapai puncaknya pada tengah malam/dini hari. Pola polusi harian membentuk pola U-shape baik pada hari kerja maupun akhir pekan. Dengan konsentrasi PM2.5 akhir pekan yang selalu berada di atas hari kerja hampir setiap jam. tingginya polusi di akhir pekan kemungkinan didorong mobilitas yang jauh lebih tinggi dan menyebar untuk rekreasi, hiburan, dan liburan keluarga. Kemacetan mungkin berpindah dari kawasan perkantoran ke pusat perbelanjaan atau tempat wisata sepanjang hari.
    3. Stasiun Dongsi, Wanshouxigong dan Nongzhanguan menempati urutan teratas sebagai wilayah dengan kualitas udara terburuk (PM2.5 tertinggi). Sebaliknya, stasiun Dingling dan Huairou memiliki catatan kualitas udara terbaik (PM2.5 terendah). Dalam grafik komposisi polutan gas, stasiun yang kualitas udaranya buruk juga memiliki rata-rata gas Nitrogen Dioksida (NO2) yang jauh lebih tinggi dibandingkan stasiun yang kualitas udaranya bersih. Dongsi, Wanshouxigong dan Nongzhanguan terletak di kawasan pusat kota Beijing yang sangat padat dengan aktivitas urban dan kemacetan, terbukti dari tingginya kadar NO2 (yang merupakan gas buang utama dari knalpot kendaraan bermotor). Sementara itu, Dingling dan Huairou terletak di wilayah pegunungan/suburban utara Beijing, jauh dari kawasan industri dan kepadatan lalu lintas.
    """)