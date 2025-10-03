# 🚀 Snabbstart - Arbetsförmedlingen Automation

## Installera på 5 minuter

### 1. Installera beroenden
```bash
pip install -r requirements.txt
python -m playwright install chromium
```

### 2. Konfigurera
```bash
# Redigera config.json och fyll i:
nano config.json
```

Fyll i minst detta:
- `search_terms`: Lägg till jobb du söker (t.ex. "Python utvecklare")
- `location`: Din stad (valfritt)

### 3. Testa
```bash
./test_manual.py
```

Om testet går bra, fortsätt:

### 4. Aktivera automation
```bash
./setup_cron.sh
```

Klart! ✓

## Schema
- **07:00 den 15:e varje månad**: Söker 3 jobb automatiskt
- **21:00 den 15:e varje månad**: Verifierar att det är klart

## Kontrollera resultat
```bash
# Se senaste jobben
cat job_search_results.json

# Se loggar
tail -f logs/arbetsformedlingen.log
```

## Hjälp?
Läs [ARBETSFORMEDLINGEN_README.md](ARBETSFORMEDLINGEN_README.md) för fullständig dokumentation.
