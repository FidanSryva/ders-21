import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# 1. Səhifə konfiqurasiyası (ən başda olmalıdır)
st.set_page_config(page_title="Satış Dashboard", layout="wide")

# 2. Süni data yaradaq (real layihədə pd.read_csv() və ya pd.read_excel() olardı)
@st.cache_data  # data yenidən-yenidən yüklənməsin deyə keşləyir
def load_data():
    np.random.seed(42)
    tarixler = pd.date_range("2025-01-01", periods=90)
    filiallar = ["Bakı", "Gəncə", "Sumqayıt","Sheki"]
    mehsullar = ["Noutbuk", "Telefon", "Qulaqlıq"]
    
    rows = []
    for tarix in tarixler:
        for filial in filiallar:
            for mehsul in mehsullar:
                say = np.random.randint(0, 15)
                qiymet = {"Noutbuk": 1200, "Telefon": 800, "Qulaqlıq": 90}[mehsul]
                rows.append([tarix, filial, mehsul, say, say * qiymet])
    
    return pd.DataFrame(rows, columns=["Tarix", "Filial", "Məhsul", "Say", "Gəlir"])

df = load_data()

# 3. Başlıq
st.title("📊 Filial Satış Dashboard")
st.markdown("Real vaxtda filtrlənə bilən satış analitikası")

# 4. Sidebar — filtrləmə paneli (bütün UI inputları burda)
st.sidebar.header("Filtrlər")

secilmis_filiallar = st.sidebar.multiselect(
    "Filial seçin:", 
    options=df["Filial"].unique(), 
    default=df["Filial"].unique()
)

tarix_araligi = st.sidebar.date_input(
    "Tarix aralığı:",
    value=(df["Tarix"].min(), df["Tarix"].max())
)

# 5. Datanı filtrlə (əvvəllər öyrəndiyiniz & operatoru burda!)
mask = (
    df["Filial"].isin(secilmis_filiallar) &
    (df["Tarix"] >= pd.Timestamp(tarix_araligi[0])) &
    (df["Tarix"] <= pd.Timestamp(tarix_araligi[1]))
)
filtered_df = df[mask]

# 6. Əsas metriklər (KPI kartları)
col1, col2, col3 = st.columns(3)
col1.metric("Ümumi Gəlir", f"{filtered_df['Gəlir'].sum():,.0f} AZN")
col2.metric("Ümumi Satış (ədəd)", f"{filtered_df['Say'].sum():,.0f}")
col3.metric("Orta Günlük Gəlir", f"{filtered_df.groupby('Tarix')['Gəlir'].sum().mean():,.0f} AZN")

# 7. Qruplaşdırma (groupby — artıq tanış!)
filial_xulase = filtered_df.groupby("Filial")["Gəlir"].sum().reset_index()

# 8. Qrafiklər — iki sütunda yan-yana
col1, col2 = st.columns(2)

with col1:
    fig1 = px.bar(filial_xulase, x="Filial", y="Gəlir", 
                   title="Filial üzrə Ümumi Gəlir", color="Filial")
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    mehsul_xulase = filtered_df.groupby("Məhsul")["Gəlir"].sum().reset_index()
    fig2 = px.pie(mehsul_xulase, names="Məhsul", values="Gəlir", 
                   title="Məhsul üzrə Gəlir Payı")
    st.plotly_chart(fig2, use_container_width=True)

# 9. Zaman üzrə trend
gunluk_trend = filtered_df.groupby("Tarix")["Gəlir"].sum().reset_index()
fig3 = px.line(gunluk_trend, x="Tarix", y="Gəlir", title="Günlük Gəlir Trendi")
st.plotly_chart(fig3, use_container_width=True)

# 10. Cədvəl (istəyən özü axtara bilsin)
st.subheader("Ətraflı Data")
st.dataframe(filtered_df, use_container_width=True)