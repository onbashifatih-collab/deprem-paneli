import requests
import pandas as pd

def deprem_verilerini_getir():
    # Doğru USGS GeoJSON uç noktası (Çoğul olan 'earthquakes' kelimesiyle)
    url = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson"
    
    print("🌍 USGS API'sinden canlı deprem verileri çekiliyor...")
    response = requests.get(url)
    
    if response.status_code != 200:
        print("❌ Veri çekilemedi! Hata kodu:", response.status_code)
        return None
        
    data = response.json()
    depremler = []
    
    for feature in data["features"]:
        props = feature["properties"]
        coords = feature["geometry"]["coordinates"] # [boylam, enlem, derinlik]
        
        depremler.append({
            "yer": props["place"],
            "buyukluk": props["mag"],
            "zaman": pd.to_datetime(props["time"], unit="ms"),
            "detay_url": props["url"],
            "boylam": coords[0],
            "enlem": coords[1],
            "derinlik": coords[2]
        })
        
    df = pd.DataFrame(depremler)
    print(f"✅ Başarıyla {len(df)} adet güncel deprem verisi çekildi!")
    return df

if __name__ == "__main__":
    df = deprem_verilerini_getir()
    if df is not None:
        print(df.head())