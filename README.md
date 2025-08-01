# Mail Access Checker

Ett Python-verktyg för att testa e-postkontos tillgänglighet och säkerhet. Utvecklat för utbildningsändamål och säkerhetstestning.

## ⚠️ Viktigt meddelande

Detta verktyg är utvecklat **ENDAST** för:
- Utbildningsändamål
- Säkerhetstestning av egna system
- Penetrationstestning med explicit tillstånd

**Använd ALDRIG detta verktyg för:**
- Obehörig åtkomst till andras konton
- Brute force-attacker mot system du inte äger
- Aktiviteter som bryter mot lagar eller regler

## Funktioner

- ✅ Stöd för IMAP, SMTP och POP3 protokoll
- ✅ Multi-threading för snabb bearbetning
- ✅ Konfigurerbara timeouts och retry-mekanismer
- ✅ Färgad terminal-output för bättre läsbarhet
- ✅ Detaljerad loggning och progress-tracking
- ✅ Stöd för stora e-postleverantörer (Gmail, Outlook, Yahoo, etc.)
- ✅ Exportera resultat till fil
- ✅ Flexibel konfiguration via YAML-filer

## Installation

1. **Klona repositoriet:**
```bash
git clone <repository-url>
cd mail-access-checker
```

2. **Installera beroenden:**
```bash
pip install -r requirements.txt
```

## Användning

### Grundläggande exempel

**Testa ett enskilt konto:**
```bash
python main.py --target user@example.com --password secretpassword
```

**Testa konton från fil:**
```bash
python main.py --file accounts.txt --output results.txt
```

**Anpassad konfiguration:**
```bash
python main.py --file accounts.txt --threads 10 --timeout 45 --protocol imap
```

### Filformat

Skapa en fil `accounts.txt` med format:
```
email1@example.com:password1
email2@gmail.com:password2
email3@outlook.com:password3
# Kommentarer börjar med #
```

### Kommandoradsargument

```
positional arguments:
  ingen

optional arguments:
  -h, --help            visa hjälpmeddelande och avsluta
  --target TARGET, -t TARGET
                        Enskild e-postadress att testa
  --password PASSWORD, -p PASSWORD
                        Lösenord för enskild e-post
  --file FILE, -f FILE  Fil med e-post:lösenord kombinationer
  --config CONFIG, -c CONFIG
                        Konfigurationsfil (default: config/settings.yaml)
  --threads THREADS     Antal trådar att använda (default: 5)
  --timeout TIMEOUT     Timeout i sekunder (default: 30)
  --output OUTPUT, -o OUTPUT
                        Utdatafil för resultat
  --verbose, -v         Verbose output
  --quiet, -q           Tyst läge
  --protocol {imap,smtp,pop3,all}
                        Protokoll att testa (default: imap)
```

## Projektstruktur

```
mail-access-checker/
├── main.py                 # Huvudfil
├── requirements.txt        # Python-beroenden
├── README.md              # Denna fil
├── config/
│   └── settings.yaml      # Standardkonfiguration
├── src/
│   ├── core/
│   │   ├── config.py      # Konfigurationshantering
│   │   ├── logger.py      # Loggningssystem
│   │   └── exceptions.py  # Anpassade exceptions
│   ├── protocols/         # (Kommer snart)
│   │   ├── imap_client.py
│   │   ├── smtp_client.py
│   │   └── pop3_client.py
│   ├── auth/             # (Kommer snart)
│   ├── network/          # (Kommer snart)
│   ├── processing/       # (Kommer snart)
│   └── ui/
│       └── cli.py        # Command Line Interface
└── tests/               # (Kommer snart)
```

## Konfiguration

Standardkonfigurationen finns i `config/settings.yaml`. Du kan anpassa:

- Timeout-värden
- Antal trådar
- Protokollspecifika inställningar
- E-postleverantörer och deras servrar
- SSL/TLS-inställningar

## Utvecklingsstatus

### ✅ Klart
- [x] Grundläggande projektstruktur
- [x] Konfigurationshantering
- [x] Loggningssystem
- [x] CLI-interface
- [x] Felhantering

### 🚧 Pågående utveckling
- [ ] IMAP-protokollimplementation
- [ ] SMTP-protokollimplementation
- [ ] POP3-protokollimplementation
- [ ] Multi-threading engine
- [ ] Autentiseringssystem

### 📋 Planerat
- [ ] OAuth-stöd för moderna tjänster
- [ ] Proxy-stöd
- [ ] GUI-interface
- [ ] Avancerad rapportgenerering
- [ ] Keyword searching i e-postmeddelanden

## Bidrag

Detta är ett utbildningsprojekt. Bidrag välkomnas för:
- Buggfixar
- Säkerhetsförbättringar
- Dokumentationsförbättringar
- Nya funktioner (som följer etiska riktlinjer)

## Licens

Endast för utbildningsändamål. Se projektets licensfil för detaljer.

## Ansvarsfriskrivning

Utvecklarna av detta verktyg ansvarar inte för missbruk eller skada som orsakas av användning av detta verktyg. Användare ansvarar för att följa alla tillämpliga lagar och regler.

## Support

För frågor eller problem, skapa en issue i repositoriet.
