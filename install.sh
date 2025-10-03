#!/bin/bash
# Installationsscript för Arbetsförmedlingen Automation

echo "╔════════════════════════════════════════════════════════════╗"
echo "║   Arbetsförmedlingen Automation - Installation            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Färgkoder
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Kontrollera Python
echo -n "Kontrollerar Python... "
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "${GREEN}✓ $PYTHON_VERSION${NC}"
else
    echo -e "${RED}✗ Python 3 saknas!${NC}"
    echo "Installera Python 3 först."
    exit 1
fi

# Kontrollera pip
echo -n "Kontrollerar pip... "
if command -v pip3 &> /dev/null; then
    echo -e "${GREEN}✓ pip installerad${NC}"
else
    echo -e "${RED}✗ pip saknas!${NC}"
    exit 1
fi

# Installera Python-paket
echo ""
echo "Installerar Python-paket..."
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Python-paket installerade${NC}"
else
    echo -e "${RED}✗ Fel vid installation av Python-paket${NC}"
    exit 1
fi

# Installera Playwright browsers
echo ""
echo "Installerar Playwright browsers (detta kan ta några minuter)..."
python3 -m playwright install chromium

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Playwright browsers installerade${NC}"
else
    echo -e "${YELLOW}⚠ Varning: Playwright browsers kanske inte installerades korrekt${NC}"
fi

# Skapa logs-mapp
echo ""
echo -n "Skapar logs-mapp... "
mkdir -p /workspace/logs
echo -e "${GREEN}✓${NC}"

# Kontrollera om config.json finns
echo ""
if [ -f "/workspace/config.json" ]; then
    echo -e "${GREEN}✓ config.json finns redan${NC}"
else
    echo -e "${YELLOW}⚠ config.json saknas${NC}"
    echo "  Kopiera config.example.json till config.json och redigera den:"
    echo "  cp config.example.json config.json"
    echo "  nano config.json"
fi

# Gör scripts körbara
echo ""
echo -n "Gör scripts körbara... "
chmod +x /workspace/arbetsformedlingen_bot.py
chmod +x /workspace/verify_job_search.py
chmod +x /workspace/test_manual.py
chmod +x /workspace/setup_cron.sh
echo -e "${GREEN}✓${NC}"

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                Installation klar! ✓                        ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "Nästa steg:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "1. Konfigurera systemet:"
if [ ! -f "/workspace/config.json" ]; then
    echo "   cp config.example.json config.json"
fi
echo "   nano config.json"
echo ""
echo "2. Testa systemet:"
echo "   ./test_manual.py"
echo ""
echo "3. Aktivera automation:"
echo "   ./setup_cron.sh"
echo ""
echo "Fullständig dokumentation: ARBETSFORMEDLINGEN_README.md"
echo ""
