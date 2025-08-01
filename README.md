# Mail Access Checker

Ett komplett Python-program för att verifiera e-postadresser utan att skicka några meddelanden. Inspirerat av verktyg som "mail access checker by xrisky" men byggt från grunden med moderna Python-tekniker.

## Funktioner

✅ **Syntax validering** - Kontrollerar om email-adressen följer RFC 5322 standarden  
✅ **DNS validering** - Verifierar MX records och domänens existens  
✅ **SMTP verifiering** - Ansluter till mail-servern för att validera mottagarens existens  
✅ **Disposable email detektion** - Identifierar temporära/engångs email-tjänster  
✅ **Role account detektion** - Upptäcker administrativa email-adresser (admin, support, etc.)  
✅ **Catch-all detektion** - Kontrollerar om domänen accepterar alla email-adresser  
✅ **Bulk verifiering** - Parallell bearbetning av stora email-listor  
✅ **Export funktioner** - Spara resultat som CSV eller JSON  
✅ **Grafiskt gränssnitt** - Användarvänligt GUI med tkinter  
✅ **Kommandorad interface** - Kraftfull CLI för automatisering  

## Installation

### Förutsättningar
- Python 3.7 eller senare
- Internetuppkoppling
- Öppen port 25 (för SMTP-verifiering)

### Steg 1: Klona eller ladda ner filerna
```bash
# Om du har git
git clone <repository-url>
cd mail-access-checker

# Eller ladda ner filerna manuellt
```

### Steg 2: Installera beroenden
```bash
pip install -r requirements.txt
```

## Användning

### Kommandoradsgränssnitt

#### Kontrollera en enskild email:
```bash
python mail_access_checker.py example@gmail.com
```

#### Kontrollera emails från fil:
```bash
python mail_access_checker.py -f emails.txt
```

#### Exportera resultat:
```bash
# Exportera som CSV
python mail_access_checker.py -f emails.txt --export csv

# Exportera som JSON
python mail_access_checker.py example@gmail.com --export json
```

#### Avancerade alternativ:
```bash
# Anpassa timeout och antal workers
python mail_access_checker.py -f emails.txt --timeout 15 --workers 10

# Använd anpassad "from" email
python mail_access_checker.py example@gmail.com --from-email myemail@mydomain.com
```

#### Fullständig hjälp:
```bash
python mail_access_checker.py --help
```

### Grafiskt gränssnitt

Starta GUI-versionen:
```bash
python mail_checker_gui.py
```

GUI:n erbjuder:
- Enkel email-verifiering med realtidsresultat
- Bulk-verifiering genom att ladda text-filer
- Progress bar för långvariga operationer
- Visuell presentation av resultat
- Export-funktioner med fildialoger
- Inställningar för timeout och antal workers

## Filformat för bulk-verifiering

Skapa en textfil med en email-adress per rad:

```
example1@gmail.com
user@company.com
test@disposable-email.com
admin@domain.org
```

## Resultat förklaring

### Fält i resultatet:

- **is_valid_syntax**: Om email-adressen följer korrekt format
- **domain_exists**: Om domänen existerar och har mail-servrar
- **smtp_valid**: Om mail-servern accepterar meddelanden till denna adress
- **is_disposable**: Om det är en temporär/engångs email-tjänst
- **is_role_account**: Om det är en administrativ email (admin, support, etc.)
- **is_catch_all**: Om domänen accepterar alla email-adresser
- **mx_records**: Lista över mail-servrar för domänen
- **error_message**: Felmeddelande om något gick fel
- **check_duration**: Tid det tog att verifiera (i sekunder)

### Exempel på utdata:

```
============================================================
Email: example@gmail.com
============================================================
✓ Valid syntax: True
✓ Domain exists: True
✓ SMTP valid: True
✓ Is disposable: False
✓ Is role account: False
✓ Is catch-all: False
MX Records: gmail-smtp-in.l.google.com., alt1.gmail-smtp-in.l.google.com.
Check duration: 2.345s
```

## Teknisk information

### Hur verifieringen fungerar:

1. **Syntax kontroll**: Använder regex för att validera email-format enligt RFC 5322
2. **DNS lookup**: Söker MX records för domänen, faller tillbaka på A records
3. **SMTP handshake**: Ansluter till mail-servern och simulerar email-sändning
4. **Catch-all test**: Testar en slumpmässig email för att upptäcka catch-all domäner
5. **Blacklist kontroll**: Jämför mot kända disposable email-providers

### Protokoll som används:
- **DNS**: För domän- och MX record-upplösning
- **SMTP**: För mail-server verifiering (port 25)
- **TCP**: För nätverksanslutningar

## Begränsningar och tips

### Vanliga problem:

1. **Port 25 blockerad**: Många ISP:er blockerar utgående SMTP-trafik
   - **Lösning**: Använd en VPS eller molntjänst

2. **Timeout errors**: Vissa mail-servrar är långsamma
   - **Lösning**: Öka timeout-värdet med `--timeout`

3. **"Connection refused"**: Brandvägg eller blockerad IP
   - **Lösning**: Testa från en annan IP-adress

4. **Greylisting**: Mail-servern försenar första anslutningen
   - **Lösning**: Programmet hanterar detta automatiskt

### Prestanda tips:

- Använd fler workers för större listor: `--workers 15`
- Minska timeout för snabbare genomgång: `--timeout 5`
- Kör bulk-verifieringar under lågtrafik-timmar

## Säkerhet och etik

⚠️ **Viktigt**: Detta verktyg ska användas ansvarsfullt

- Använd endast för legitima ändamål (rensa egna email-listor, etc.)
- Respektera andras servrar - överbelasta inte med för många förfrågningar
- Följ GDPR och andra dataskyddslagar
- Använd inte för spam eller skadlig verksamhet

## Utveckling och anpassning

### Lägga till fler disposable email-providers:

Redigera `disposable_domains` set i `MailAccessChecker` klassen:

```python
self.disposable_domains = {
    '10minutemail.com', 
    'tempmail.org',
    'your-new-domain.com'  # Lägg till här
}
```

### Anpassa role accounts:

Redigera `role_accounts` set:

```python
self.role_accounts = {
    'admin', 
    'support',
    'your-custom-role'  # Lägg till här
}
```

### Bygga egen GUI:

Grundklassen `MailAccessChecker` kan användas i andra gränssnitt:

```python
from mail_access_checker import MailAccessChecker

checker = MailAccessChecker(timeout=10)
result = checker.check_email("test@example.com")
print(f"Valid: {result.smtp_valid}")
```

## Felsökning

### Debug-läge:

Lägg till debug-utskrifter genom att modifiera koden eller använd Python's logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Vanliga felkoder:

- **SMTP 550**: Permanent fel - email existerar inte
- **SMTP 421**: Temporärt fel - försök igen senare  
- **SMTP 450**: Greylisting - servern försenar anslutningen
- **Connection timeout**: Nätverksproblem eller blockerad port

## Licens

Detta projekt är skapat som ett utbildningsexempel. Använd det fritt för egna projekt men ta ansvar för hur du använder det.

## Bidrag

För att förbättra detta verktyg:

1. Lägg till fler disposable email-providers
2. Förbättra error handling
3. Optimera prestanda
4. Lägg till fler export-format
5. Förbättra GUI:et

## Support

Om du stöter på problem:

1. Kontrollera att port 25 är öppen
2. Testa med en annan email-adress
3. Kontrollera internet-uppkopplingen
4. Läs felmeddelandet noggrant

---

**Byggt med kärlek för Python-communityt! 🐍💙**
