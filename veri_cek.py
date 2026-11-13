import pandas as pd
import requests

USGS_URL = (
    "https://earthquake.usgs.gov/earthquakes/feed/"
    "v1.0/summary/all_day.geojson"
)


def deprem_verilerini_getir():
    try:
        # Bağlantı en fazla 15 saniye bekler.
        response = requests.get(USGS_URL, timeout=15)
        response.raise_for_status()
        data = response.json()

        depremler = []

        for feature in data.get("features", []):
            props = feature.get("properties") or {}
            geometry = feature.get("geometry") or {}
            coords = geometry.get("coordinates") or []

            # Harita ve grafikler için gerekli bilgiler eksikse kaydı atla.
            if len(coords) < 3 or props.get("mag") is None:
                continue

            depremler.append({
                "yer": props.get("place") or "Konum bilinmiyor",
                "buyukluk": props["mag"],
                "zaman": props.get("time"),
                "detay_url": props.get("url") or "",
                "boylam": coords[0],
                "enlem": coords[1],
                "derinlik": coords[2],
            })

        df = pd.DataFrame(depremler)
        if not df.empty:
            df["zaman"] = pd.to_datetime(
                df["zaman"], unit="ms", utc=True, errors="coerce"
            ).dt.tz_convert("Europe/Istanbul")
        return df

    except (requests.RequestException, ValueError) as hata:
        print(f"USGS verileri alınamadı: {hata}")
        return None


if __name__ == "__main__":
    df = deprem_verilerini_getir()

    if df is not None:
        print(df.head())