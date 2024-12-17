import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import streamlit as st
import plotly.express as px
import pandas as pd
from datetime import datetime
import calendar

sns.set(style='dark')
px.defaults.template = 'plotly_dark'
px.defaults.color_continuous_scale = 'reds'

# membaca data dari URL                              
day_df = pd.read_csv("https://raw.githubusercontent.com/oktaagnes/bikeSharing/refs/heads/main/Data/day.csv")   
hour_df = pd.read_csv("https://raw.githubusercontent.com/oktaagnes/bikeSharing/refs/heads/main/Data/hour.csv")

# Helper function yang di butuhkan untuk menyiapkan berbagai dataframe
# explore_pertanyaan1 
def create_monthly_df(df):
    monthly_df = df.groupby(by=["mnth","yr"]).agg({
        "cnt" : "sum"
    }).reset_index()
    return monthly_df

def calculate_weekday_vs_weekend(df):
    # Tentukan hari kerja (0-4 untuk weekday) dan akhir pekan (5-6 untuk weekend)
    df["day_type"] = df["weekday"].apply(lambda x: "Weekday" if x < 5 else "Weekend")
    
    # Hitung jumlah penyewaan untuk setiap jenis hari
    weekday_weekend_df = df.groupby("day_type")["cnt"].sum().reset_index()
    weekday_weekend_df.columns = ["day_type", "total_rentals"]
    
    # Hitung persentase
    total = weekday_weekend_df["total_rentals"].sum()
    weekday_weekend_df["percentage"] = (weekday_weekend_df["total_rentals"] / total) * 100
    
    return weekday_weekend_df

def create_casual_register_df(df):
    casual_year_df = df.groupby("season")["casual"].sum().reset_index()
    casual_year_df.columns = ["season", "casual"]
    reg_year_df = df.groupby("season")["registered"].sum().reset_index()
    reg_year_df.columns = ["season", "registered"]
    casual_register_df = casual_year_df.merge(reg_year_df, on="season")
    return casual_register_df

# Filter data
day_df['dteday'] = pd.to_datetime(day_df["dteday"])
hour_df['dteday'] = pd.to_datetime(hour_df["dteday"])
min_date = day_df['dteday'].min()
max_date = day_df['dteday'].max()

# Buat sidebarnya
with st.sidebar:
    st.text('Bike Rental')
    st.image('coding/assets/bikeSharing.jpeg')
    start_date, end_date = st.date_input(
        label='Rentang Waktu', min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )
    main_df = day_df[(day_df["dteday"] >= str(start_date)) & 
                (day_df["dteday"] <= str(end_date))]

# Memanggil helper function
monthly_df = create_monthly_df(main_df)
casual_register_df = create_casual_register_df(main_df)
weekday_vs_weekend_df = calculate_weekday_vs_weekend(main_df)


# Menampilkan DataFrame di aplikasi
st.header('Information of Sharing Bike')
# st.write("Data Penyewaan Bulanan")
# st.dataframe(monthly_df)

#Menampilkan total penyewaan per musim
# st.write("Data Casual dan Registered per musim")
# st.dataframe(casual_register_df)


#visualisai grafik garis penyewa setiap bulan
st.subheader('Grafik Penyewaan Sepeda Setiap Bulan')


# Membaca DataFrame
# Anda perlu mengganti 'data.csv' dengan path ke file data Anda
day_df = pd.read_csv('https://raw.githubusercontent.com/oktaagnes/bikeSharing/refs/heads/main/Data/day.csv', parse_dates=['dteday'])

# Tambahkan kolom nama bulan
day_df['mnthh'] = day_df['dteday'].dt.to_period('M')

# Kelompokkan data berdasarkan bulan
grouped = day_df.groupby('mnthh')['cnt'].sum().reset_index()

# Visualisasi dengan Matplotlib
fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(grouped['mnthh'].astype(str), grouped['cnt'], marker='o', color='blue')
ax.set_title('Jumlah Penyewa per Bulan')
ax.set_xlabel('Bulan')
ax.set_ylabel('Jumlah Penyewa')
ax.set_xticks(range(len(grouped['mnthh'])))
ax.set_xticklabels(grouped['mnthh'].astype(str), rotation=45, fontsize=10)

# Menampilkan hanya garis horizontal
ax.grid(axis='y', linestyle='--', alpha=0.7)  # Garis horizontal putus-putus

# Tampilkan plot di Streamlit
st.pyplot(fig)

# Menghitung jumlah penyewa untuk hari kerja dan akhir pekan
workingday_cnt = day_df[day_df['workingday'] == 1]['cnt'].sum()
weekend_cnt = day_df[day_df['workingday'] == 0]['cnt'].sum()

# Menghitung jumlah penyewa total
total_cnt = day_df['cnt'].sum()

# Menghitung persentase untuk hari kerja dan akhir pekan
workingday_percentage = (workingday_cnt / total_cnt) * 100
weekend_percentage = (weekend_cnt / total_cnt) * 100

# Data untuk pie chart
sizes = [workingday_percentage, weekend_percentage]
labels = ['Workingday', 'Weekend']

# Membuat pie chart persentase menggunakan Plotly
fig = px.pie(
    names=labels, 
    values=sizes, 
    title="Persentase Penyewaan Sepeda Berdasarkan Hari Kerja dan Akhir Pekan",
    color=labels,  # Warna berdasarkan labels
    color_discrete_map={'Workingday': '#1f77b4', 'Weekend': '#85C1E9'},  # Menentukan warna
) 

# Mengatur layout pie chart agar lebih konsisten
fig.update_layout(
    showlegend=True,
    legend_title="Berdasarkan hari",  # Menambahkan judul untuk legenda
    margin=dict(t=50, b=50, l=50, r=50),  # Memberikan margin yang cukup
    height=500  # Mengatur tinggi chart agar sesuai
)

# Menampilkan grafik di Streamlit
st.subheader("Persentase Penyewaan Sepeda Berdasarkan Hari Kerja dan Akhir Pekan")
st.plotly_chart(fig, use_container_width=True)



# Visualisasi penyewa casual dan registered saat menyewa sepeda
# Ganti angka musim menjadi label nama musim
st.subheader('Jumlah Penyewa Casual dan Registered Berdasarkan Musim')

season_mapping = {
    1: "Musim Semi",
    2: "Musim Panas",
    3: "Musim Gugur",
    4: "Musim Dingin"
}
casual_register_df["season"] = casual_register_df["season"].map(season_mapping)

# Buat bar chart untuk membandingkan casual dan registered
fig = px.bar(
    casual_register_df.melt(id_vars="season", var_name="Tipe Penyewa", value_name="Jumlah Penyewa"),
    x="season",
    y="Jumlah Penyewa",
    color="Tipe Penyewa",
    title="Jumlah Penyewa Casual dan Registered Berdasarkan Musim",
    labels={"season": "Musim", "Jumlah Penyewa": "Jumlah Penyewa", "Tipe Penyewa": "Tipe Penyewa"},
    barmode="group",  # Bar akan dikelompokkan untuk setiap musim
    color_discrete_map={
        "casual": "#ADD8E6",  
        "registered": "#00008B"  
    }
)

# Tampilkan bar chart di Streamlit
st.plotly_chart(fig)




