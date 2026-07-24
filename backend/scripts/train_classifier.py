"""T6 — Kendi konu sınıflandırıcımızı eğitir ve 120 soruluk ÖSYM setinde ölçer.

Veri Protokolü (docs/mimari.md) bu script'te KODLA zorlanır:
- Değerlendirme seti = 2024-2026'nın 120 sorusu; eğitime ASLA girmez.
- 2018-2023 ön-etiketleri insan onayından geçmeden eğitimde kullanılmaz:
  data/osym/raw/etiket_onay.csv yoksa script eğitime başlamaz.
- AI üretimi sorular (data/uretilen_sorular.csv) yalnız eğitimde kullanılır.
- Hiperparametre seçimi YALNIZ eğitim verisi üzerinde çapraz doğrulamayla yapılır;
  değerlendirme setine model seçiminde bakılmaz (tek atış ölçüm).

Ablasyon kolları:
- yalnız ÖSYM · ÖSYM + tüm AI · ÖSYM + hedefli AI (yalnız az örnekli konulara takviye)

Çıktılar:
- backend/app/data/konu_siniflandirici.joblib  (CV'ye göre en iyi model)
- docs/siniflandirici-karsilastirma.md         (Gemini zero-shot %83.3 ile karşılaştırma)

Çalıştırma (repo kökünden):
    python backend/scripts/train_classifier.py
"""

from __future__ import annotations

import csv
import json
import sys
from collections import Counter
from pathlib import Path

import joblib
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GridSearchCV, KFold
from sklearn.pipeline import Pipeline

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "backend"))

from app.services.queries import load_topics  # noqa: E402

RAW_DIR = ROOT / "data" / "osym" / "raw"
TRANSCRIPT_CSV = RAW_DIR / "sorular_metin.csv"
APPROVAL_CSV = RAW_DIR / "etiket_onay.csv"
GENERATED_CSV = ROOT / "data" / "uretilen_sorular.csv"
EVAL_LABELS_CSV = ROOT / "data" / "osym" / "etiketleme.csv"
MODEL_PATH = ROOT / "backend" / "app" / "data" / "konu_siniflandirici.joblib"
REPORT_MD = ROOT / "docs" / "siniflandirici-karsilastirma.md"

EVAL_YEARS = {"2024", "2025", "2026"}
TRAIN_YEARS = {"2018", "2019", "2020", "2021", "2022", "2023"}
GEMINI_ZEROSHOT = 0.833  # T4 v2 ölçümü (docs/etiketleme-dogruluk-raporu.md)
RANDOM_STATE = 42
AZ_ORNEK_ESIK = 6   # ÖSYM'de bu sayıdan az örneği olan konu "az örnekli" sayılır
HEDEFLI_AI_UST = 8  # hedefli kolda konu başına en fazla bu kadar AI sorusu eklenir

PARAM_GRID = [
    {
        "tfidf__analyzer": ["word"],
        "tfidf__ngram_range": [(1, 2)],
        "tfidf__min_df": [1, 2],
        "clf__C": [1.0, 2.0, 4.0],
        "clf__class_weight": [None, "balanced"],
    },
    {
        "tfidf__analyzer": ["char_wb"],
        "tfidf__ngram_range": [(2, 5)],
        "tfidf__min_df": [2],
        "clf__C": [1.0, 2.0, 4.0],
        "clf__class_weight": [None, "balanced"],
    },
]


def math_topics() -> set[str]:
    data = load_topics()
    return set(next(s["topics"] for s in data["subjects"] if s["name"] == "Matematik"))


def load_transcripts() -> list[dict]:
    if not TRANSCRIPT_CSV.exists():
        raise SystemExit(f"Transkripsiyon dosyası yok: {TRANSCRIPT_CSV}")
    return list(csv.DictReader(TRANSCRIPT_CSV.open(encoding="utf-8")))


def load_osym_training(topics: set[str]) -> list[tuple[str, str]]:
    """2018-2023 metin+etiket — yalnız insan onayından geçmiş etiketlerle."""
    if not APPROVAL_CSV.exists():
        raise SystemExit(
            "Veri Protokolü: 2018-2023 etiketleri insan onayından geçmeden eğitim yapılamaz.\n"
            f"Beklenen dosya: {APPROVAL_CSV}\n"
            "(Ön-etiketleri gözden geçirip onay dosyasını kaydedin.)"
        )
    approvals: dict[tuple[str, str], str] = {}
    for r in csv.DictReader(APPROVAL_CSV.open(encoding="utf-8-sig")):
        final = (r.get("onay_konu") or "").strip() or (r.get("on_konu") or "").strip()
        approvals[(r["kitapcik"].strip(), r["soru_no"].strip())] = final

    rows = []
    for r in load_transcripts():
        if r["kitapcik"] not in TRAIN_YEARS:
            continue
        label = approvals.get((r["kitapcik"], r["soru_no"]))
        if label is None:
            raise SystemExit(
                f"Onay dosyasında satır eksik: {r['kitapcik']} soru {r['soru_no']}"
            )
        if label.upper() == "ATLA":
            continue
        if label not in topics:
            raise SystemExit(f"Onay dosyasında listede olmayan konu: '{label}'")
        rows.append((r["metin"], label))
    return rows


def load_generated(topics: set[str]) -> list[tuple[str, str]]:
    if not GENERATED_CSV.exists():
        return []
    rows = []
    for r in csv.DictReader(GENERATED_CSV.open(encoding="utf-8")):
        if r["konu"] in topics and r["soru"].strip():
            rows.append((r["soru"], r["konu"]))
    return rows


def load_eval(topics: set[str]) -> list[tuple[str, str]]:
    """120 değerlendirme sorusu: metin transkriptten, etiket İNSAN elinden (nihai_konu)."""
    texts = {
        (r["kitapcik"], r["soru_no"]): r["metin"]
        for r in load_transcripts()
        if r["kitapcik"] in EVAL_YEARS
    }
    rows = []
    for r in csv.DictReader(EVAL_LABELS_CSV.open(encoding="utf-8-sig")):
        key = (r["kitapcik"].strip(), r["soru_no"].strip())
        if key[0] not in EVAL_YEARS:
            continue
        label = ((r.get("nihai_konu") or "").strip() or r["konu"].strip())
        text = texts.get(key)
        if not text:
            raise SystemExit(f"Değerlendirme sorusunun metni eksik: {key}")
        if label not in topics:
            raise SystemExit(f"Etiket listede yok: {label} ({key})")
        rows.append((text, label))
    if len(rows) != 120:
        raise SystemExit(f"Değerlendirme seti 120 değil: {len(rows)}")
    return rows


def targeted_ai(osym: list[tuple[str, str]], generated: list[tuple[str, str]]):
    """Yalnız ÖSYM'de az örnekli konulara, sınırlı sayıda AI sorusu ekler."""
    osym_counts = Counter(y for _, y in osym)
    rows, added = [], Counter()
    for text, label in generated:
        if osym_counts.get(label, 0) < AZ_ORNEK_ESIK and added[label] < HEDEFLI_AI_UST:
            rows.append((text, label))
            added[label] += 1
    return rows


def fit_with_cv(
    osym_rows: list[tuple[str, str]], extra_rows: list[tuple[str, str]]
) -> tuple[Pipeline, float, str]:
    """Izgara araması; doğrulama katmanları YALNIZ gerçek ÖSYM örnekleridir.

    AI soruları yalnız eğitim katmanlarına eklenir. Böylece üç kolun CV skorları
    aynı (gerçek) dağılımda ölçülür ve karşılaştırılabilir olur — değerlendirme
    setine model seçiminde yine bakılmaz.
    """
    texts = [t for t, _ in osym_rows] + [t for t, _ in extra_rows]
    labels = [y for _, y in osym_rows] + [y for _, y in extra_rows]
    n_osym = len(osym_rows)
    extra_idx = np.arange(n_osym, len(texts))
    folds = []
    for train_o, test_o in KFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE).split(
        np.arange(n_osym)
    ):
        folds.append((np.concatenate([train_o, extra_idx]), test_o))

    pipe = Pipeline([
        ("tfidf", TfidfVectorizer(lowercase=True, sublinear_tf=True)),
        ("clf", LogisticRegression(max_iter=3000, random_state=RANDOM_STATE)),
    ])
    grid = GridSearchCV(pipe, PARAM_GRID, cv=folds, scoring="accuracy", n_jobs=-1)
    grid.fit(texts, labels)
    best = grid.best_params_
    tag = (f"{best['tfidf__analyzer']}{best['tfidf__ngram_range']}, "
           f"C={best['clf__C']}, cw={best['clf__class_weight']}")
    return grid.best_estimator_, grid.best_score_, tag


def _ai_bulgusu(results: dict) -> str:
    """Ablasyon sonucunu anlatan cümleyi gerçek sayılara göre kurar."""
    osym = results["yalnız ÖSYM"]["accuracy"]
    tum = results["ÖSYM + tüm AI"]["accuracy"]
    hedef = results["ÖSYM + hedefli AI (az örnekli konulara)"]["accuracy"]
    if tum < osym:
        cumle = ("- **AI soruların tamamını eklemek doğruluğu düşürdü** (ablasyon): üretilen "
                 "sorular gerçek ÖSYM dilinden daha kalıplı; model stil öğrenip konudan "
                 "uzaklaşabiliyor.")
        if hedef > tum:
            cumle += " Az örnekli konulara sınırlı (hedefli) takviye bu zararı azaltıyor."
    elif tum > osym:
        cumle = ("- **AI soruları eklemek doğruluğu artırdı** (ablasyon): az örnekli "
                 "konuların kapsanması stil maliyetinden ağır bastı.")
    else:
        cumle = "- **AI sorularının net etkisi nötr çıktı** (ablasyon tablosu)."
    return cumle


def evaluate(model: Pipeline, eval_rows: list[tuple[str, str]]) -> dict:
    texts = [t for t, _ in eval_rows]
    gold = [y for _, y in eval_rows]
    pred = list(model.predict(texts))
    correct = sum(1 for g, p in zip(gold, pred) if g == p)
    return {
        "accuracy": correct / len(gold),
        "correct": correct,
        "total": len(gold),
        "per_topic_err": Counter(g for g, p in zip(gold, pred) if g != p),
        "confusion": Counter((g, p) for g, p in zip(gold, pred) if g != p),
    }


def main() -> None:
    topics = math_topics()
    osym = load_osym_training(topics)
    generated = load_generated(topics)
    hedefli = targeted_ai(osym, generated)
    eval_rows = load_eval(topics)

    print(f"Eğitim (ÖSYM 2018-23, insan onaylı): {len(osym)} soru")
    print(f"AI havuzu (doğrulanmış): {len(generated)} — hedefli kolda kullanılan: {len(hedefli)}")
    print(f"Değerlendirme (2024-26, insan): {len(eval_rows)} soru\n")

    configs = {
        "yalnız ÖSYM": (osym, []),
        "ÖSYM + tüm AI": (osym, generated),
        "ÖSYM + hedefli AI (az örnekli konulara)": (osym, hedefli),
    }

    results: dict[str, dict] = {}
    best_name, best_model, best_cv = "", None, -1.0
    for name, (osym_part, extra_part) in configs.items():
        model, cv_score, tag = fit_with_cv(osym_part, extra_part)
        res = evaluate(model, eval_rows)
        res["cv"] = cv_score
        res["n_train"] = len(osym_part) + len(extra_part)
        res["params"] = tag
        results[name] = res
        print(f"{name}: CV %{cv_score * 100:.1f} → eval {res['correct']}/120 = "
              f"%{res['accuracy'] * 100:.1f}  [{tag}]")
        if cv_score > best_cv:  # model seçimi ÖSYM-katmanlı CV'ye göre — eval'e göre DEĞİL
            best_name, best_model, best_cv = name, model, cv_score

    best = results[best_name]
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(best_model, MODEL_PATH)
    MODEL_PATH.with_suffix(".json").write_text(json.dumps({
        "kol": best_name, "cv": best_cv, "eval_dogruluk": best["accuracy"],
        "egitim_boyutu": best["n_train"], "parametreler": best["params"],
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# T6 — Kendi Konu Sınıflandırıcımız vs Gemini (karşılaştırma raporu)",
        "",
        "**Soru:** Konu etiketlemeyi Gemini'ye (zero-shot) yaptırmak yerine kendi",
        "eğittiğimiz bir model aynı işi ne kadar iyi yapar?",
        "",
        "**Veri:** Eğitim = 2018-2023 ÖSYM soruları (Gemini transkripsiyonu + iki bağımsız",
        "model görüşü; çelişkiler T4 tutarlılık kurallarıyla tek tek karara bağlandı — analiz",
        "Claude destekli, nihai onay insan) ve bağımsız çözücü doğrulamasından geçmiş AI",
        "üretimi sorular. Değerlendirme = T4'teki 120 soruluk, elle etiketli 2024-2026 seti;",
        "eğitime hiçbir biçimde girmez (bu script kodla zorlar).",
        "",
        "**Yöntem dürüstlüğü:** Hiperparametreler ve kol seçimi yalnız eğitim verisinde",
        "çapraz doğrulamayla yapıldı; doğrulama katmanları her kolda yalnız gerçek ÖSYM",
        "örnekleridir (AI soruları sadece eğitim katmanlarına girer — böylece kollar aynı",
        "dağılımda, karşılaştırılabilir ölçülür). Değerlendirme setine model seçiminde",
        "bakılmadı; kayıtlı model CV'ye göre en iyi koldur.",
        "",
        "## Sonuçlar (aynı 120 soruda)",
        "",
        "| Model / kol | Eğitim boyutu | CV (ÖSYM katmanları) | Eval doğruluk |",
        "|---|---|---|---|",
        f"| Gemini 2.5 Flash zero-shot (v2 kurallı prompt) | — | — | **%{GEMINI_ZEROSHOT * 100:.1f}** |",
    ]
    for name, res in results.items():
        star = " ★" if name == best_name else ""
        lines.append(f"| TF-IDF + LogReg — {name}{star} | {res['n_train']} | "
                     f"%{res['cv'] * 100:.1f} | %{res['accuracy'] * 100:.1f} "
                     f"({res['correct']}/120) |")
    lines += [
        "",
        f"★ Kayıtlı model (`backend/app/data/{MODEL_PATH.name}`): **{best_name}** — "
        f"{best['params']}",
        "",
        "## Bulgular",
        "",
        f"- **Gemini %{GEMINI_ZEROSHOT * 100:.1f} vs bizim model %{best['accuracy'] * 100:.1f}.**"
        " 27 sınıflı problemde ~500 örnekle eğitilen klasik bir modelle milyarlarca",
        "  parametreli bir modelin farkı dürüstçe raporlanmıştır; hedef Gemini'yi geçmek",
        "  değil, farkı ve kendi modelimizin değer önerisini ölçmektir.",
        _ai_bulgusu(results),
        "- **Küçük veri notu:** ~50 örneklik doğrulama katmanlarında ±4-5 puanlık",
        "  gürültü doğaldır; CV ile eval sıralaması bu bant içinde yer değiştirebilir",
        "  (tabloda üç kol da şeffaf verilmiştir, seçim kuralı eval'e bakmaz).",
        "- **AI soruları üç modelle üretildi** (çoğunluk Gemini 2.5 Flash; son ~%20",
        "  Gemini 3 Flash / Flash-Lite — model erişim değişikliği nedeniyle) ve tamamı",
        "  bağımsız çözücü doğrulamasından geçti.",
        "- **Üründe gerçek kullanım (demo modu):** GOOGLE_API_KEY yokken yazılı sorular bu",
        "  modelle etiketlenir, sinyal düşer ve zayıflık haritası anahtarsız da işlemeye",
        "  devam eder (`app/services/classifier.py` + `/ask` akışı, testli). Anahtar varken",
        "  etiket, anlatımla birlikte Gemini'den gelir — model API'siz, ~milisaniyede,",
        "  sıfır maliyetle çalışır.",
        "",
        "## En çok hata yapılan konular (kayıtlı model)",
        "",
        "| Konu | Hata |",
        "|---|---|",
    ]
    for topic, n in best["per_topic_err"].most_common(8):
        lines.append(f"| {topic} | {n} |")
    lines += ["", "## En sık karışan çiftler (gerçek → tahmin)", ""]
    for (g, p), n in best["confusion"].most_common(8):
        lines.append(f"- {g} → {p}: {n}")
    lines += [
        "",
        "*Üretim: `backend/scripts/train_classifier.py` (seed 42, CV tabanlı seçim,",
        "deterministik). Eğitim verisi telif nedeniyle repoda değildir (data/osym/raw/).*",
    ]
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\nRapor: {REPORT_MD}")
    print(f"Model: {MODEL_PATH} ({best_name})")


if __name__ == "__main__":
    main()
