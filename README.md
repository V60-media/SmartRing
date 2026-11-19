# Smart Ring – Exploded View (Blender / bpy)

Animasi 3D smart ring: utuh → exploded view → utuh lagi. Seluruh proses (modeling,
material, kamera, lighting, animasi, render) dibuat oleh `ring_explode.py`.

| File | Isi |
|---|---|
| `ring_explode.py` | Script bpy lengkap, headless |
| `ring_explode.blend` | Hasil modeling + animasi (disimpan dengan setting **final**: 1920×1080, 256 spp, output `//final/frame_####.png`) |
| `test/` | 6 frame verifikasi (1, 40, 80, 120, 180, 240) @ 480×270, 32 spp |
| `test_contact_sheet.png` | Ke-6 frame test dalam satu gambar |
| `preview/frame_0180.png` | 1 frame dengan setting final penuh (1920×1080, 256 spp, denoise) |

## Cara menjalankan

```bash
blender -b -P ring_explode.py                       # MODE di awal file ("test")
blender -b -P ring_explode.py -- --mode final       # 240 frame PNG ke final/
blender -b -P ring_explode.py -- --no-render        # hanya build + simpan .blend
```

Variabel global di awal script: `MODE`, `ENGINE` (`"CYCLES"`/`"EEVEE"`), `DEVICE`,
`RESOLUTION`, `SAMPLES`, `FRAME_RANGE` (list = frame tertentu, tuple = rentang animasi),
`OUTPUT_DIR`, `DENOISE`. Semuanya juga bisa di-override lewat CLI setelah `--`
(`--mode --engine --device --samples --res 1280x720 --frames 1-240 | 1,40,80 --out --no-render --no-save`).

Diuji dengan Blender 4.5 LTS (Cycles, CPU). Butuh Blender ≥ 4.2.

## Skala & struktur

* 1 unit = 1 mm (`unit_settings.scale_length = 0.001`), sehingga DOF f/5.6 & lensa 50 mm
  berperilaku fisik (sudah dicek: blur ringan terlihat di close-up).
* Semua part adalah benda putar (revolve profil 2D) – lingkaran sempurna atau busur –
  di sekitar sumbu Z lokal empty `Ring_Root`. Sumbu itu juga sumbu explode
  (~45° dari vertikal di layar, miring ke arah kamera).
* Satu collection per komponen (`01_Shell_Outer` … `06_Shell_Inner`, plus `00_Rig`,
  `07_Environment`, `08_Camera_Lights`). Detail kecil di-parent ke objek utamanya.

| # | Objek utama | Dimensi (radius dari sumbu) | Detail |
|---|---|---|---|
| 1 | `Shell_Outer` | OD 22 (r 10.42–11.0), lebar 8, profil luar membulat (crown 0.08 + fillet 0.65) | rebate/lekukan tipis di tepi dalam (r 10.56, 0.5 mm) |
| 2 | `Sensor_Frame` | r 10.10–10.40, lebar 6.6 | 2 jendela sensor (hijau & merah, housing translusen + core emissive), 4 titik LED hijau |
| 3 | `Battery_Arc` | busur 200°, tebal 1.38, lebar 6, ujung membulat (taper) | tab terminal emas |
| 4 | `PCB_Flex` | r 9.95–10.03, lebar 5.6 | jalur emas di 2 sisi, 4 chip hitam (2 dengan kaki emas), pad emas + connector finger, 2 kabel merah (curve) |
| 5 | `Pin_L`, `Pin_R` (di bawah empty `Charging_Pins`) | silinder Ø0.9 × 3 mm, sejajar sumbu pada r = 9 | collar + bevel |
| 6 | `Shell_Inner` | ID 17 (r 8.5–9.5, dinding bening 1.0), flange depan/belakang sampai r 10.38 | modul sensor tertanam dengan 2 LED hijau, 1 LED merah, photodiode |

Material: semua Principled BSDF, tanpa image texture (nilai sesuai brief: shell metallic 1 /
rough 0.15 / #1a1a1a / anisotropic 0.35 dengan tangent radial, frame & battery metallic 0.8 /
rough 0.35, gold metallic 1 / rough 0.3, chip rough 0.5, kabel merah rough 0.4 + emission lemah,
kaca transmission 1 / IOR 1.45 / rough 0.02, LED #00ff40 emission 6, pin metallic 1 / rough 0.2).

## Timeline (24 fps, 240 frame)

| Frame | Aksi |
|---|---|
| 1–40 | Ring utuh, turntable lambat 18° (ease), kamera push-in pelan |
| 40–120 | Part lepas satu per satu (stagger 8 f, 40 f/part, Bézier ease-in-out), jarak 18 mm, rotasi kecil (spin ±12–26°, tilt ±3–5°). Garis putus-putus tumbuh, kamera mundur |
| 120–180 | Hold exploded, kamera orbit 60° (ease) |
| 180–240 | Urutan dibalik persis, ring utuh lagi di frame 238 |

Urutan lepas: Shell_Outer → Shell_Inner → Sensor_Frame → Pins → Battery → PCB (dari kedua
ujung ke dalam), supaya tidak ada part yang menembus part lain yang belum bergerak.

## Yang sudah dicek di render test

* Frame 1/40: bentuk ring sesuai referensi #1 – shell hitam glossy, kaca dalam bening
  dengan modul sensor LED hijau/merah dan jalur emas terlihat dari dalam.
* Frame 80: part sedang berpisah; semua part tetap dalam frame (dolly kamera disesuaikan).
* Frame 120/180: exploded view diagonal seperti referensi #2, garis sumbu putus-putus,
  shadow lembut di shadow catcher, background #eeeeee.
* Frame 240: ring kembali utuh (terlihat dari sisi lain karena orbit).
* Close-up (960×540) tiap part: PCB (trace, chip, pad, kabel), sensor frame (jendela + LED),
  battery (ujung membulat), kaca (flange + modul), pin. Frame antara (48, 60, 72, 90, 100,
  190, 205, 215, 225) dicek untuk tabrakan/penetrasi – kabel merah yang sempat tembus
  sensor frame sudah diperbaiki.
* DOF f/5.6 terbukti bekerja dengan skala mm.

## Keterbatasan / yang belum persis

* **Tebal dinding 2.5 mm vs isi.** Battery 1.5 mm + kaca 1.0 mm saja sudah 2.5 mm, belum
  termasuk shell luar, frame dan PCB. Solusi: battery (tebal 1.38) dan modul sensor
  **tertanam di dalam dinding kaca** (seperti resin potting pada ring asli). Akibatnya saat
  kaca lepas/masuk, kaca terlihat melewati battery selama beberapa frame.
* **Pin** tidak bisa "berbagi pusat" dengan shell karena berbentuk silinder kecil; pin
  sejajar sumbu dan diletakkan di lingkaran r = 9 mm di dalam dinding kaca.
* **Kontak charging bundar** di permukaan dalam (referensi #1) tidak dibuat terpisah; yang
  terlihat dari dalam adalah modul sensor.
* **Shadow catcher** hanya ada di Cycles. Di EEVEE plane-nya disembunyikan. Jalur EEVEE
  belum teruji karena container ini tidak punya GPU/EGL.
* **Kaca** memakai trik "Is Shadow Ray → Transparent" supaya isi di dalam tetap terang dan
  bayangannya lembut. Dari sudut tertentu (frame 120/160) kaca tampak lebih abu-abu.
* **Waktu render final** di CPU 4 core ±6.5 menit/frame (≈ 27 jam untuk 240 frame), jadi
  sequence `final/` tidak dirender di sini. Dengan GPU (`DEVICE="AUTO"` memilih
  OptiX/CUDA/HIP/Metal otomatis) jauh lebih cepat.
* Lampu di-parent ke pivot kamera (ikut orbit) supaya key kiri-atas / fill kanan / rim
  belakang konsisten relatif terhadap kamera. Akibatnya bayangan di lantai ikut bergeser
  sedikit saat orbit.
