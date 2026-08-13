# Böcek Videosu — Karakter Kadrosu

5 böcek sahnede, 6. (Tuna) sonradan giriyor.

| # | İsim | Takım | Ayırt edici özellik |
|---|---|---|---|
| 1 | Sait | Fenerbahçe | En iri ve en yaşlı, sol anteni kırık, kaptan bandı |
| 2 | Mustafa | Fenerbahçe | Tombul, kalın bıyık kılları, alın bandı |
| 3 | Afsan | Fenerbahçe | En ufak ve sıska, upuzun antenler, şapkası ters |
| 4 | Özcan | Beşiktaş | Uzun boylu, ince, kabuğunda eski bir çizik |
| 5 | Mete | Trabzonspor | Bodur ve geniş, güneş gözlüğü alnına takılı |
| 6 | Tuna | Beşiktaş | En genç, kabuğu pırıl pırıl yeni — sonradan gelir |

Üçü aynı formayı (Fenerbahçe) giydiği için ayırt edici fiziksel özellik şart:
model sadece formaya bakarsa Sait, Mustafa ve Afsan'ı birbirine karıştırıyor.

## Forma tarifi — kulüp ismi yazmayın

Video modelleri kulüp isimlerini ve armalarını ya reddediyor ya da bozuk
üretiyor. İsim yerine **rengi tarif edin**, sonuç çok daha temiz oluyor:

| Takım | Prompt'a yazılacak |
|---|---|
| Fenerbahçe | `navy blue and bright yellow vertically striped football jersey` |
| Beşiktaş | `black and white vertically striped football jersey` |
| Trabzonspor | `burgundy and blue football jersey` |

## Karakter blokları — prompta birebir kopyalayın

Model klipler arası hafıza tutmaz. Bir karakter hangi klipte geçiyorsa, o
karakterin cümlesini o prompta **kelimesi kelimesine** aynı yapıştırın.

**Sait**
> a large older cockroach in a navy blue and bright yellow vertically striped
> football jersey, chipped left antenna, thin captain's armband on his front
> leg, authoritative posture

**Mustafa**
> a chubby round cockroach in a navy blue and bright yellow vertically striped
> football jersey, thick bristly moustache-like hairs above his mouth, cloth
> headband

**Afsan**
> a small skinny cockroach in a navy blue and bright yellow vertically striped
> football jersey, unusually long antennae, tiny baseball cap worn backwards

**Özcan**
> a tall lean cockroach in a black and white vertically striped football
> jersey, an old healed scratch across his shell, calm sceptical expression

**Mete**
> a short stocky broad-shelled cockroach in a burgundy and blue football
> jersey, sunglasses pushed up onto his forehead

**Tuna**
> a young cockroach in a black and white vertically striped football jersey,
> glossy spotless new shell, eager nervous energy

## Grup çekimi için

Hepsi aynı karede olacaksa isimleri değil, kadrodaki yerlerini tarif edin —
"five cockroaches on a worn living-room couch: (Sait bloğu), next to him
(Mustafa bloğu), ..." şeklinde soldan sağa sırayla. Altı karakteri tek karede
tutmak zor; 5 kişilik kadro üst sınır, Tuna'yı ayrı bir girişte kullanın.
