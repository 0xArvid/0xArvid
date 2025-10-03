## Arbetsförmedlingen monthly job search automation

### Overview
This automation searches Arbetsförmedlingen Platsbanken for three relevant jobs each month, using keywords and optional location from `.env`. It writes results to `outputs/jobs-YYYY-MM.json` and records completion status in `state.json`. A verification script exits non-zero if the monthly target is not complete.

### Setup
1. Create a virtual environment (Python 3.11+ recommended):
   ```bash
   python3 -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. Configure environment:
   ```bash
   cp .env.example .env
   # Edit .env to set JOB_KEYWORDS, JOB_LOCATION, MAX_JOBS, HEADLESS, etc.
   ```

Note: Login to Arbetsförmedlingen typically uses BankID and may not be automatable. The script performs public search without authentication.

### Usage
Run the job search (intended at 06:50 on the 15th, or earlier):
```bash
source .venv/bin/activate
python search_jobs.py
```

Verify completion status (intended at 21:00 on the 14th):
```bash
python verify_status.py
```

Exit codes:
- `0`: success/completed
- `2`: not completed (found fewer than required jobs)
- `3`: state or configuration issue

### Scheduling (cron)
Edit your user crontab:
```bash
crontab -e
```
Add entries (adjust paths):
```cron
# Run search at 06:50 on the 15th every month
50 6 15 * * cd /workspace/af-automation && /workspace/af-automation/.venv/bin/python /workspace/af-automation/search_jobs.py >> /workspace/af-automation/run.log 2>&1

# Pre-deadline verification at 21:00 on the 14th every month
0 21 14 * * cd /workspace/af-automation && /workspace/af-automation/.venv/bin/python /workspace/af-automation/verify_status.py >> /workspace/af-automation/verify.log 2>&1
```

If verification at 21:00 fails (exit code 2), configure an alert (e.g., email) via your system's cron/mail setup.

### Customization
- Edit `config.py` to extend configuration
- Adjust selectors in `search_jobs.py` if AF updates its site
