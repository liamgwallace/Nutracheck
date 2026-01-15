import os
from flask import Flask, render_template, jsonify, send_file
from fetch_site_data import fetch_nutracheck_site_data
from plot_charts import create_charts
import threading

# Load environment variables from .env file if it exists
try:
    from dotenv import load_dotenv
    load_dotenv()
except:
    pass

app = Flask(__name__)

# Configuration
KCAL_PLOT_HTML = os.getenv('KCAL_PLOT_FILE', 'liam_kcal_plot.png').replace('.png', '.html')
MASS_FAT_PLOT_HTML = os.getenv('MASS_FAT_PLOT_FILE', 'liam_mass_fat_plot.png').replace('.png', '.html')

# Track if refresh is in progress
refresh_in_progress = False

@app.route('/')
def index():
    """Serve the main page with chart tabs"""
    return render_template('index.html')

@app.route('/chart/<chart_type>')
def get_chart(chart_type):
    """Serve the HTML chart files"""
    if chart_type == 'calories':
        if os.path.exists(KCAL_PLOT_HTML):
            return send_file(KCAL_PLOT_HTML)
        else:
            return "Chart not found. Please refresh data first.", 404
    elif chart_type == 'mass-fat':
        if os.path.exists(MASS_FAT_PLOT_HTML):
            return send_file(MASS_FAT_PLOT_HTML)
        else:
            return "Chart not found. Please refresh data first.", 404
    else:
        return "Invalid chart type", 400

@app.route('/refresh', methods=['POST'])
def refresh_data():
    """Trigger data fetch and chart regeneration"""
    global refresh_in_progress

    if refresh_in_progress:
        return jsonify({
            'status': 'in_progress',
            'message': 'Data refresh already in progress. Please wait.'
        }), 429

    def background_refresh():
        global refresh_in_progress
        try:
            refresh_in_progress = True
            print("[app] Starting data refresh...")
            fetch_nutracheck_site_data()
            print("[app] Creating charts...")
            create_charts(show_charts=False)
            print("[app] Refresh complete!")
        except Exception as e:
            print(f"[app] Error during refresh: {e}")
        finally:
            refresh_in_progress = False

    # Start refresh in background thread
    thread = threading.Thread(target=background_refresh)
    thread.start()

    return jsonify({
        'status': 'success',
        'message': 'Data refresh started. Charts will update shortly.'
    })

@app.route('/status')
def get_status():
    """Check if refresh is in progress"""
    return jsonify({
        'refreshing': refresh_in_progress
    })

if __name__ == '__main__':
    # Generate initial charts if they don't exist
    if not os.path.exists(KCAL_PLOT_HTML) or not os.path.exists(MASS_FAT_PLOT_HTML):
        print("[app] Generating initial charts...")
        try:
            fetch_nutracheck_site_data()
            create_charts(show_charts=False)
            print("[app] Initial charts created successfully")
        except Exception as e:
            print(f"[app] Warning: Could not generate initial charts: {e}")

    # Run the Flask app
    app.run(host='0.0.0.0', port=5000, debug=False)
