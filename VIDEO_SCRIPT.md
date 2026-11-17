# AquaShift — video senaryosu (~3 dakika)

Konuşma metni İngilizce (makale ile aynı dil). Köşeli parantez içindekiler çekim notu.
Yarışmanın video süre sınırını kontrol et; aşağıdaki süreler toplam ~3 dk.

## Çekimden önce

- Tüm uygulamaları kapat (ölçüm koşulu makaledeki Set 1/4 ile aynı olsun).
- Terminali büyük font ile aç (Ctrl + tekerlek), koyu tema.
- Bir kez prova çalıştır: `py aquashift.py` (ilk çalıştırma biraz yavaş olabilir).
- Açık sekmeler: `aquashift_map.html`, `figures/fig2_water_vs_stress.png`, `figures/fig3_model_size.png`, makale.

## 1. Kanca — 0:00–0:20  [kameraya konuş]

> Every time we run code, somewhere a data center uses water, to cool its servers
> and to generate its electricity. But no developer ever sees that number.
> I built AquaShift to make it visible.

## 2. Problem — 0:20–0:45  [makalenin Introduction kısmı ekranda]

> Water is used in two places: on-site, for cooling, and off-site, at the power plants.
> Published research estimates that training GPT-3 used about 5.4 million litres.
> But the same job does not cost the same water everywhere, and a litre in a dry
> region is not the same as a litre in a wet one.

## 3. Canlı demo — 0:45–1:35  [terminal]

`py aquashift.py`

> I train a real machine-learning model, a 200-tree Random Forest, on my laptop.
> AquaShift measures the time and CPU use, estimates the energy,
> and converts it into water for 11 data-center regions.

[Tablo çıkınca imleçle göster]

> Same job: Ireland about 0.1 millilitres, Washington about 0.7. That's 6.7 times more.
> And look at the on-site column: cooling is at most 22 percent.
> The electricity grid is the real water consumer.

## 4. Litre ≠ kıtlık — 1:35–2:10  [fig2_water_vs_stress.png veya aquashift_map.html]

> But litres are only half the story. Here I put each region's water footprint next to
> its water stress from WRI Aqueduct. Texas uses very little water, but it is in a
> High-stress region. Washington uses the most, but has low stress.
> That's why AquaShift never merges them into one number: it shows both.

## 5. İkinci kaldıraç: model boyutu — 2:10–2:40  [önce terminal, sonra fig3]

`py aquashift.py --trees 100`

> And if you can't move your job, you can shrink it. With 100 trees instead of 200,
> the model used 48 percent of the energy and water, and the accuracy was the same,
> even slightly higher.

## 6. Dürüstlük + kapanış — 2:40–3:00  [kameraya konuş]

> This is a prototype: energy is estimated, not metered, and the factors are annual averages.
> All assumptions, data and code are open, and every number can be regenerated with one command.
> The goal is simple: put the water cost of software in front of the people who write it.
> Thank you.

## Ekranda gösterilecek sayılar (hepsi makaleyle tutarlı)

| Bulgu | Sayı |
|---|---|
| Bölge farkı | 0,106 mL (İrlanda) – 0,708 mL (Washington), 6,7 kat |
| Tesis içi (soğutma) payı | en fazla %22 (Arizona) |
| Teksas | 2. en düşük su, Yüksek su stresi (3,33) |
| 100 ağaç | enerjinin ve suyun %48'i, doğruluk %96,15 (200 ağaçta %95,90) |

Not: Canlı demoda sayılar her çalıştırmada biraz değişir (ör. 0,097 mL); makaledeki
değerler 15 çalıştırmanın ortalamasıdır. Videoda bunu söylemen dürüst olur:
"numbers vary slightly per run; the paper reports the mean of 15 runs."
