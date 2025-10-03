#!/bin/bash
# Setup script för att installera cron-jobb för Arbetsförmedlingen automation

echo "=== Setting up Arbetsförmedlingen Automation Cron Jobs ==="

# Hitta rätt Python path
PYTHON_PATH=$(which python3)
WORKSPACE_PATH="/workspace"

echo "Python path: $PYTHON_PATH"
echo "Workspace: $WORKSPACE_PATH"

# Skapa crontab entries
CRON_FILE="/tmp/arbetsformedlingen_cron"

# Skapa ny crontab fil
cat > "$CRON_FILE" << EOF
# Arbetsförmedlingen Job Search Automation
# Kör jobbsökning kl 07:00 den 15:e varje månad
0 7 15 * * $PYTHON_PATH $WORKSPACE_PATH/arbetsformedlingen_bot.py >> $WORKSPACE_PATH/logs/cron.log 2>&1

# Verifiera att jobbet är klart kl 21:00 den 15:e varje månad
0 21 15 * * $PYTHON_PATH $WORKSPACE_PATH/verify_job_search.py >> $WORKSPACE_PATH/logs/cron_verify.log 2>&1

# Backup: Kör verifiering kl 21:00 varje dag från 15:e till 17:e för att säkerställa
0 21 15-17 * * $PYTHON_PATH $WORKSPACE_PATH/verify_job_search.py >> $WORKSPACE_PATH/logs/cron_verify.log 2>&1
EOF

echo ""
echo "Crontab entries to be added:"
echo "----------------------------"
cat "$CRON_FILE"
echo "----------------------------"
echo ""

# Lägg till i befintlig crontab
(crontab -l 2>/dev/null; cat "$CRON_FILE") | crontab -

if [ $? -eq 0 ]; then
    echo "✓ Cron jobs added successfully!"
    echo ""
    echo "Schedule:"
    echo "  - Job search: 07:00 on the 15th of every month"
    echo "  - Verification: 21:00 on the 15th-17th of every month"
    echo ""
    echo "Current crontab:"
    crontab -l
else
    echo "✗ Failed to add cron jobs"
    exit 1
fi

# Rensa temporary fil
rm -f "$CRON_FILE"

echo ""
echo "Setup complete! Logs will be written to $WORKSPACE_PATH/logs/"
