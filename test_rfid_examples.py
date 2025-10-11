#!/usr/bin/env python3
"""
Testexempel för RFID UID Calculator
Visar olika användningsfall enligt ISO 14443-standarden
"""

from rfid_uid_calculator import RFIDUIDCalculator


def run_examples():
    """Kör olika exempel med RFID UID Calculator."""
    calculator = RFIDUIDCalculator()
    
    print("="*70)
    print(" "*15 + "RFID UID Calculator - Testexempel")
    print("="*70 + "\n")
    
    # Exempel 1: Validera Single Size UID (4 bytes)
    print("📝 EXEMPEL 1: Validera Single Size UID (4 bytes)")
    print("-" * 70)
    uid_single = "04 5F A2 F9"  # Korrekt BCC
    valid, msg = calculator.validate_single_uid(uid_single)
    print(f"UID: {uid_single}")
    print(f"Resultat: {msg}\n")
    
    # Exempel 2: Generera Single Size UID med BCC
    print("📝 EXEMPEL 2: Generera Single Size UID från 3 bytes")
    print("-" * 70)
    uid_partial = "04 5F A2"
    success, result = calculator.generate_uid_with_bcc(uid_partial)
    print(f"Partiell UID: {uid_partial}")
    print(f"{result}\n")
    
    # Exempel 3: Validera Double Size UID (7 bytes)
    print("📝 EXEMPEL 3: Validera Double Size UID (7 bytes)")
    print("-" * 70)
    uid_double = "04 12 34 56 78 9A BC"
    uid_bytes = calculator._hex_to_bytes(uid_double)
    # Beräkna korrekt BCC
    correct_bcc = calculator.calculate_bcc(uid_bytes[:6])
    uid_double_correct = f"{uid_double[:17]} {correct_bcc:02X}"
    valid, msg = calculator.validate_double_uid(uid_double_correct)
    print(f"UID: {uid_double_correct}")
    print(f"Resultat: {msg}\n")
    
    # Exempel 4: Generera Double Size UID
    print("📝 EXEMPEL 4: Generera Double Size UID från 6 bytes")
    print("-" * 70)
    uid_partial_double = "04 12 34 56 78 9A"
    success, result = calculator.generate_uid_with_bcc(uid_partial_double)
    print(f"Partiell UID: {uid_partial_double}")
    print(f"{result}\n")
    
    # Exempel 5: Analysera olika UIDs
    print("📝 EXEMPEL 5: Detaljerad analys av UID")
    print("-" * 70)
    uid_analyze = "045FA2F9"
    result = calculator.analyze_uid(uid_analyze)
    print(result)
    
    # Exempel 6: BCC-beräkning från scratch
    print("📝 EXEMPEL 6: Manuell BCC-beräkning")
    print("-" * 70)
    uid_bytes_example = [0x04, 0x5F, 0xA2]
    bcc = calculator.calculate_bcc(uid_bytes_example)
    print(f"UID bytes: {' '.join([f'0x{b:02X}' for b in uid_bytes_example])}")
    print(f"BCC beräkning: 0x{uid_bytes_example[0]:02X} ⊕ 0x{uid_bytes_example[1]:02X} ⊕ 0x{uid_bytes_example[2]:02X} = 0x{bcc:02X}")
    print(f"Decimal: {uid_bytes_example[0]} ⊕ {uid_bytes_example[1]} ⊕ {uid_bytes_example[2]} = {bcc}")
    print(f"Binär: {uid_bytes_example[0]:08b} ⊕ {uid_bytes_example[1]:08b} ⊕ {uid_bytes_example[2]:08b} = {bcc:08b}\n")
    
    # Exempel 7: Olika format på indata
    print("📝 EXEMPEL 7: Olika inputformat (alla ekvivalenta)")
    print("-" * 70)
    formats = [
        "04 5F A2 F9",
        "04:5F:A2:F9",
        "04-5F-A2-F9",
        "045FA2F9"
    ]
    
    for fmt in formats:
        valid, _ = calculator.validate_single_uid(fmt)
        status = "✓" if valid else "✗"
        print(f"{status} Format: '{fmt}'")
    print()
    
    # Exempel 8: Felaktiga UIDs
    print("📝 EXEMPEL 8: Detektera felaktig BCC")
    print("-" * 70)
    uid_incorrect = "04 5F A2 FF"  # Felaktig BCC
    valid, msg = calculator.validate_single_uid(uid_incorrect)
    print(f"UID med felaktig BCC: {uid_incorrect}")
    print(f"Resultat: {msg}\n")
    
    # Exempel 9: MIFARE Classic UID exempel
    print("📝 EXEMPEL 9: Typiska MIFARE Classic UIDs")
    print("-" * 70)
    mifare_partial_uids = [
        "DE AD BE",  # 3 bytes, vi genererar BCC
        "CA FE BA",
        "12 34 56"
    ]
    
    for partial_uid in mifare_partial_uids:
        uid_bytes = calculator._hex_to_bytes(partial_uid)
        bcc = calculator.calculate_bcc(uid_bytes)
        complete_uid = f"{partial_uid} {bcc:02X}"
        valid, msg = calculator.validate_single_uid(complete_uid)
        print(f"UID: {complete_uid} - {msg}")
    print()
    
    print("="*70)
    print("Alla exempel klara! ✓")
    print("="*70)


if __name__ == "__main__":
    run_examples()
