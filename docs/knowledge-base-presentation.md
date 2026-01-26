# Etkili Knowledge Base Kurulumu
## AI-Powered Sistemler için RAG Optimizasyonu

---

# Executive Summary

**Knowledge Base (KB)**, AI sistemlerinin "hafızasıdır". Doğru kurulmuş bir KB:
- **%40-60 daha az hallucination** (yanlış bilgi üretimi)
- **2-3x daha hızlı** içerik üretimi
- **%30 daha az manual düzeltme** ihtiyacı

Bu sunum, self-improving-content-generator projesinden öğrenilen best practice'leri ve RAG optimizasyon stratejilerini kapsamaktadır.

---

# 1. Knowledge Base Nedir?

## Basit Tanım

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│   Knowledge Base = AI'ın güvenilir bilgi kaynağı       │
│                                                         │
│   Kullanıcı Sorusu → KB'de Ara → Doğru Bilgiyle Cevap  │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## KB Olmadan vs KB ile

| Durum | KB Olmadan | KB ile |
|-------|------------|--------|
| Fiyat bilgisi | AI tahmin eder (yanlış) | Doğru fiyat döner |
| Program detayları | Genel bilgi verir | Spesifik detaylar |
| Marka sesi | Tutarsız | Tutarlı ve markalı |
| Güvenilirlik | Düşük | Yüksek |

---

# 2. Multi-Agent Mimari ve KB İlişkisi

## TheLifeCo Örneği: EPA-GONCA-ALP

```
                     ┌─────────────────────┐
                     │       EPA           │
                     │   (Orchestrator)    │
                     │                     │
                     │  Kullanıcı ile      │
                     │  diyalog yönetir    │
                     └──────────┬──────────┘
                                │
              ┌─────────────────┼─────────────────┐
              │                 │                 │
              ▼                 ▼                 ▼
     ┌────────────────┐ ┌────────────────┐ ┌────────────────┐
     │     GONCA      │ │      ALP       │ │    Review      │
     │   (Wellness)   │ │ (Storytelling) │ │    Agent       │
     │                │ │                │ │                │
     │  KB: wellness/ │ │ KB: story/     │ │  Feedback      │
     │  Temp: 0.3     │ │ Temp: 0.8      │ │  toplama       │
     └────────────────┘ └────────────────┘ └────────────────┘
```

## Temel İlke: Her Agent Kendi KB'sine Sahip

| Agent | KB Klasörü | Amaç |
|-------|------------|------|
| GONCA | `wellness/` | Program, terapi, merkez bilgileri |
| ALP | `storytelling/` | Hook, CTA, platform kuralları |
| Orchestrator | `orchestrator/` | Briefing, funnel bilgileri |

**İş Değeri:** Ayrı KB'ler = Daha az gürültü = Daha doğru sonuçlar

---

# 3. RAG (Retrieval-Augmented Generation) Nedir?

## 3 Adımlı Süreç

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   RETRIEVE  │────▶│   AUGMENT   │────▶│   GENERATE  │
│             │     │             │     │             │
│  İlgili     │     │  Context'e  │     │  Bilgiyle   │
│  bilgiyi    │     │  ekle       │     │  içerik     │
│  bul        │     │             │     │  üret       │
└─────────────┘     └─────────────┘     └─────────────┘
```

## Neden RAG?

| Yöntem | Avantaj | Dezavantaj |
|--------|---------|------------|
| Pure LLM | Hızlı | Hallucination riski yüksek |
| Fine-tuning | Özelleşmiş | Pahalı, güncelleme zor |
| **RAG** | Güncel, doğru, esnek | Optimal |

---

# 4. RAG Optimizasyonu (Ana Odak)

## 4.1 Chunking Stratejisi

### Chunk Nedir?

Büyük dokümanlar küçük parçalara (chunk) bölünür:

```
┌─────────────────────────────────────────┐
│           Büyük Doküman (10 sayfa)      │
└─────────────────────────────────────────┘
                    │
                    ▼
┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
│ Chunk 1  │ │ Chunk 2  │ │ Chunk 3  │ │ Chunk N  │
│ 500-1500 │ │ 500-1500 │ │ 500-1500 │ │ 500-1500 │
│ karakter │ │ karakter │ │ karakter │ │ karakter │
└──────────┘ └──────────┘ └──────────┘ └──────────┘
```

### Optimal Chunk Boyutu

| Boyut | Problem | İş Etkisi |
|-------|---------|-----------|
| Çok küçük (<300) | Context kaybolur | Anlamsız cevaplar |
| Çok büyük (>2000) | İlgisiz bilgi gelir | Token maliyeti artar |
| **Optimal (500-1500)** | Dengeli | Yüksek doğruluk |

### 3 Katmanlı Chunking Stratejisi

```python
# 1. Küçük dokümanlar → Olduğu gibi
if len(document) < chunk_size:
    return [document]

# 2. Normal dokümanlar → Paragraf bazlı
chunks = split_by_paragraphs(document)

# 3. Uzun paragraflar → Cümle sonu tespiti
if len(paragraph) > chunk_size:
    split_at_sentence_boundary(paragraph)
```

### Overlap (Örtüşme) Neden Önemli?

```
Overlap OLMADAN:
[Chunk 1: "Detox programı 7 gün sürer ve..."]
[Chunk 2: "...günlük 3 öğün içerir."]
→ Bilgi kaybı!

Overlap İLE:
[Chunk 1: "Detox programı 7 gün sürer ve günlük"]
[Chunk 2: "7 gün sürer ve günlük 3 öğün içerir."]
→ Context korunur!
```

**Öneri:** %10-20 overlap (100-200 karakter)

---

## 4.2 Embedding Stratejisi

### Embedding Nedir?

Metin → Sayısal vektör dönüşümü

```
"Detox programı" → [0.23, -0.45, 0.78, ..., 0.12]
                    └──────── 1024 boyut ────────┘
```

### Model Seçimi

| Model | Boyut | Maliyet | Kalite |
|-------|-------|---------|--------|
| OpenAI ada-002 | 1536 | $$ | İyi |
| **Voyage AI** | 1024 | $ | Çok iyi |
| Cohere | 1024 | $$ | İyi |

**TheLifeCo Seçimi:** Voyage AI (voyage-3-lite) - Maliyet/performans optimum

### Query vs Document Embedding

```
┌─────────────────────────────────────────────────────────┐
│                    Kritik Ayrım                         │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  embed_document() → Saklanacak bilgiler için           │
│  embed_query()    → Arama sorguları için               │
│                                                         │
│  Farklı optimize edilmiş = Daha iyi eşleşme            │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 4.3 Retrieval Kalitesi

### Arama Parametreleri

```python
search_knowledge(
    query="Detox programı fiyatı",
    match_threshold=0.7,    # Minimum benzerlik
    match_count=5,          # Maksimum sonuç
    sources=["wellness/"]   # Kaynak filtresi
)
```

### Threshold Ayarı

| Threshold | Sonuç | Ne Zaman? |
|-----------|-------|-----------|
| < 0.5 | Çok fazla, ilgisiz | Keşif amaçlı |
| **0.7** | Dengeli | Genel kullanım |
| > 0.85 | Az, çok spesifik | Hassas eşleşme |

### Kaynak Filtreleme

```
Sorgu: "Program fiyatları"

Filtresiz: Wellness + Brand + Platform kuralları (gürültülü)
Filtreli:  Sadece wellness/programs.md (temiz)
```

---

## 4.4 Maliyet Optimizasyonu

### Embedding Maliyeti Hesaplama

```
Doküman sayısı: 100
Ortalama uzunluk: 2000 karakter
Chunk sayısı: ~500

Voyage AI: $0.00006 / 1K token
Toplam: ~$0.15 (tek seferlik)
```

### Sorgu Maliyeti

```
Günlük sorgu: 1000
Token/sorgu: ~50

Günlük maliyet: ~$0.003
Aylık maliyet: ~$0.10
```

### Maliyet Azaltma Stratejileri

1. **Önbellekleme** - Sık sorulan sorgular için
2. **Batch processing** - Toplu embedding
3. **Düşük boyutlu model** - 1024 vs 1536

---

# 5. Knowledge Base Organizasyonu

## 5.1 Hiyerarşik Klasör Yapısı

```
knowledge/
├── orchestrator/           # Briefing bilgileri
│   └── funnel_stages.md
│
├── wellness/               # Sağlık & programlar
│   ├── centers/
│   │   ├── antalya.md
│   │   ├── bodrum.md
│   │   └── phuket.md
│   ├── programs.md
│   └── therapies.md
│
├── storytelling/           # İçerik kuralları
│   ├── hook_patterns.md
│   ├── cta_guidelines.md
│   └── platform_rules.md
│
└── brand/                  # Marka sesi
    ├── voice_guide.md
    └── usps.md
```

## 5.2 Dosya Tipleri ve Amaçları

| Tip | Örnek | İçerik | Kullanım |
|-----|-------|--------|----------|
| **Matrix** | `pain_solution_matrix.md` | İlişki haritaları | Eşleştirme |
| **Pattern** | `hook_patterns.md` | Şablonlar | Üretim |
| **Entity** | `center_antalya.md` | Varlık bilgisi | Doğrulama |
| **Guideline** | `cta_guidelines.md` | Kurallar | Uyum |

---

# 6. Statik vs Dinamik Bilgi

## Kritik Ayrım

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│   Statik Bilgi  → Knowledge Base'e KOY                 │
│   Dinamik Bilgi → Kullanıcıdan Real-time AL            │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## Örnekler

| Bilgi Tipi | Örnek | KB'de mi? | Neden? |
|------------|-------|-----------|--------|
| Program açıklaması | "Detox programı..." | Evet | Nadiren değişir |
| Terapi listesi | "Ozon terapi..." | Evet | Sabit |
| **Fiyatlar** | "€3500" | **HAYIR** | Sık değişir |
| **Kampanyalar** | "%20 indirim" | **HAYIR** | Geçici |
| **Tarihler** | "15-22 Ocak" | **HAYIR** | Değişken |

## İş Etkisi

| Yanlış | Sonuç | Doğru |
|--------|-------|-------|
| Eski fiyat KB'de | Müşteriye yanlış fiyat | Fiyatı sor |
| Bitmiş kampanya KB'de | Geçersiz teklif | Kampanyayı sor |

---

# 7. Signal-Derived Learning

## Kendini Geliştiren Sistem

```
                    ┌─────────────────┐
                    │  İçerik Üret    │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  Kullanıcı      │
                    │  Feedback       │
                    │  (Rating 1-5)   │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  Signal Score   │
                    │  Güncelle       │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  Gelecek        │
                    │  Retrieval'da   │
                    │  Öncelikli      │
                    └─────────────────┘
```

## Formül

```
Final Skor = Semantic Similarity × Signal Score
```

**Örnek:**
- Chunk A: Benzerlik 0.85, Signal 0.6 → **0.51**
- Chunk B: Benzerlik 0.75, Signal 0.9 → **0.675** (kazanır!)

## İş Değeri

- Zaman içinde sistem **otomatik iyileşir**
- İyi içerikler **daha fazla kullanılır**
- Kötü içerikler **otomatik elenir**

---

# 8. Hallucination Önleme

## Problem

```
AI: "TheLifeCo'nun Detox programı €1500'dır"
Gerçek: €3500

→ Müşteri güveni kaybı
→ İş kaybı
```

## Çözüm: Verification Layer

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Brief      │────▶│    GONCA     │────▶│     ALP      │
│   Topla      │     │  (Doğrula)   │     │   (Üret)     │
│              │     │              │     │              │
│              │     │  KB'de var   │     │  Sadece      │
│              │     │  mı kontrol  │     │  doğrulanmış │
│              │     │  et          │     │  bilgiyle    │
└──────────────┘     └──────────────┘     └──────────────┘
```

## Verification Result

```python
{
    "verified_facts": [
        "Detox programı 7 gün sürer",
        "Antalya merkezinde mevcut"
    ],
    "unverified_claims": [
        "Fiyat bilgisi"  # KB'de yok
    ],
    "corrections": [
        "21 gün değil, 7 gün"
    ]
}
```

## Temel İlke

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│   Fact-checking ve Content Creation AYRI AJANLARDA     │
│                                                         │
│   GONCA = Doğruluk (Temp 0.3)                          │
│   ALP = Yaratıcılık (Temp 0.8)                         │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

# 9. Best Practices Checklist

## Yapısal Kurallar

- [ ] Agent başına ayrı KB klasörü
- [ ] Hiyerarşik organizasyon
- [ ] Tutarlı dosya isimlendirme
- [ ] Metadata zenginliği

## Chunking

- [ ] Optimal boyut: 500-1500 karakter
- [ ] %10-20 overlap
- [ ] Paragraf sınırlarına saygı
- [ ] Cümle ortasında kesme yok

## Embedding

- [ ] Query/Document ayrımı
- [ ] Uygun model seçimi
- [ ] Batch processing

## Retrieval

- [ ] Threshold: 0.7 başlangıç
- [ ] Kaynak filtreleme aktif
- [ ] Signal-derived scoring

## İçerik

- [ ] Tek sorumluluk prensibi
- [ ] Statik/dinamik ayrımı
- [ ] Yapılandırılmış format
- [ ] Self-contained chunks

## Kalite

- [ ] Verification layer
- [ ] Feedback döngüsü
- [ ] Düzenli güncelleme

---

# 10. Sonraki Adımlar ve Öneriler

## Kısa Vadeli (1-2 Hafta)

1. **Mevcut KB'yi audit et**
   - Hangi bilgiler güncel?
   - Dinamik bilgi var mı?

2. **Chunk boyutlarını optimize et**
   - Test et: 500, 1000, 1500
   - Retrieval kalitesini ölç

## Orta Vadeli (1-2 Ay)

3. **Signal-derived learning aktifleştir**
   - Feedback toplama UI'ı
   - Score güncelleme mekanizması

4. **Verification layer ekle**
   - Fact-check agent
   - Unverified claim flagging

## Uzun Vadeli (3+ Ay)

5. **A/B testing framework**
   - Chunk stratejileri karşılaştırma
   - Embedding model karşılaştırma

6. **Otomatik KB güncellemeleri**
   - Stale content detection
   - Auto-refresh mekanizması

---

# Özet

## Ana Mesajlar

1. **Knowledge Base = AI'ın Doğruluk Garantisi**
   - Hallucination'ı önler
   - Tutarlılık sağlar

2. **RAG Optimizasyonu = İş Değeri**
   - Doğru chunking = Doğru cevaplar
   - İyi embedding = Hızlı retrieval
   - Signal scoring = Sürekli iyileşme

3. **Organizasyon = Ölçeklenebilirlik**
   - Agent-specific KB'ler
   - Statik/dinamik ayrımı
   - Verification layers

---

# Sorular?

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│   "İyi bir Knowledge Base, AI sisteminin              │
│    en değerli varlığıdır."                             │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

*Bu sunum, `self-improving-content-generator` projesinin analizi ve RAG best practices'lerine dayanmaktadır.*
