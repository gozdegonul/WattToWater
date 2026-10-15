# stress.py - Bölgelerin su stresi puanları (Adım 8)
#
# Kaynak: WRI Aqueduct 4.0 Country Rankings
#   dosya   : Aqueduct40_rankings_download_Y2023M07D05.xlsx
#   gösterge: bws (baseline water stress), ağırlık: Tot (toplam talep)
#   puan 0-5 arası (yüksek = daha fazla su stresi)
# Ülke düzeyi : sayfa "country_baseline" (Hollanda, İrlanda, İsveç, ABD ortalaması)
# Eyalet düzeyi: sayfa "province_baseline" (ABD eyaletleri)
# Bu sayılar xlsx dosyasından program ile okundu, elle yazılmadı.
#
# Doğrulamak için: xlsx'i aç, ilgili sayfada name_0 / name_1, indicator_name = bws,
# weight = Tot satırına bak, "score" sütunu aşağıdaki sayıyla aynı olmalı.
#
# UYARI (WRI Read Me): bu göstergeler doğrudan ölçülemez, doğrulanmamıştır
# ve havzalar arası su transferlerini modellemez.

STRESS = {
    # bölge: (puan, kategori, düzey)
    "Netherlands": (1.581120297, "Low - Medium (10-20%)", "ülke"),
    "Arizona": (4.392122413, "Extremely High (>80%)", "eyalet"),
    "Ireland": (0.363338153, "Low (<10%)", "ülke"),
    "US average": (2.604411175, "Medium - High (20-40%)", "ülke"),
    "Illinois": (2.402912456, "Medium - High (20-40%)", "eyalet"),
    "Iowa": (1.08236803, "Low - Medium (10-20%)", "eyalet"),
    "Texas": (3.329698739, "High (40-80%)", "eyalet"),
    "Virginia": (2.562448902, "Medium - High (20-40%)", "eyalet"),
    "Washington": (1.203172775, "Low - Medium (10-20%)", "eyalet"),
    "Wyoming": (3.765395727, "High (40-80%)", "eyalet"),
    "Sweden": (0.781293393, "Low (<10%)", "ülke"),
}
