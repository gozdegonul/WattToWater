# water2.py - Bölgeye göre su ayak izi (Adım 2)
# Kaynak: Ren ve ark., arXiv:2304.03271, Tablo 1

REGIONS = {
    # bölge        (PUE,  WUE,   EWIF)
    "Netherlands": (1.140, 0.060, 3.445),
    "Arizona":     (1.180, 1.630, 4.959),
    "Ireland":     (1.190, 0.020, 1.476),
    "US average":  (1.170, 0.550, 3.142),
    "Illinois":    (1.350, 0.740, 2.233),
    "Iowa":        (1.160, 0.140, 3.104),
    "Texas":       (1.280, 0.250, 1.287),
    "Virginia":    (1.140, 0.140, 2.385),
    "Washington":  (1.150, 0.950, 9.501),
    "Wyoming":     (1.110, 0.130, 2.574),
    "Sweden":      (1.160, 0.090, 6.019),
}
# Not: Tablo 1'deki yıldızlı (inşaat aşamasında, Microsoft tahmini) bölgeler
# henüz eklenmedi.


def water_for(region, energy_kwh):
    """Bölge adı ve enerjiden (kWh) litre cinsinden su hesaplar."""
    pue, wue, ewif = REGIONS[region]
    onsite = energy_kwh * wue
    offsite = energy_kwh * pue * ewif
    return onsite, offsite, onsite + offsite


# Bu blok sadece dosya doğrudan çalıştırılınca (py water2.py) çalışır,
# başka dosya "import water2" yapınca çalışmaz.
if __name__ == "__main__":
    for region in REGIONS:
        onsite, offsite, total = water_for(region, 0.06)
        print(f"{region:12} toplam: {total * 1000:6.1f} mL "
              f"(tesis içi {onsite * 1000:5.1f}, elektrik {offsite * 1000:5.1f})")
