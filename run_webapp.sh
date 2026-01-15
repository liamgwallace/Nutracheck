#!/bin/bash
# Health Tracker Web App Launcher

echo "Starting Health Tracker Web App..."

# Change to script directory
cd "$(dirname "$0")"

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Check if required packages are installed
if ! python -c "import flask" 2>/dev/null; then
    echo "Flask not found. Installing dependencies..."
    pip install -r requirements.txt
fi

# Run the web application
echo "Starting Flask server on http://0.0.0.0:5000"
echo "Access the dashboard at http://localhost:5000"
echo "Press Ctrl+C to stop the server"
echo ""

python app.py
