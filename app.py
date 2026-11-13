import streamlit as st
import pandas as pd
import plotly.express as px
from veri_cek import deprem_verilerini_getir

# 1. Sayfa Konfigürasyonu
st.set_page_config(
    page_title="Global Deprem İstihbarat Paneli",
    page_icon="🌍",
    layout="wide"
)

# 2. Ultra-Modern UI / CSS ve Gizlilik Stilleri
st.markdown("""
    <style>
        .stApp {
            background-color: #030712;
            color: #f3f4f6;
        }
        .stSidebar {
            background-color: #0b0f19;
            border-right: 1px solid #1f2937;
        }
        .block-container {
            padding-top: 2rem !important;
            padding-bottom: 2rem !important;
        }
        div[data-testid="stMetric"] {
            background: linear-gradient(135deg, #111827 0%, #030712 100%);
            padding: 22px;
            border-radius: 14px;
            border: 1px solid #1f2937;
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.7);
        }
        div[data-testid="stMetric"] label {
            color: #9ca3af !important;
            font-weight: 600;
            font-size: 0.95rem;
        }
        div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
            color: #ffffff !important;
            font-weight: 800;
        }
        .custom-card {
            background: linear-gradient(135deg, #111827 0%, #090d16 100%);
            padding: 16px;
            border-radius: 12px;
            border: 1px solid #1f2937;
            margin-bottom: 12px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.4);
            transition: all 0.3s ease;
        }
        .custom-card:hover {
            border-color: #ef4444;
            box-shadow: 0 0 15px rgba(239, 68, 68, 0.3);
        }
    </style>
""", unsafe_allow_html=True)

st.title("🌍 Global Deprem İstihbarat ve Analiz Paneli")
st.markdown("USGS (Amerikan Jeoloji Araştırmaları Kurumu) canlı akış verileriyle güçlendirilmiş profesyonel gözlem merkezi.")

# 3. Veriyi Önbelleğe Alarak Çekme
@st.cache_data(ttl=600)
def veri_yukle():
    return deprem_verilerini_getir()

df = veri_yukle()

if df is None or df.empty:
    st.error("Veri yüklenirken bir hata oluştu!")
else:
    # 4. Sol Menü (Filtreleme Alanı)
    st.sidebar.header("🔍 Kontrol & Filtre Masası")
    
    bolgeler = ["Tüm Dünya", "Türkiye ve Çevresi", "Amerika (USA)", "Alaska", "Japonya ve Asya Pasifik", "Güney Amerika"]
    secilen_bolge = st.sidebar.selectbox("Hedef Bölge / Ülke", bolgeler)
    
    min_mag = float(df["buyukluk"].min())
    max_mag = float(df["buyukluk"].max())
    
    secilen_buyukluk = st.sidebar.slider(
        "Minimum Deprem Büyüklüğü (Mag)",
        min_value=min_mag,
        max_value=max_mag,
        value=float(min_mag)
    )
    
    # Filtreleme Mantığı
    df_filtered = df[df["buyukluk"] >= secilen_buyukluk]
    
    if secilen_bolge == "Türkiye ve Çevresi":
        df_filtered = df_filtered[
            (df_filtered["enlem"] >= 34.0) & (df_filtered["enlem"] <= 45.0) &
            (df_filtered["boylam"] >= 25.0) & (df_filtered["boylam"] <= 45.0)
        ]
    elif secilen_bolge == "Amerika (USA)":
        df_filtered = df_filtered[df_filtered["yer"].str.contains("CA|California|Nevada|Oregon|Washington|Hawaii|WY|ID", case=False, na=False)]
    elif secilen_bolge == "Alaska":
        df_filtered = df_filtered[df_filtered["yer"].str.contains("Alaska|Aleutian", case=False, na=False)]
    elif secilen_bolge == "Japonya ve Asya Pasifik":
        df_filtered = df_filtered[df_filtered["yer"].str.contains("Japan|Fiji|Tonga|Indonesia|Philippines|New Zealand|Kamchatka", case=False, na=False)]
    elif secilen_bolge == "Güney Amerika":
        df_filtered = df_filtered[df_filtered["yer"].str.contains("Chile|Peru|Argentina|Colombia|Ecuador", case=False, na=False)]

    # 5. Kritik Alarm Sistemi
    buyuk_depremler = df_filtered[df_filtered["buyukluk"] >= 4.5]
    if not buyuk_depremler.empty:
        st.warning(f"⚠️ KRİTİK UYARI: Seçilen kriterlerde {len(buyuk_depremler)} adet 4.5 büyüklüğü veya üzerinde deprem tespit edildi!")

    # 6. Üst Özet Kartları (KPI Metrikleri)
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Toplam Deprem Sayısı", len(df_filtered))
    
    if not df_filtered.empty:
        col2.metric("En Büyük Deprem", f"{df_filtered['buyukluk'].max():.1f} Mag")
        col3.metric("Ortalama Derinlik", f"{df_filtered['derinlik'].mean():.1f} km")
        col4.metric("En Sığ Deprem", f"{df_filtered['derinlik'].min():.1f} km")
    else:
        col2.metric("En Büyük Deprem", "0 Mag")
        col3.metric("Ortalama Derinlik", "0 km")
        col4.metric("En Sığ Deprem", "0 km")

    st.divider()

    # 7. Sekme Yapısı
    sekme1, sekme2 = st.tabs(["🌐 Canlı Küresel Harita & Radar", "📈 Gelişmiş Analitik Grafikler"])

    with sekme1:
        if df_filtered.empty:
            st.info("Seçilen bölge ve kriterlere uygun deprem bulunamadı.")
        else:
            col_harita, col_bilgi = st.columns([1.8, 1])
            
            with col_harita:
                st.subheader("🌐 Canlı ve Dikkat Çekici Deprem Radarı")
                
                df_map = df_filtered.copy()
                df_map["buyukluk_gorsel"] = df_map["buyukluk"].apply(lambda x: max(x, 0.4))
                
                fig_map = px.scatter_geo(
                    df_map,
                    lat="enlem",
                    lon="boylam",
                    size="buyukluk_gorsel",
                    color="buyukluk",
                    hover_name="yer",
                    hover_data={
                        "zaman": True,
                        "buyukluk": True,
                        "derinlik": True,
                        "buyukluk_gorsel": False
                    },
                    color_continuous_scale="Reds",
                    projection="mercator"
                )
                
                fig_map.update_geos(
                    showland=True, landcolor="#1e293b",
                    showocean=True, oceancolor="#030712",
                    showcountries=True, countrycolor="#334155",
                    showsubunits=True, subunitcolor="#1e293b"
                )
                
                fig_map.update_layout(
                    margin=dict(l=0, r=0, t=10, b=0),
                    paper_bgcolor='#030712',
                    plot_bgcolor='#030712',
                    font=dict(color='white'),
                    legend=dict(font=dict(color='white')),
                    height=520
                )
                st.plotly_chart(fig_map, width='stretch')

            with col_bilgi:
                st.subheader("⚡ Son Büyük Sarsıntılar (Canlı Akış)")
                st.markdown("En yüksek şiddetli depremlerin kritik künyesi:")
                
                en_buyukler = df_filtered.sort_values(by="buyukluk", ascending=False).head(5)
                for idx, row in en_buyukler.iterrows():
                    temiz_zaman = str(row['zaman']).split('.')[0] if pd.notnull(row['zaman']) else "Bilinmiyor"
                    
                    # Hatalı parametre (unsafe_alert) temizlendi, sadece unsafe_allow_html kaldı
                    st.markdown(f"""
                    <div class="custom-card">
                        📍 <b>Konum:</b> {row['yer']}<br>
                        ⚡ <b>Büyüklük:</b> <span style="color: #ef4444; font-weight: bold; font-size: 1.1rem;">{row['buyukluk']} Mag 🔴</span><br>
                        🕒 <b>Zaman:</b> {temiz_zaman}<br>
                        🌊 <b>Derinlik:</b> {row['derinlik']} km<br>
                        🔗 <a href="{row['detay_url']}" target="_blank" style="color: #38bdf8; text-decoration: none;">USGS Resmi Kayıt →</a>
                    </div>
                    """, unsafe_allow_html=True)

    with sekme2:
        if df_filtered.empty:
            st.info("Grafik oluşturulacak veri bulunamadı.")
        else:
            col_g1, col_g2 = st.columns(2)
            with col_g1:
                st.subheader("Büyüklük Frekans Dağılımı")
                fig_mag = px.histogram(df_filtered, x="buyukluk", nbins=20, labels={"buyukluk": "Büyüklük"}, color_discrete_sequence=["#ef4444"])
                fig_mag.update_layout(paper_bgcolor='#030712', plot_bgcolor='#030712', font=dict(color='white'), height=400)
                st.plotly_chart(fig_mag, width='stretch')
            
            with col_g2:
                st.subheader("Derinlik / Şiddet Matrisi")
                fig_depth = px.scatter(df_filtered, x="buyukluk", y="derinlik", color="buyukluk", color_continuous_scale="Reds", labels={"buyukluk": "Büyüklük", "derinlik": "Derinlik (km)"})
                fig_depth.update_layout(paper_bgcolor='#030712', plot_bgcolor='#030712', font=dict(color='white'), height=400)
                st.plotly_chart(fig_depth, width='stretch')