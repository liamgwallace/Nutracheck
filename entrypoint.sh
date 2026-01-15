#!/bin/bash
set -e

echo "Starting Nutracheck Health Tracker Docker Container"
echo "=================================================="
echo "Mode: ${MODE:-webapp}"
echo "Current time: $(date)"
echo "Timezone: $(cat /etc/timezone 2>/dev/null || echo 'UTC')"
echo ""

# Check required environment variables
if [ -z "$NUTRACHECK_EMAIL" ]; then
    echo "ERROR: NUTRACHECK_EMAIL environment variable is not set!"
    exit 1
fi

if [ -z "$NUTRACHECK_PASSWORD" ]; then
    echo "ERROR: NUTRACHECK_PASSWORD environment variable is not set!"
    exit 1
fi

echo "Environment variables validated successfully"
echo ""

# Decide mode: webapp (default) or cron
if [ "${MODE:-webapp}" = "cron" ]; then
    echo "=== CRON MODE ==="

    # Check GITHUB_TOKEN for cron mode
    if [ -z "$GITHUB_TOKEN" ]; then
        echo "ERROR: GITHUB_TOKEN environment variable is required for cron mode!"
        exit 1
    fi

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

else
    echo "=== WEB APP MODE ==="
    echo "Starting Flask web application on port 5000"
    echo "Access the dashboard at http://localhost:5000"
    echo ""

    # Generate initial charts if they don't exist and RUN_ON_STARTUP is true
    if [ "${RUN_ON_STARTUP:-false}" = "true" ]; then
        echo "Generating initial charts..."
        if python -c "from fetch_site_data import fetch_nutracheck_site_data; from plot_charts import create_charts; fetch_nutracheck_site_data(); create_charts(show_charts=False)"; then
            echo "Initial charts created successfully at $(date)"
        else
            echo "Warning: Could not generate initial charts. You can refresh data from the web UI."
        fi
        echo ""
    fi

    # Start Flask application
    echo "Starting Flask server..."
    exec python app.py
fi
