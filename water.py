# water.py - Bir işin su ayak izi (Adım 1)
# Formül: Ren ve ark., arXiv:2304.03271

def water_footprint(energy_kwh, wue, pue, ewif):
    """Enerjiden (kWh) litre cinsinden su hesaplar."""
    onsite = energy_kwh * wue            # tesis içi (soğutma) suyu
    offsite = energy_kwh * pue * ewif    # elektrik üretimi suyu
    total = onsite + offsite
    return onsite, offsite, total


# Örnek: 30 W x 2 saat = 0,06 kWh, Hollanda değerleri (Ren ve ark. Tablo 1)
energy_kwh = 0.06
onsite, offsite, total = water_footprint(energy_kwh, wue=0.060, pue=1.140, ewif=3.445)

print(f"Tesis içi su       : {onsite * 1000:.1f} mL")
print(f"Elektrik üretimi   : {offsite * 1000:.1f} mL")
print(f"Toplam             : {total * 1000:.1f} mL")
