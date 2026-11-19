# water2.py - Bölgeye göre su ayak izi (Adım 2)
# Veriler ve formül artık tek kaynakta: watttowater/data.py
# Kaynak: Li ve ark., arXiv:2304.03271, Tablo 1

from watttowater.data import REGIONS, water_for  # noqa: F401

# Bu blok sadece dosya doğrudan çalıştırılınca (py water2.py) çalışır.
if __name__ == "__main__":
    for region in REGIONS:
        onsite, offsite, total = water_for(region, 0.06)
        print(f"{region:12} toplam: {total * 1000:6.1f} mL "
              f"(tesis içi {onsite * 1000:5.1f}, elektrik {offsite * 1000:5.1f})")
