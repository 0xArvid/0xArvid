# RFID UID Calculator - ISO 14443 Standard

Ett Python-program för att beräkna, validera och analysera RFID UID (Unique Identifier) enligt ISO 14443-standarden för contactless smart cards.

## 🎯 Funktioner

- ✅ **Validering av UID**: Kontrollera om en UID har korrekt BCC (Block Check Character)
- ✅ **BCC-beräkning**: Generera komplett UID med korrekt checksumma
- ✅ **Detaljerad analys**: Få omfattande information om en UID
- ✅ **Flera format**: Stöd för olika inputformat (med/utan mellanslag, kolon, bindestreck)
- ✅ **ISO 14443-kompatibel**: Följer internationell standard för RFID

## 📋 UID-typer som stöds

| Typ | Längd | Beskrivning |
|-----|-------|-------------|
| Single Size UID | 4 bytes | Standard för MIFARE Classic |
| Double Size UID | 7 bytes | Förlängd UID med cascade |
| Triple Size UID | 10 bytes | Extra lång UID |

## 🚀 Användning

### Installation

Inget behöver installeras! Programmet använder bara Python 3 standardbibliotek.

```bash
# Gör skriptet körbart (Linux/Mac)
chmod +x rfid_uid_calculator.py
```

### Kommandoradsläge

```bash
# Validera en komplett UID
python rfid_uid_calculator.py validate "04 5F A2 B9"

# Generera UID med BCC från partiell UID
python rfid_uid_calculator.py generate "04 5F A2"

# Analysera en UID i detalj
python rfid_uid_calculator.py analyze "045FA2B9"

# Visa hjälp
python rfid_uid_calculator.py help
```

### Interaktivt läge

```bash
# Starta interaktivt läge
python rfid_uid_calculator.py

# Sedan kan du köra kommandon:
rfid> validate 04 5F A2 B9
rfid> generate 04 5F A2
rfid> analyze 045FA2B9
rfid> quit
```

## 📚 Exempel

### Exempel 1: Validera en UID

```bash
$ python rfid_uid_calculator.py validate "04 5F A2 B9"

✓ Valid Single UID. BCC korrekt: 0xB9
```

### Exempel 2: Generera UID med BCC

```bash
$ python rfid_uid_calculator.py generate "04 5F A2"

✓ Single Size UID:
  UID med BCC: 04 5F A2 B9
  BCC-värde: 0xB9 (decimal: 185)
  Total längd: 4 bytes
```

### Exempel 3: Analysera en UID

```bash
$ python rfid_uid_calculator.py analyze "045FA2B9"

============================================================
RFID UID Analys (ISO 14443)
============================================================

Rådata: 04 5F A2 B9
Längd: 4 bytes
Decimal: [4, 95, 162, 185]

Typ: Single Size UID (4 bytes)
UID-del: 04 5F A2
BCC (mottagen): 0xB9
BCC (beräknad): 0xB9
Status: ✓ VALID

============================================================
```

### Exempel 4: Köra testexempel

```bash
$ python test_rfid_examples.py
```

Kör en serie testexempel som visar olika användningsfall.

## 🔬 Hur BCC beräknas

BCC (Block Check Character) beräknas genom XOR-operation på alla UID-bytes:

### Single Size UID (4 bytes)
```
BCC = UID[0] ⊕ UID[1] ⊕ UID[2]

Exempel:
UID bytes: 0x04, 0x5F, 0xA2
BCC = 0x04 ⊕ 0x5F ⊕ 0xA2
    = 0b00000100 ⊕ 0b01011111 ⊕ 0b10100010
    = 0b10111001
    = 0xB9 (185 i decimal)
```

### Double Size UID (7 bytes)
```
BCC = UID[0] ⊕ UID[1] ⊕ UID[2] ⊕ UID[3] ⊕ UID[4] ⊕ UID[5]
```

### Triple Size UID (10 bytes)
```
BCC = UID[0] ⊕ UID[1] ⊕ ... ⊕ UID[8]
```

## 🎓 Om ISO 14443 Standard

ISO/IEC 14443 är en internationell standard för contactless smart cards (RFID) som opererar på 13.56 MHz.

### Viktiga egenskaper:

- **ISO 14443-3**: Definierar anti-collision och transmission protocol
- **UID-struktur**: Unik identifierare för varje kort
- **BCC**: Checksumma för att säkerställa dataintegrity
- **Cascade levels**: För att hantera längre UIDs (7 och 10 bytes)

### Vanliga korttyper:

- **MIFARE Classic**: 4 bytes UID (Single Size)
- **MIFARE Ultralight**: 7 bytes UID (Double Size)
- **MIFARE DESFire**: Kan ha 4 eller 7 bytes UID

## 📖 API-användning

Du kan också använda programmet som ett Python-bibliotek:

```python
from rfid_uid_calculator import RFIDUIDCalculator

# Skapa en calculator-instans
calculator = RFIDUIDCalculator()

# Validera en UID
valid, message = calculator.validate_single_uid("04 5F A2 B9")
print(f"Valid: {valid}, Message: {message}")

# Generera UID med BCC
success, result = calculator.generate_uid_with_bcc("04 5F A2")
print(result)

# Beräkna BCC manuellt
uid_bytes = [0x04, 0x5F, 0xA2]
bcc = calculator.calculate_bcc(uid_bytes)
print(f"BCC: 0x{bcc:02X}")

# Analysera UID
analysis = calculator.analyze_uid("045FA2B9")
print(analysis)
```

## 🔧 Tekniska detaljer

### Inputformat som stöds

Programmet accepterar UIDs i följande format:

- Med mellanslag: `04 5F A2 B9`
- Med kolon: `04:5F:A2:B9`
- Med bindestreck: `04-5F-A2-B9`
- Utan separator: `045FA2B9`
- Små eller stora bokstäver: `045fa2b9` eller `045FA2B9`

### Krav

- Python 3.6 eller senare
- Inga externa beroenden

## 🧪 Testning

Kör testexemplen för att verifiera funktionaliteten:

```bash
python test_rfid_examples.py
```

Detta kommer att köra:
- Single, Double och Triple Size UID-validering
- BCC-generering från partiella UIDs
- Detaljerad analys av UIDs
- Olika inputformat
- Feldetektering
- MIFARE Classic exempel

## 📝 Vanliga användningsfall

### 1. RFID-kortläsning
När du läser ett RFID-kort och vill verifiera att UID:n är korrekt.

### 2. RFID-emulering
När du skapar eller emulerar RFID-kort och behöver generera giltig UID med korrekt BCC.

### 3. Säkerhetsanalys
När du analyserar RFID-system och behöver validera UID-strukturer.

### 4. Debugging
När du arbetar med RFID-hårdvara och behöver felsöka kommunikationsproblem.

## 🤝 Bidra

Detta är ett öppet projekt. Förbättringar och bugfixar är välkomna!

## 📄 Licens

Detta program är fritt att använda för alla ändamål.

## 🔗 Referenser

- [ISO/IEC 14443-3:2018](https://www.iso.org/standard/73598.html) - Identification cards — Contactless integrated circuit cards — Proximity cards
- [MIFARE Documentation](https://www.nxp.com/products/rfid-nfc/mifare-hf/mifare-classic:MC_41863)
- [RFID Basics](https://en.wikipedia.org/wiki/RFID)

## 💡 Tips

1. **För MIFARE Classic**: Använd vanligtvis 4 bytes UID
2. **BCC-fel**: Om du får BCC-fel, kontrollera att du har läst rätt bytes från kortet
3. **Byte order**: ISO 14443 använder big-endian byte order
4. **Cascade Tag**: För 7-byte UIDs, första byten i cascade level 1 är 0x88

---

**Skapad för ISO 14443 RFID UID-hantering** 🔐
