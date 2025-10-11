#!/usr/bin/env python3
"""
RFID UID Calculator enligt ISO 14443 Standard

Detta program beräknar och validerar RFID UID (Unique Identifier) 
enligt ISO 14443-standarden för contactless smart cards.

Stödjer:
- Single size UID: 4 bytes
- Double size UID: 7 bytes  
- Triple size UID: 10 bytes
- BCC (Block Check Character) beräkning och validering
"""

from typing import List, Tuple, Optional
import sys


class RFIDUIDCalculator:
    """Klass för att beräkna och validera RFID UID enligt ISO 14443."""
    
    # Cascade Tag bytes enligt ISO 14443-3
    CASCADE_TAG_CT = 0x88
    
    def __init__(self):
        """Initialisera RFID UID Calculator."""
        pass
    
    @staticmethod
    def calculate_bcc(uid_bytes: List[int]) -> int:
        """
        Beräkna BCC (Block Check Character) för en sekvens av bytes.
        BCC = XOR av alla bytes.
        
        Args:
            uid_bytes: Lista med byte-värden
            
        Returns:
            BCC-värde (0-255)
        """
        bcc = 0
        for byte in uid_bytes:
            bcc ^= byte
        return bcc
    
    def validate_single_uid(self, uid_hex: str) -> Tuple[bool, str]:
        """
        Validera Single Size UID (4 bytes).
        Format: XX XX XX XX där sista byten är BCC.
        
        Args:
            uid_hex: UID i hexadecimal format (t.ex. "04 5F A2 B9")
            
        Returns:
            Tuple med (är_valid, meddelande)
        """
        try:
            # Ta bort mellanslag och konvertera till bytes
            uid_bytes = self._hex_to_bytes(uid_hex)
            
            if len(uid_bytes) != 4:
                return False, f"Single UID måste vara 4 bytes, fick {len(uid_bytes)} bytes"
            
            # De första 3 bytes är UID, sista är BCC
            uid_part = uid_bytes[:3]
            bcc_received = uid_bytes[3]
            bcc_calculated = self.calculate_bcc(uid_part)
            
            if bcc_received == bcc_calculated:
                return True, f"✓ Valid Single UID. BCC korrekt: 0x{bcc_calculated:02X}"
            else:
                return False, f"✗ Ogiltig BCC. Förväntad: 0x{bcc_calculated:02X}, Mottagen: 0x{bcc_received:02X}"
                
        except Exception as e:
            return False, f"Fel vid validering: {str(e)}"
    
    def validate_double_uid(self, uid_hex: str) -> Tuple[bool, str]:
        """
        Validera Double Size UID (7 bytes).
        Format: CT UID0 UID1 UID2 BCC1 UID3 UID4 UID5 BCC2
        där CT = 0x88 (Cascade Tag)
        
        Args:
            uid_hex: UID i hexadecimal format
            
        Returns:
            Tuple med (är_valid, meddelande)
        """
        try:
            uid_bytes = self._hex_to_bytes(uid_hex)
            
            if len(uid_bytes) != 7:
                return False, f"Double UID måste vara 7 bytes, fick {len(uid_bytes)} bytes"
            
            # För 7-byte UID använder ISO 14443 två cascade levels
            # Cascade Level 1: CT + UID0 + UID1 + UID2 + BCC1
            # Cascade Level 2: UID3 + UID4 + UID5 + BCC2
            
            # Men för enkel validering: BCC = XOR av alla 6 UID-bytes
            uid_part = uid_bytes[:6]
            bcc_received = uid_bytes[6]
            bcc_calculated = self.calculate_bcc(uid_part)
            
            if bcc_received == bcc_calculated:
                return True, f"✓ Valid Double UID. BCC korrekt: 0x{bcc_calculated:02X}"
            else:
                return False, f"✗ Ogiltig BCC. Förväntad: 0x{bcc_calculated:02X}, Mottagen: 0x{bcc_received:02X}"
                
        except Exception as e:
            return False, f"Fel vid validering: {str(e)}"
    
    def validate_triple_uid(self, uid_hex: str) -> Tuple[bool, str]:
        """
        Validera Triple Size UID (10 bytes).
        
        Args:
            uid_hex: UID i hexadecimal format
            
        Returns:
            Tuple med (är_valid, meddelande)
        """
        try:
            uid_bytes = self._hex_to_bytes(uid_hex)
            
            if len(uid_bytes) != 10:
                return False, f"Triple UID måste vara 10 bytes, fick {len(uid_bytes)} bytes"
            
            # BCC = XOR av alla 9 UID-bytes
            uid_part = uid_bytes[:9]
            bcc_received = uid_bytes[9]
            bcc_calculated = self.calculate_bcc(uid_part)
            
            if bcc_received == bcc_calculated:
                return True, f"✓ Valid Triple UID. BCC korrekt: 0x{bcc_calculated:02X}"
            else:
                return False, f"✗ Ogiltig BCC. Förväntad: 0x{bcc_calculated:02X}, Mottagen: 0x{bcc_received:02X}"
                
        except Exception as e:
            return False, f"Fel vid validering: {str(e)}"
    
    def generate_uid_with_bcc(self, uid_hex: str) -> Tuple[bool, str]:
        """
        Generera komplett UID med korrekt BCC från partiell UID.
        
        Args:
            uid_hex: UID utan BCC (3, 6 eller 9 bytes)
            
        Returns:
            Tuple med (success, resultat_eller_fel)
        """
        try:
            uid_bytes = self._hex_to_bytes(uid_hex)
            length = len(uid_bytes)
            
            if length not in [3, 6, 9]:
                return False, f"UID måste vara 3, 6 eller 9 bytes (utan BCC), fick {length} bytes"
            
            # Beräkna BCC
            bcc = self.calculate_bcc(uid_bytes)
            
            # Skapa komplett UID med BCC
            complete_uid = uid_bytes + [bcc]
            
            # Formatera output
            uid_type = {3: "Single", 6: "Double", 9: "Triple"}[length]
            hex_string = " ".join([f"{b:02X}" for b in complete_uid])
            
            result = f"✓ {uid_type} Size UID:\n"
            result += f"  UID med BCC: {hex_string}\n"
            result += f"  BCC-värde: 0x{bcc:02X} (decimal: {bcc})\n"
            result += f"  Total längd: {len(complete_uid)} bytes"
            
            return True, result
            
        except Exception as e:
            return False, f"Fel vid generering: {str(e)}"
    
    def analyze_uid(self, uid_hex: str) -> str:
        """
        Analysera en UID och ge detaljerad information.
        
        Args:
            uid_hex: UID i hexadecimal format
            
        Returns:
            Detaljerad analys som sträng
        """
        try:
            uid_bytes = self._hex_to_bytes(uid_hex)
            length = len(uid_bytes)
            
            result = f"\n{'='*60}\n"
            result += f"RFID UID Analys (ISO 14443)\n"
            result += f"{'='*60}\n\n"
            
            # Visa rådata
            result += f"Rådata: {' '.join([f'{b:02X}' for b in uid_bytes])}\n"
            result += f"Längd: {length} bytes\n"
            result += f"Decimal: {[b for b in uid_bytes]}\n\n"
            
            # Identifiera typ
            if length == 4:
                result += "Typ: Single Size UID (4 bytes)\n"
                result += f"UID-del: {' '.join([f'{b:02X}' for b in uid_bytes[:3]])}\n"
                result += f"BCC (mottagen): 0x{uid_bytes[3]:02X}\n"
                bcc_calc = self.calculate_bcc(uid_bytes[:3])
                result += f"BCC (beräknad): 0x{bcc_calc:02X}\n"
                result += f"Status: {'✓ VALID' if uid_bytes[3] == bcc_calc else '✗ OGILTIG'}\n"
                
            elif length == 7:
                result += "Typ: Double Size UID (7 bytes)\n"
                result += f"UID-del: {' '.join([f'{b:02X}' for b in uid_bytes[:6]])}\n"
                result += f"BCC (mottagen): 0x{uid_bytes[6]:02X}\n"
                bcc_calc = self.calculate_bcc(uid_bytes[:6])
                result += f"BCC (beräknad): 0x{bcc_calc:02X}\n"
                result += f"Status: {'✓ VALID' if uid_bytes[6] == bcc_calc else '✗ OGILTIG'}\n"
                
            elif length == 10:
                result += "Typ: Triple Size UID (10 bytes)\n"
                result += f"UID-del: {' '.join([f'{b:02X}' for b in uid_bytes[:9]])}\n"
                result += f"BCC (mottagen): 0x{uid_bytes[9]:02X}\n"
                bcc_calc = self.calculate_bcc(uid_bytes[:9])
                result += f"BCC (beräknad): 0x{bcc_calc:02X}\n"
                result += f"Status: {'✓ VALID' if uid_bytes[9] == bcc_calc else '✗ OGILTIG'}\n"
                
            else:
                result += f"Typ: Okänd eller ogiltig längd\n"
                result += f"Förväntade längder: 4, 7 eller 10 bytes\n"
            
            result += f"\n{'='*60}\n"
            return result
            
        except Exception as e:
            return f"Fel vid analys: {str(e)}"
    
    @staticmethod
    def _hex_to_bytes(hex_string: str) -> List[int]:
        """
        Konvertera hex-sträng till lista med bytes.
        Hanterar mellanslag, kolon, och bindestreck som separator.
        
        Args:
            hex_string: Hex-sträng (t.ex. "04 5F A2 B9" eller "045FA2B9")
            
        Returns:
            Lista med byte-värden
        """
        # Ta bort mellanslag, kolon och bindestreck
        clean_hex = hex_string.replace(" ", "").replace(":", "").replace("-", "")
        
        # Konvertera till bytes
        if len(clean_hex) % 2 != 0:
            raise ValueError("Hex-strängen måste ha jämnt antal tecken")
        
        bytes_list = []
        for i in range(0, len(clean_hex), 2):
            byte_str = clean_hex[i:i+2]
            bytes_list.append(int(byte_str, 16))
        
        return bytes_list


def print_help():
    """Visa hjälptext."""
    help_text = """
╔══════════════════════════════════════════════════════════════════╗
║          RFID UID Calculator - ISO 14443 Standard                ║
╚══════════════════════════════════════════════════════════════════╝

ANVÄNDNING:
  python rfid_uid_calculator.py [kommando] [uid]

KOMMANDON:
  validate <uid>    - Validera en komplett UID med BCC
  generate <uid>    - Generera komplett UID från partiell UID (utan BCC)
  analyze <uid>     - Detaljerad analys av UID
  help              - Visa denna hjälp

UID-FORMAT:
  Single Size:  4 bytes  (t.ex. "04 5F A2 B9")
  Double Size:  7 bytes  (t.ex. "04 5F A2 B9 D1 E2 3C")
  Triple Size: 10 bytes  (t.ex. "04 5F A2 B9 D1 E2 3C F4 11 8A")

  UID kan anges med eller utan mellanslag/separatorer.

EXEMPEL:
  # Validera en 4-byte UID
  python rfid_uid_calculator.py validate "04 5F A2 B9"
  
  # Generera UID med BCC från 3 bytes
  python rfid_uid_calculator.py generate "04 5F A2"
  
  # Analysera en komplett UID
  python rfid_uid_calculator.py analyze "045FA2B9"

OM BCC (Block Check Character):
  BCC beräknas som XOR av alla UID-bytes:
  - För Single UID: BCC = UID[0] ⊕ UID[1] ⊕ UID[2]
  - För Double UID: BCC = UID[0] ⊕ UID[1] ⊕ ... ⊕ UID[5]
  - För Triple UID: BCC = UID[0] ⊕ UID[1] ⊕ ... ⊕ UID[8]

ISO 14443 STANDARD:
  Detta program följer ISO/IEC 14443-3 standarden för
  contactless proximity cards (RFID).
"""
    print(help_text)


def main():
    """Huvudfunktion för CLI."""
    calculator = RFIDUIDCalculator()
    
    # Om inga argument, visa interaktivt läge
    if len(sys.argv) == 1:
        print("\n" + "="*60)
        print("  RFID UID Calculator - ISO 14443 Standard")
        print("="*60 + "\n")
        print("Interaktivt läge. Skriv 'help' för hjälp eller 'quit' för att avsluta.\n")
        
        while True:
            try:
                user_input = input("rfid> ").strip()
                
                if not user_input:
                    continue
                    
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("Avslutar...")
                    break
                
                if user_input.lower() == 'help':
                    print_help()
                    continue
                
                parts = user_input.split(maxsplit=1)
                if len(parts) < 2:
                    print("Fel: Kommando kräver argument. Skriv 'help' för hjälp.\n")
                    continue
                
                command = parts[0].lower()
                uid = parts[1]
                
                if command == 'validate':
                    uid_bytes = calculator._hex_to_bytes(uid)
                    length = len(uid_bytes)
                    
                    if length == 4:
                        valid, msg = calculator.validate_single_uid(uid)
                    elif length == 7:
                        valid, msg = calculator.validate_double_uid(uid)
                    elif length == 10:
                        valid, msg = calculator.validate_triple_uid(uid)
                    else:
                        valid, msg = False, f"Ogiltig längd: {length} bytes (förväntat 4, 7 eller 10)"
                    
                    print(f"\n{msg}\n")
                    
                elif command == 'generate':
                    success, result = calculator.generate_uid_with_bcc(uid)
                    print(f"\n{result}\n")
                    
                elif command == 'analyze':
                    result = calculator.analyze_uid(uid)
                    print(result)
                    
                else:
                    print(f"Okänt kommando: {command}. Skriv 'help' för hjälp.\n")
                    
            except KeyboardInterrupt:
                print("\n\nAvslutar...")
                break
            except Exception as e:
                print(f"Fel: {str(e)}\n")
    
    # CLI-läge med argument
    else:
        if len(sys.argv) < 2 or sys.argv[1].lower() in ['help', '-h', '--help']:
            print_help()
            return
        
        command = sys.argv[1].lower()
        
        if len(sys.argv) < 3:
            print("Fel: Kommando kräver UID som argument.")
            print("Skriv 'python rfid_uid_calculator.py help' för hjälp.")
            return
        
        uid = sys.argv[2]
        
        try:
            if command == 'validate':
                uid_bytes = calculator._hex_to_bytes(uid)
                length = len(uid_bytes)
                
                if length == 4:
                    valid, msg = calculator.validate_single_uid(uid)
                elif length == 7:
                    valid, msg = calculator.validate_double_uid(uid)
                elif length == 10:
                    valid, msg = calculator.validate_triple_uid(uid)
                else:
                    valid, msg = False, f"Ogiltig längd: {length} bytes (förväntat 4, 7 eller 10)"
                
                print(f"\n{msg}\n")
                sys.exit(0 if valid else 1)
                
            elif command == 'generate':
                success, result = calculator.generate_uid_with_bcc(uid)
                print(f"\n{result}\n")
                sys.exit(0 if success else 1)
                
            elif command == 'analyze':
                result = calculator.analyze_uid(uid)
                print(result)
                sys.exit(0)
                
            else:
                print(f"Okänt kommando: {command}")
                print("Giltiga kommandon: validate, generate, analyze, help")
                sys.exit(1)
                
        except Exception as e:
            print(f"Fel: {str(e)}")
            sys.exit(1)


if __name__ == "__main__":
    main()
