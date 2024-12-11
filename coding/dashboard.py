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

# Load berkas                                   
day_clean_df = pd.read_csv("bikeSharing/coding/data/dayDataSet.csv")
hour_df = pd.read_csv("bikeSharing/coding/data/hourDataSet.csv")

# Helper function yang di butuhkan untuk menyiapkan berbagai dataframe
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
    casual_year_df.columns = ["season", "total_casual"]
    reg_year_df = df.groupby("season")["registered"].sum().reset_index()
    reg_year_df.columns = ["season", "total_registered"]
    casual_register_df = casual_year_df.merge(reg_year_df, on="season")
    return casual_register_df

# Filter data
day_clean_df['dteday'] = pd.to_datetime(day_clean_df["dteday"])
hour_df['dteday'] = pd.to_datetime(hour_df["dteday"])
min_date = day_clean_df['dteday'].min()
max_date = day_clean_df['dteday'].max()

# Buat sidebarnya
with st.sidebar:
    st.text('Bike Rental')
    st.image('assets/bikeSharing.jpeg', caption='')
    start_date, end_date = st.date_input(
        label='Rentang Waktu', min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )
    main_df = day_clean_df[(day_clean_df["dteday"] >= str(start_date)) & 
                (day_clean_df["dteday"] <= str(end_date))]

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

# Konversi nilai 'yr' menjadi format tahun yang sebenarnya
def map_year(yr_value):
    base_year = 2011  # Tahun awal dalam dataset
    return base_year + yr_value

monthly_df['tahun'] = monthly_df['yr'].apply(map_year)
monthly_df['mnth'] = monthly_df['mnth'].astype(int)

# Buat visualisasi line chart
fig = px.line(
    monthly_df,
    x="mnth",
    y="cnt",
    color="tahun",  # Gunakan kolom 'tahun' yang baru
    title="Jumlah Penyewaan Sepeda Bulanan",
    labels={"mnth": "Bulan", "cnt": "Jumlah Penyewaan", "tahun": "Tahun"},
    category_orders={"mnth": list(range(1, 13))}
)
# Mengatur nilai tick pada sumbu-x 
fig.update_layout( 
    xaxis=dict( 
        tickvals=list(range(1, 13)), # Menampilkan angka dari 1 hingga 12 
        ticktext=["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"] 
    ) 
)

# Menampilkan grafik pada aplikasi Streamlit
st.plotly_chart(fig)

# Buat pie chart untuk persentase weekday vs weekend dengan warna sesuai praktik data science
fig = px.pie(
    weekday_vs_weekend_df,
    names="day_type",  # Nama kategori (Weekday/Weekend)
    values="percentage",  # Nilai persentase
    title="Persentase Penyewaan Sepeda: Hari Kerja vs Akhir Pekan",
    color="day_type",  # Gunakan day_type untuk membedakan warna
    color_discrete_map={
        "Weekday": "#1f77b4",  # Warna biru untuk hari kerja
        "Weekend": "#2ca02c"  # Warna hijau untuk akhir pekan
    }
)

# Tampilkan pie chart di Streamlit
st.subheader("Persentase Penyewaan Sepeda Berdasarkan Hari Kerja dan Akhir Pekan")
st.plotly_chart(fig)

# Visualisasi penyewa casual dan registered saat menyewa sepeda
# Ganti angka musim menjadi label nama musim
st.subheader('Jumlah Penyewa Casual dan Registered Berdasarkan Musim')

season_mapping = {
    1: "Spring",
    2: "Summer",
    3: "Fall",
    4: "Winter"
}
casual_register_df["season"] = casual_register_df["season"].map(season_mapping)

# Buat bar chart untuk membandingkan casual dan registered
fig = px.bar(
    casual_register_df.melt(id_vars="season", var_name="Tipe Penyewa", value_name="Jumlah Penyewa"),
    x="season",
    y="Jumlah Penyewa",
    color="Tipe Penyewa",
    title="Jumlah Penyewa Casual dan Registered Berdasarkan Musim",
    labels={"season": "Musim", "Jumlah Penyewa": "Total Penyewa", "Tipe Penyewa": "Tipe Penyewa"},
    barmode="group",  # Bar akan dikelompokkan untuk setiap musim
    color_discrete_map={
        "casual": "#FDBF6F",  # Oranye untuk Casual
        "registered": "#377eb8"  # Biru untuk Registered
    }
)

# Tampilkan bar chart di Streamlit
st.plotly_chart(fig)




