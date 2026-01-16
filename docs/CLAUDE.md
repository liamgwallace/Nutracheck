# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is a Python-based health data tracker that scrapes nutrition and fitness data from Nutracheck.co.uk, processes the data, generates visualizations, and uploads them to GitHub. The application tracks daily calorie intake, exercise, body weight, waist measurements, and calculated body fat percentage.

The application supports **two deployment modes**:
1. **Batch/Cron Mode** - Scheduled execution with GitHub upload (original mode)
2. **Web App Mode** - Interactive Flask dashboard for on-demand data refresh

## Running the Application

### Web App Mode (Flask Dashboard)

**Start the web server:**
```bash
python app.py
```

Access at `http://localhost:5000`. The web interface provides:
- Two chart tabs (Calories and Mass/Fat) with interactive Plotly visualizations
- "Refresh Data" button to fetch latest data from Nutracheck on-demand
- Real-time status updates during refresh

Environment variables:
- `NUTRACHECK_EMAIL` and `NUTRACHECK_PASSWORD` (required)
- `KCAL_PLOT_FILE` and `MASS_FAT_PLOT_FILE` (optional)

### Batch/Cron Mode (GitHub Upload)

**Run the complete pipeline:**
```bash
python main.py
```

This orchestrates the full pipeline:
1. Scrapes data from Nutracheck (last 7 days of calorie data, all weight/waist measurements)
2. Processes and stores data in `daily_data.json` using TinyDB
3. Generates two PNG charts (`liam_kcal_plot.png` and `liam_mass_fat_plot.png`)
4. Uploads charts to GitHub repository

Environment variables:
- `NUTRACHECK_EMAIL` and `NUTRACHECK_PASSWORD` (required)
- `GITHUB_TOKEN` and `GITHUB_REPO` (required for upload)

### Running Individual Components

**Fetch data only (headless mode):**
```bash
python fetch_site_data.py
```

**Fetch data with visible browser:**
```bash
# Modify fetch_site_data.py __main__ to use headless=False
python fetch_site_data.py
```

**Generate charts only:**
```bash
python plot_charts.py
```

**Upload files to GitHub:**
```bash
python git_upload.py
```

### Batch Execution (Windows)
```bash
runscript.bat
```

### Docker Deployment

The application supports Docker deployment in both modes:

**Web App Mode (default):**
```bash
docker-compose up -d
# Access at http://localhost:5000
```

**Cron Mode (scheduled execution):**
```bash
# Set MODE=cron in .env file
docker-compose up -d
```

Docker uses environment variables from `.env` file. See `DOCKER_README.md` for full deployment details.

## Architecture

### Data Flow Pipeline

The core data pipeline consists of five stages, with different endpoints depending on deployment mode:

1. **Web Scraping** (`fetch_site_data.py`)
   - Uses Selenium WebDriver to automate Nutracheck login
   - Cookie management for session persistence
   - Scrapes three data sources:
     - Daily calorie diary (Breakfast, Lunch, Dinner, Snacks, Drinks, Exercise)
     - Body weight measurements
     - Waist circumference measurements

2. **Data Processing** (`fetch_site_data.py`)
   - Parses HTML with BeautifulSoup to extract structured data
   - Date normalization to ISO 8601 format (`YYYY-MM-DD`)
   - Calculates net calorie intake (food - exercise)
   - Computes body fat percentage using Army body fat formula
   - Merges weight and waist data by date

3. **Data Storage** (`fetch_site_data.py`)
   - TinyDB JSON database with two tables:
     - `daily_kcal`: Date, meal categories, Exercise, net_kcal
     - `daily_mass_waist`: Date, Mass, Waist, Navy_fat (body fat %)
   - Updates existing entries or inserts new ones based on date

4. **Visualization** (`plot_charts.py`)
   - Uses Plotly for interactive charts (HTML) and static images (PNG)
   - Two main charts:
     - **Calorie Chart**: Stacked bar chart with 7-day EMA, 1500 kcal goal line
     - **Mass/Fat Chart**: Dual Y-axis with trend lines and weight loss goal projection
   - Custom EMA calculation that handles missing/zero values

5. **Output** (mode-dependent)
   - **Batch/Cron Mode**: `git_upload.py` uploads PNG files to GitHub via REST API
   - **Web App Mode**: `app.py` serves HTML charts through Flask with on-demand refresh

### Application Modes

**Batch/Cron Mode (`main.py`):**
- Entry point for scheduled execution
- Calls: fetch_site_data → plot_charts → git_upload
- Generates PNG charts for GitHub upload
- Requires `GITHUB_TOKEN` and `GITHUB_REPO`

**Web App Mode (`app.py`):**
- Flask server with REST endpoints
- Routes:
  - `/` - Main page with tabbed interface (`templates/index.html`)
  - `/chart/<chart_type>` - Serves HTML chart files
  - `/refresh` (POST) - Triggers background data fetch in separate thread
  - `/status` - Returns refresh progress status
- Generates HTML charts for interactive viewing
- Uses threading to prevent blocking during data refresh

### Key Data Structures

**Daily Calorie Entry:**
```python
{
    'Date': '2024-01-15',
    'Breakfast': 314.0,
    'Lunch': 655.0,
    'Dinner': 486.0,
    'Snacks': 0.0,
    'Drinks': 0.0,
    'Exercise': 0.0,
    'net_kcal': 1455.0
}
```

**Mass/Waist Entry:**
```python
{
    'Date': '2024-01-31',
    'Mass': 97.8,
    'Waist': 100.0,
    'Navy_fat': 24.7  # Body fat percentage
}
```

### Authentication & Credentials

The application supports both environment variables (recommended) and hardcoded credentials (legacy):

**Environment Variables (Recommended):**
- `NUTRACHECK_EMAIL` - Nutracheck login email
- `NUTRACHECK_PASSWORD` - Nutracheck password
- `GITHUB_TOKEN` - GitHub Personal Access Token (required for batch/cron mode)
- `GITHUB_REPO` - Target repository in format `username/repository`

Both `fetch_site_data.py` and `main.py` attempt to load environment variables from a `.env` file using `python-dotenv`. If environment variables are not set, the code falls back to hardcoded values in:
- Nutracheck login: `fetch_site_data.py` (around line 244-245)
- GitHub token: `main.py:14`, `git_upload.py` (around line 65)

**IMPORTANT:** When modifying authentication code, prefer environment variables. Never commit `.env` files to version control.

## Dependencies

Key Python packages:
- `selenium`: Web automation
- `beautifulsoup4`: HTML parsing
- `tinydb`: JSON-based database
- `pandas`: Data manipulation
- `plotly`: Chart generation (includes Kaleido for PNG export)
- `scipy`: Statistical analysis (linear regression, EMA)
- `flask`: Web server for dashboard mode
- `python-dotenv`: Environment variable management
- `requests`: GitHub API calls
- `matplotlib`: Alternative plotting (not actively used in main flow)

WebDriver:
- Chrome WebDriver required for Selenium automation
- In Docker, Chrome and ChromeDriver are automatically installed

## Environment Configuration

All configuration is managed through environment variables, loaded from `.env` file:

**Required for All Modes:**
- `NUTRACHECK_EMAIL` - Nutracheck account email
- `NUTRACHECK_PASSWORD` - Nutracheck account password

**Required for Batch/Cron Mode:**
- `GITHUB_TOKEN` - GitHub Personal Access Token with `repo` scope
- `GITHUB_REPO` - Target repository (format: `username/repository`)

**Optional:**
- `MODE` - Deployment mode: `webapp` (default) or `cron`
- `KCAL_PLOT_FILE` - Calorie chart filename (default: `liam_kcal_plot.png`)
- `MASS_FAT_PLOT_FILE` - Weight/fat chart filename (default: `liam_mass_fat_plot.png`)
- `DATA_FILE` - JSON database filename (default: `daily_data.json`)
- `COOKIES_FILE` - Cookie storage filename (default: `cookies.pkl`)
- `TZ` - Timezone for Docker cron (default: `UTC`)
- `RUN_ON_STARTUP` - Run immediately when container starts
  - Cron mode: `true` (default)
  - Web app mode: `false` (default, use refresh button instead)
- `HOST_PORT` - Web app port mapping (default: `5000`)

## Important Implementation Details

### Body Fat Calculation
Uses Army body fat formula (not Navy, despite variable naming):
```python
Army_fat = (86.010 * log10(waist - neck)) - (70.041 * log10(height)) + 36.76
```
Constants: height=178cm, neck=41.5cm

### EMA Calculation
Custom exponential moving average that resets on NaN/zero values rather than interpolating. See `calculate_ema()` in `plot_charts.py:31-50`.

### Date Handling
All dates converted to `YYYY-MM-DD` format for consistency. Source dates from Nutracheck are in format `%A %d %B %Y` (e.g., "Monday 15 January 2024").

### Cookie Management
Session cookies saved to `cookies.pkl` but currently disabled (see `fetch_site_data.py:238`). The code always performs fresh login.

### Chart Styling
Both charts use consistent dark theme (`#343434` background) with custom color schemes:
- Calorie chart: Purple/green gradient for meal categories
- Mass/Fat chart: Green (mass) and purple (body fat) with trend lines extending to Nov 2027

## Project Files

**Core Python Modules:**
- `main.py` - Batch/cron mode entry point (fetch → plot → upload)
- `app.py` - Web app mode entry point (Flask server)
- `fetch_site_data.py` - Web scraping and data processing
- `plot_charts.py` - Chart generation (HTML and PNG)
- `git_upload.py` - GitHub upload functionality

**Web App:**
- `templates/index.html` - Web dashboard UI with tabbed charts

**Documentation:**
- `README.md` - User-facing setup and usage guide
- `WEBAPP_README.md` - Web app specific documentation
- `DOCKER_README.md` - Docker deployment guide
- `PORTAINER_DEPLOY.md` - Portainer-specific instructions

**Auxiliary:**
- `web_macro_tools.py` - Standalone GUI tool for web interaction recording (not used in pipeline)
- `run/` - Contains duplicate output files and shortcuts
- `runscript.bat` - Windows batch execution script
- `cookies.pkl` - Pickled session cookies (currently unused)
- `daily_data.json` - TinyDB database (generated)
- `*.html` and `*.png` - Generated chart outputs (generated)
