# Arbetsförmedlingen Automatisk Jobbsökning 🤖

Automatiserad lösning för att söka och hitta jobb på Arbetsförmedlingen enligt schema.

## 📋 Översikt

Detta system automatiskt:
- Loggar in på Arbetsförmedlingen (valfritt)
- Söker efter 3 relevanta jobb baserat på dina sökord
- Körs automatiskt kl **07:00 den 15:e varje månad**
- Verifierar att jobbet är klart kl **21:00 samma dag**
- Sparar resultat och status för uppföljning

## 🚀 Installation

### 1. Installera beroenden

```bash
# Installera Python-paket
pip install -r requirements.txt

# Installera Playwright browsers
python -m playwright install chromium
```

### 2. Konfigurera systemet

Redigera `config.json` och fyll i dina uppgifter:

```json
{
  "email": "din.email@exempel.se",
  "password": "ditt_lösenord",
  "login_required": false,
  "search_terms": [
    "Python utvecklare",
    "Backend utvecklare",
    "Automation engineer"
  ],
  "location": "Stockholm"
}
```

**Viktiga fält:**
- `email`: Din email kopplad till Comet och Arbetsförmedlingen
- `password`: Lösenord (om inloggning krävs)
- `login_required`: Sätt till `true` om du behöver logga in (OBS: BankID kan krävas)
- `search_terms`: Lista med sökord för jobb du söker
- `location`: Plats där du söker jobb (valfritt)

### 3. Installera cron-jobb

```bash
# Gör setup-scriptet körbart
chmod +x setup_cron.sh

# Kör setup
./setup_cron.sh
```

Detta skapar två cron-jobb:
- **07:00 den 15:e varje månad**: Kör jobbsökning
- **21:00 den 15:e varje månad**: Verifierar att sökningen är klar

### 4. Gör scripts körbara

```bash
chmod +x arbetsformedlingen_bot.py
chmod +x verify_job_search.py
```

## 🧪 Testa systemet

Innan du litar på automatiken, testa manuellt:

```bash
# Kör jobbsökning
python3 arbetsformedlingen_bot.py

# Verifiera resultat
python3 verify_job_search.py
```

## 📁 Filstruktur

```
/workspace/
├── arbetsformedlingen_bot.py      # Huvudscript för jobbsökning
├── verify_job_search.py           # Verifieringsscript
├── config.json                    # Din konfiguration (HEMLIG!)
├── config.example.json            # Exempel på konfiguration
├── setup_cron.sh                  # Installerar cron-jobb
├── requirements.txt               # Python-beroenden
├── ARBETSFORMEDLINGEN_README.md   # Denna fil
├── logs/                          # Loggfiler
│   ├── arbetsformedlingen.log     # Bot-loggar
│   ├── cron.log                   # Cron jobbsökning loggar
│   └── cron_verify.log           # Cron verifiering loggar
├── job_search_results.json        # Hittade jobb (genereras)
├── job_search_status.json         # Status (genereras)
└── notification.txt               # Verifieringsnotis (genereras)
```

## 📊 Resultat och Status

### job_search_results.json
Innehåller alla hittade jobb:

```json
{
  "timestamp": "2025-10-15T07:05:32",
  "jobs": [
    {
      "title": "Python utvecklare",
      "company": "Tech AB",
      "url": "https://...",
      "search_term": "Python utvecklare",
      "found_at": "2025-10-15T07:05:30"
    }
  ],
  "count": 3
}
```

### job_search_status.json
Status för senaste sökningen:

```json
{
  "timestamp": "2025-10-15T07:05:32",
  "status": "success",
  "message": "Hittade 3 jobb",
  "jobs_found": 3,
  "month": 10,
  "year": 2025
}
```

## 🔍 Kontrollera status

### Se loggar

```bash
# Senaste jobbsökning
tail -f logs/arbetsformedlingen.log

# Cron-loggar
tail -f logs/cron.log

# Verifiering
tail -f logs/cron_verify.log
```

### Kontrollera cron-jobb

```bash
# Lista alla cron-jobb
crontab -l

# Ta bort alla cron-jobb (om nödvändigt)
crontab -r
```

## ⚠️ Viktiga noteringar

### Arbetsförmedlingens inloggning
Arbetsförmedlingen kan kräva **BankID** för inloggning, vilket inte kan automatiseras helt. Alternativen är:

1. **Utan inloggning** (rekommenderat för start):
   - Sätt `"login_required": false` i config.json
   - Systemet söker jobb utan att logga in
   - Fungerar för att hitta jobb, men kanske inte för att spara favoriter

2. **Med manuell inloggning**:
   - Logga in manuellt och spara session (mer avancerat)
   - Kräver cookie/session-hantering

3. **API-integration** (framtida):
   - Använd Arbetsförmedlingens API om tillgängligt

### Webbplatsändringar
Om Arbetsförmedlingens webbplats ändras kan scriptet behöva uppdateras. Kolla loggarna om något går fel.

### Säkerhet
- **Lägg ALDRIG in config.json i git** (den innehåller lösenord!)
- Använd stark lösenord
- Håll systemet uppdaterat

## 🛠️ Felsökning

### Problem: Inga jobb hittas
```bash
# Kontrollera loggar
cat logs/arbetsformedlingen.log

# Testa manuellt med debug
python3 arbetsformedlingen_bot.py
```

**Lösning**: Justera `search_terms` i config.json

### Problem: Cron-jobbet körs inte
```bash
# Kontrollera att cron är aktiverat
sudo systemctl status cron

# Kontrollera crontab
crontab -l
```

### Problem: Playwright fungerar inte
```bash
# Installera om browsers
python -m playwright install chromium

# Installera systemdependencies
python -m playwright install-deps
```

## 📈 Nästa steg

Möjliga förbättringar:
- [ ] Email-notiser när jobb hittas
- [ ] Automatisk ansökan till jobb
- [ ] Bättre felhantering för BankID
- [ ] Dashboard för att se resultat
- [ ] Integration med CV-databas

## 📞 Support

Om du stöter på problem:
1. Kolla loggfilerna i `/workspace/logs/`
2. Testa manuell körning först
3. Verifiera att alla beroenden är installerade
4. Kontrollera att config.json är korrekt

## 📄 Licens

Fri att använda och modifiera för personligt bruk.

---

**Skapad**: 2025-10-03  
**Version**: 1.0  
**Författare**: 0xArvid
