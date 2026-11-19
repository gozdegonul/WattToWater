# WattToWater — video senaryosu (3:00)

Yarışma şartı: anlatımlı sunum + demo, en fazla 3 dakika. Konuşma metni İngilizce,
köşeli parantez içindekiler çekim notu. Süreler toplam 3:00.

## Çekimden önce

- Tüm uygulamaları kapat (makaledeki Set 1/4 koşulu).
- Terminali büyük font ile aç (Ctrl + tekerlek), koyu tema.
- Prova: aşağıdaki 3 komutu birer kez çalıştır (ilk çalıştırma yavaş olabilir).
- `water_log.csv` dosyasını sil, böylece rapor sadece çekimdeki çalıştırmaları gösterir.
- Açık sekmeler: `figures/banner_wide.png`, `examples/quickstart.py` (VS Code),
  GitHub'da Actions sayfasındaki son "water-report" çalıştırmasının özeti, makale PDF'i.

## 1. Kanca — 0:00–0:15  [banner ekranda, kameraya konuş]

> Every time we run code, a data center somewhere uses water, to cool its servers and
> to generate its electricity. But developers never see that number. And you can't
> reduce what you can't see. So I built WattToWater: a water meter for code.

## 2. Problem — 0:15–0:35  [makalenin Fig. 1 ve Fig. 2'si]

> Water is used in two places: on-site, for cooling, and off-site, at the power plants.
> The same job does not cost the same water everywhere, and a litre in a dry region is
> not the same as a litre in a wet one.

## 3. Canlı ölçüm — 0:35–1:15  [terminal]

`python -m watttowater --max-stress 2`

> I train a real machine-learning model on my laptop. WattToWater measures it, estimates
> the energy and converts it into water for 11 data-center regions.

[Tablo çıkınca imleçle göster]

> Same job: Ireland about 0.1 millilitres, Washington about 0.7: 6.7 times more.
> Cooling is at most 22 percent; the electricity grid is the real water consumer.
> And look at Texas: very little water, but high water stress. That's why WattToWater
> shows litres and scarcity side by side, and here it recommends only regions under
> a water-stress limit.

## 4. Çözüm 1 — geliştirici: tek satır — 1:15–1:40  [VS Code: examples/quickstart.py, sonra terminal]

> The solution has three levels. First, the developer. You add one line, track_water,
> above your function...

`python examples/quickstart.py`

> ...and every run prints its water footprint and is logged.

## 5. Çözüm 2 — ekip: her push'ta su raporu — 1:40–2:05  [terminal, sonra GitHub Actions özeti]

`python -m watttowater report water_log.csv --region Virginia`

> Second, the team. The log becomes a report: total water, best and worst region, and
> which job uses the most. On GitHub, it runs automatically on every push, so the whole
> team sees the water footprint of every change.

## 6. Çözüm 3 — kurum: ne ve nerede çalıştırmalı — 2:05–2:35  [terminal]

`python examples/model_size.py`

> Third, decisions. The advisor measures model variants. Here, 50 trees reach the same
> accuracy as 200 trees with about a quarter of the water. No new hardware, no new
> region: just a smaller model. And for teams that choose cloud regions, a water-stress
> policy filters the regions.

## 7. Dürüstlük + kapanış — 2:35–3:00  [kameraya konuş, sonra banner]

> This is a prototype: energy is estimated, not metered, and the factors are annual
> averages. Everything is open: the data, the code, the tests and our paper.
> WattToWater puts the water cost of software in front of the people who write it,
> at the moment they decide. Thank you.

## Ekranda gösterilecek sayılar (makaleyle tutarlı)

| Bulgu | Sayı |
|---|---|
| Bölge farkı | 0,106 mL (İrlanda) – 0,708 mL (Washington), 6,7 kat |
| Soğutma payı | en fazla %22 (Arizona); elektrik en az %78 |
| Teksas | 2. en düşük su, Yüksek su stresi (3,33) |
| Model boyutu | 100 ağaç: suyun %48'i, doğruluk %96,15 (200 ağaçta %95,90) |
| Danışman (canlı) | 50 ağaç: suyun ~%23'ü, doğruluk %95,95 |

Not: Canlı sayılar her çalıştırmada biraz değişir; makaledeki değerler 15 çalıştırmanın
ortalamasıdır. Videoda bir kez söylemen yeterli: "live numbers vary slightly per run".
