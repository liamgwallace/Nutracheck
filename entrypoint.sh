#!/bin/bash
set -e

echo "Starting Nutracheck Health Tracker Docker Container"
echo "=================================================="
echo "Current time: $(date)"
echo "Timezone: $(cat /etc/timezone 2>/dev/null || echo 'UTC')"
echo ""

# Check if environment variables are set
if [ -z "$GITHUB_TOKEN" ]; then
    echo "ERROR: GITHUB_TOKEN environment variable is not set!"
    exit 1
fi

if [ -z "$NUTRACHECK_EMAIL" ]; then
    echo "ERROR: NUTRACHECK_EMAIL environment variable is not set!"
    exit 1
fi

if [ -z "$NUTRACHECK_PASSWORD" ]; then
    echo "ERROR: NUTRACHECK_PASSWORD environment variable is not set!"
    exit 1
fi

echo "Environment variables validated successfully"
echo "GitHub Repo: ${GITHUB_REPO:-liamgwallace/HealthData}"
echo "Schedule: Every 4 hours (00:00, 04:00, 08:00, 12:00, 16:00, 20:00 UTC)"
echo ""

# Run immediately on startup if RUN_ON_STARTUP is set
if [ "${RUN_ON_STARTUP:-true}" = "true" ]; then
    echo "Running initial data fetch..."
    if ! python main.py; then
        echo ""
        echo "ERROR: Initial run failed!"
        if [ -f /app/chromedriver.log ]; then
            echo "ChromeDriver log:"
            echo "================="
            cat /app/chromedriver.log
        fi
        exit 1
    fi
    echo "Initial run complete at $(date)"
    echo ""
fi

# Start cron in foreground
echo "Starting cron scheduler..."
cron && tail -f /var/log/cron.log
