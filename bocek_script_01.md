# Böcek Videosu — Bölüm 1: "Nasıl gidiyor hayat?"

Kadro ve karakter blokları: `bocek_karakterler.md`
Stil bloğu, ayarlar ve birleştirme komutları: `bocek_video_prompts.md`

## Ham senaryo

| # | Karakter | Replik |
|---|---|---|
| 1 | Sait | Nasıl gidiyor hayat? |
| 2 | Mustafa | İyi ya, malum, memleketle uğraştık yine bugün. |
| 3 | Afsan | Sweetie ile date vardı, oradan geliyorum. |
| 4 | Özcan | Biz de hafta sonu konserdeydik ya, iyi dağıttık kafayı. |
| 5 | Mete | Kankaaaa aynen, Salah gelince biz de kutlamaya çıktık. |
| 6 | Tuna | *(bölüm 2 — sonradan sahneye girer)* |

Yapı: Sait soruyu açıyor, herkes sırayla giderek daha alakasız bir cevap
veriyor. Espri cevapların tırmanmasında, o yüzden sıra bozulmamalı.

## Bölümleme

Replikler kısa (~2.5-3 sn). Tek replik = tek klip yapılırsa 8 saniyenin
yarısı boş kalıyor, o yüzden ikişerli gruplandı:

| Klip | İçerik | Süre |
|---|---|---|
| 1 | Sait sorar + Mustafa cevaplar | 8 sn |
| 2 | Afsan + Özcan | 8 sn |
| 3 | Mete + sessizlik beat'i | 8 sn |

Toplam ~24 saniye. Klip 3'ün sonundaki sessizlik kasıtlı: Tuna'nın girişi
için açık bırakılmış slot.

## Ortak ortam bloğu

Üç klipte de birebir aynı kalmalı, yoksa mekân klipten klibe değişiyor:

> at night on a kitchen counter turned into a miniature Turkish tea house,
> tiny tulip-shaped tea glasses on small saucers, a stovetop double teapot
> gently steaming in the background, warm overhead light pooling on the
> counter, the rest of the kitchen dark

---

## Klip 1 — Açılış + Mustafa

> Wide establishing shot, night. Five cockroaches sit in a loose circle
> [ORTAM BLOĞU]. In the centre, a large older cockroach in a navy blue and
> bright yellow vertically striped football jersey, chipped left antenna, thin
> captain's armband on his front leg, authoritative posture, leans back,
> spreads his front legs and asks the group: "Nasıl gidiyor hayat?"
> Beside him a chubby round cockroach in a navy blue and bright yellow
> vertically striped football jersey, thick bristly moustache-like hairs above
> his mouth, cloth headband, shrugs wearily, takes a slow sip of tea and
> answers: "İyi ya, malum, memleketle uğraştık yine bugün."
> Camera slowly pushes in from the wide shot toward the two of them.
> [STİL BLOĞU]

## Klip 2 — Afsan + Özcan

> Medium two-shot, night, same location [ORTAM BLOĞU]. A small skinny
> cockroach in a navy blue and bright yellow vertically striped football
> jersey, unusually long antennae, tiny baseball cap worn backwards, tilts his
> cap and says brightly, pleased with himself: "Sweetie ile date vardı, oradan
> geliyorum."
> The camera pans right to a tall lean cockroach in a black and white
> vertically striped football jersey, an old healed scratch across his shell,
> calm sceptical expression, who nods along and adds: "Biz de hafta sonu
> konserdeydik ya, iyi dağıttık kafayı."
> Smooth lateral pan between the two speakers, others visible out of focus in
> the background. [STİL BLOĞU]

## Klip 3 — Mete + sessizlik

> Close-up, night, same location [ORTAM BLOĞU]. A short stocky broad-shelled
> cockroach in a burgundy and blue football jersey, sunglasses pushed up onto
> his forehead, slides the sunglasses down onto his eyes and says with huge
> enthusiastic energy, gesturing with both front legs: "Kankaaaa aynen, Salah
> gelince biz de kutlamaya çıktık."
> The camera pulls back to reveal the other four cockroaches, who have gone
> completely silent and are staring at him, antennae frozen mid-air, tea
> glasses halfway to their mouths. Hold the awkward silent beat until the end
> of the shot. [STİL BLOĞU]

---

## Notlar

- **[ORTAM BLOĞU]** ve **[STİL BLOĞU]** yer tutucu — üretmeden önce ilgili
  metni birebir yapıştırın, kısaltmayın.
- **Beş karakter tek karede** modelin üst sınırı. Klip 1'in geniş planında
  arkadakiler bulanık kalırsa sorun değil, önemli olan konuşanın net olması.
- **"Salah"** repliğinde model bazen gerçek bir futbolcu görselini karede
  göstermeye çalışıyor. Prompta gerektiğinde `no human characters, no real
  people shown` ekleyin.
- **Ses tonu** replikten replige değişmeli: Mustafa yorgun, Afsan neşeli ve
  kendini beğenmiş, Özcan sakin, Mete bağıra çağıra. Bunlar promptta yazılı,
  çıkmazsa tonu tarif eden sıfatı güçlendirin.
- **Klip 3'ün sonundaki sessizlik** bölüm 2'ye bağlanıyor. Bölüm 1'i tek
  başına paylaşacaksanız o beat'i kısaltın, yarım kalmış hissi veriyor.
