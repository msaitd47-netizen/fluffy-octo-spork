# Hamam Böceği Videoları — Text-to-Video Prompt Seti

Türk X/TikTok tarafında viral olan "konuşan hamam böceği" akımı için hazır
prompt seti. Buradaki promptlar **text-to-video** modelleri içindir (bkz.
"Nerede üretilir?") — bu depodaki `make_video.py` hattından
farklı bir iş: `make_video.py` sabit görsel + seslendirme + altyazı
birleştirir, buradaki promptlar ise konuşan karakterli hareketli klip üretir.
İkisini birlikte de kullanabilirsiniz (en altta "Klipleri birleştirme").

## Ton hakkında bir not

Akımın çıkış noktası, Türkleri "hamam böceği" benzetmesiyle hedef alan
aşağılayıcı bir söylemin ironiyle sahiplenilip mizaha çevrilmesi. Bu setteki
promptlar da o çizgide: mizah **kendine dönük** — maç izleme hâlleri, ev
ekonomisi, anne telefonu, komşuluk. Hiçbir etnik grubu, milleti veya
topluluğu hedef alan versiyonunu yazmayın; akımın esprisi zaten karşı tarafın
söylemini etkisiz bırakmak, aynısını üretmek değil.

## Nerede üretilir?

Bu videonun belirleyici ihtiyacı **native audio**: böceğin Türkçe repliği
görüntüyle aynı anda, aynı üretimde çıkmalı. Sonradan ses bindirmek dudak
senkronunu bozuyor ve akımın havasını kaçırıyor. Bu şartla eleyince:

| Araç | Durum |
|---|---|
| **Google Flow (Veo 3.1)** | Birinci tercih. Native diyalog + foley tek geçişte, alanın en iyisi. `labs.google/flow` |
| **Kling 3.0 Omni** | Ucuz alternatif (~$0.10/sn), çok sahneli ortak ses zaman çizelgesi. Ama native diyalogu sınırlı sayıda dili destekliyor — Türkçe listede mi, üretmeden önce doğrulayın. |
| **Sora 2** | ❌ Kullanmayın. Uygulama ve web ürünü Nisan 2026'da kapatıldı, API de Eylül 2026'da tamamen kapanıyor. |
| **Runway** | Görüntü iyi, diyalog tarafı zayıf. Bu iş için uygun değil. |

Flow erişimi **Google AI Pro** ($19.99/ay) veya **Ultra** ($249.99/ay)
aboneliğiyle geliyor; Pro'da günlük sınırlı sayıda Veo Fast üretimi var.
Ülke kullanılabilirliği değişiyor, Türkiye'den erişimi abonelik almadan önce
kontrol edin.

## Ayarlar

| Ayar | Değer | Neden |
|---|---|---|
| En-boy oranı | **16:9 yatay** | Geniş kadroda altı karakter rahat sığıyor |
| Süre | **8 saniye** | Veo/Flow klip başına üst sınır; akımın standardı |
| Ses | **native audio açık** | Böceğin konuşması modelden gelmeli, sonradan bindirilmemeli |
| Çözünürlük | 1080p+ | Yeniden yüklemede sıkışmaya karşı pay |

## Temel stil bloğu

Her promptun sonuna aynen bunu ekleyin — klipler arası görsel tutarlılığı bu
sağlıyor:

> Ultra-realistic cinematic 3D animation, photoreal cockroach with detailed
> chitin texture and translucent wings, Pixar-level facial expression and lip
> sync, expressive eyes, smooth character motion, shallow depth of field,
> subtle handheld camera, realistic practical lighting, HDR, 4K, horizontal
> 16:9 widescreen, 8 seconds.

Negatif prompt (destekleyen araçlarda):

> horror, gore, disgusting, swarm, pest infestation, blurry, distorted anatomy,
> extra limbs, watermark, text overlay, subtitles

Akım "iğrenç böcek" değil, **sevimli-absürt karakter** estetiğinde — negatif
prompt bunu tutturmak için önemli.

---

## Sahneler

Her sahne tek başına 8 saniyelik bir klip. Diyalogları tırnak içinde
bırakın; Veo/Flow tırnak içindeki repliği seslendiriyor. Replikler kısa
tutuldu (8 saniyeye ~10-12 kelime sığıyor).

**1. Milli maç — hakem kararı**
> A cockroach wearing a tiny red Turkish national team jersey sits on a worn
> living-room couch, leaning toward an old CRT television showing a football
> match. He suddenly throws both front legs in the air in disbelief, shouting
> at the screen: "Bu penaltı değilse ben hamam böceği değilim!" Warm evening
> lamp light, tea glass on the coffee table beside him.

**2. Mutfak ışığı yanınca**
> A cockroach mid-stride across a kitchen counter at 3 AM freezes completely
> as the ceiling light snaps on. He slowly turns his head toward camera,
> holds a long guilty pause, then whispers: "Yok bir şey, ben zaten
> çıkıyordum." Harsh overhead kitchen light, tiled backsplash, sudden
> silence.

**3. İlaçlama şirketi kapıda**
> A cockroach peeks through the crack under an apartment door, sees boots and
> a spray canister outside, then sprints back down a hallway yelling to his
> family: "Toplanın, toplanın! Yine geldiler!" Handheld chase-cam following
> low along the floor, dim hallway light, comedic panic energy.

**4. Çay demleme**
> A cockroach stands on a stovetop beside a traditional Turkish double
> teapot, carefully lifting the small upper pot with both front legs and
> inspecting the brew color against the light. He nods with deep satisfaction
> and says: "Tavşan kanı. İşte bu." Cozy morning kitchen, steam rising, warm
> backlight through a window.

**5. Anne telefonu**
> A cockroach lies on his back on a small couch holding a smartphone to his
> ear, visibly bracing himself. He answers with tired affection: "Yedim anne,
> yedim. Yemin ederim yedim." Soft indoor evening light, TV glow flickering
> in the background, single unbroken close-up.

**6. Market kasası — poşet parası**
> A cockroach at a supermarket checkout counter stares at the cashier in
> silent betrayal, one grocery item in front of him. He finally says, flatly:
> "Poşet de para mı ya?" Fluorescent store lighting, shallow depth of field,
> deadpan comedic timing, slow push-in on his face.

**7. Derbi galibiyeti — balkon kutlaması**
> A cockroach bursts onto a small apartment balcony at night banging a metal
> pot with a wooden spoon, screaming in pure joy: "Şampiyonuz! Şampiyonuz!"
> Neighboring apartment windows light up one by one behind him, city night
> ambience, confetti of dust in the air, energetic handheld camera.

**8. Doğalgaz faturası**
> A cockroach sits at a kitchen table under a single hanging bulb, slowly
> unfolding a long utility bill that keeps unrolling past the edge of the
> table. His expression drains as he mutters: "Kombiyi bir daha açmıyorum."
> Cold blue winter light from the window, warm bulb contrast, slow zoom out
> revealing the bill's length.

**9. Komşu kapıyı çalıyor**
> A cockroach family of four sits around a small dinner table when the
> doorbell rings. The father cockroach freezes with a fork raised and
> whispers: "Kimse ses çıkarmasın." Everyone goes still, only their antennae
> twitching. Warm dinner-table lamp light, comedic frozen tableau, soft
> handheld drift.

**10. Sabah alarmı**
> A cockroach buried under a matchbox-sized blanket slaps at a tiny alarm
> clock repeatedly, misses, and finally sits bolt upright staring at the
> time. He says with total resignation: "Bugün de olmadı." Early grey morning
> light through blinds, dust in the air, single static wide shot.

---

## Kullanım ipuçları

- **Diyalogu tırnak içinde bırakın.** Veo/Flow tırnaklı metni replik olarak
  okur; tırnağı kaldırırsanız sahne betimlemesi sanıp sessiz üretebiliyor.
- **Türkçe telaffuz** modele göre değişiyor. Tutmazsa repliği daha kısa yazın
  veya `spoken in Turkish with a natural Istanbul accent` ibaresini ekleyin.
- **Karakter tutarlılığı** için seri üretiyorsanız aynı böceği tarif eden
  cümleyi (ör. `the same cockroach with a chipped left antenna and a red
  jersey`) her prompta birebir kopyalayın. Model klipler arası hafızayı
  tutmaz.
- **Metin yazdırmayın.** Modeller Türkçe yazıyı (özellikle ç/ğ/ı/ş) bozuk
  üretiyor; kliplerde yazı istemeyin, altyazıyı sonradan gömün.
- **İlk çıktı tutmazsa** promptu uzatmak yerine tek bir değişkeni değiştirin
  (ışık, kamera, replik uzunluğu). Uzun prompt daha iyi değil, daha karışık
  sonuç veriyor.

## Klipleri birleştirme

8 saniyelik klipleri tek videoya çevirmek için (ffmpeg zaten bu deponun
gereksinimi):

```bash
# clips.txt içine sırayla:
#   file 'clip1.mp4'
#   file 'clip2.mp4'
ffmpeg -f concat -safe 0 -i clips.txt -c copy bocek_video.mp4
```

Klipler farklı çözünürlük/fps ile geldiyse `-c copy` çalışmaz; yeniden
kodlayın:

```bash
ffmpeg -f concat -safe 0 -i clips.txt \
  -vf "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:-1:-1" \
  -r 30 -c:v libx264 -crf 18 -c:a aac bocek_video.mp4
```

Üstüne Türkçe altyazı gömmek için:

```bash
ffmpeg -i bocek_video.mp4 -vf "subtitles=bocek.srt" -c:a copy bocek_final.mp4
```

Not: `bocek.srt`'yi elle yazın. Bu depodaki `export_srt.py` zamanlamayı ayrı
bir seslendirme dosyası + transcript + görsel setinden hesaplıyor; burada
diyalog klibin kendi sesinde olduğu için o akış uymuyor. Replikleri zaten siz
yazdığınız için, klip başına tek satır SRT elle yazmak birkaç dakikalık iş.
