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

# Decide mode: webapp (default), cron, or mcp
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

elif [ "${MODE:-webapp}" = "mcp" ]; then
    echo "=== MCP AUTOMATION SERVICE MODE ==="
    echo "AI-powered browser automation with Nutracheck"
    echo ""

    # Verify AI provider configuration
    AI_PROVIDER="${AI_PROVIDER:-claude}"
    echo "AI Provider: $AI_PROVIDER"

    case "$AI_PROVIDER" in
        claude)
            if [ -z "$ANTHROPIC_API_KEY" ]; then
                echo "ERROR: ANTHROPIC_API_KEY environment variable is required for Claude!"
                exit 1
            fi
            echo "Using Claude (Anthropic)"
            ;;
        openai)
            if [ -z "$OPENAI_API_KEY" ]; then
                echo "ERROR: OPENAI_API_KEY environment variable is required for OpenAI!"
                exit 1
            fi
            echo "Using OpenAI GPT"
            ;;
        google)
            if [ -z "$GOOGLE_API_KEY" ]; then
                echo "ERROR: GOOGLE_API_KEY environment variable is required for Google!"
                exit 1
            fi
            echo "Using Google Gemini"
            ;;
        *)
            echo "ERROR: Unknown AI_PROVIDER: $AI_PROVIDER (must be claude, openai, or google)"
            exit 1
            ;;
    esac

    echo ""
    echo "Starting MCP server..."
    echo "The server will communicate via stdio (standard input/output)"
    echo ""

    # Start MCP server - runs in foreground with stdio transport
    exec python -m nutracheck.mcp.server

else
    echo "=== WEB APP MODE ==="
    echo "Starting Flask web application on port 5000"
    echo "Access the dashboard at http://localhost:5000"
    echo ""

    # Generate initial charts if they don't exist and RUN_ON_STARTUP is true
    if [ "${RUN_ON_STARTUP:-false}" = "true" ]; then
        echo "Generating initial charts..."
        if python -c "from nutracheck.scraper import fetch_nutracheck_site_data; from nutracheck.visualizer import create_charts; fetch_nutracheck_site_data(); create_charts(show_charts=False)"; then
            echo "Initial charts created successfully at $(date)"
        else
            echo "Warning: Could not generate initial charts. You can refresh data from the web UI."
        fi
        echo ""
    fi

    # Start Flask application
    echo "Starting Flask server..."
    exec python -m nutracheck.web.app
fi
