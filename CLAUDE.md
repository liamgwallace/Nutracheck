# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is a Python-based health data tracker that scrapes nutrition and fitness data from Nutracheck.co.uk, processes the data, generates visualizations, and uploads them to GitHub. The application tracks daily calorie intake, exercise, body weight, waist measurements, and calculated body fat percentage.

## Running the Application

### Main Execution
```bash
python main.py
```

This orchestrates the full pipeline:
1. Scrapes data from Nutracheck (last 7 days of calorie data, all weight/waist measurements)
2. Processes and stores data in `daily_data.json` using TinyDB
3. Generates two PNG charts (`liam_kcal_plot.png` and `liam_mass_fat_plot.png`)
4. Uploads charts to GitHub repository

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

## Architecture

### Data Flow Pipeline

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

5. **GitHub Integration** (`git_upload.py`)
   - Uses GitHub REST API to upload/update PNG files
   - SHA-based content detection for updates vs. new uploads
   - Base64 encoding for binary file transfer

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

Credentials are hardcoded in the source files:
- Nutracheck login: `fetch_site_data.py:244-245`
- GitHub token: `main.py:11`, `git_upload.py:65`

**IMPORTANT:** These credentials are exposed in plain text. When modifying authentication code, suggest moving to environment variables or a separate configuration file.

## Dependencies

Key Python packages (no requirements.txt present):
- `selenium`: Web automation
- `beautifulsoup4`: HTML parsing
- `tinydb`: JSON-based database
- `pandas`: Data manipulation
- `plotly`: Chart generation (includes Kaleido for PNG export)
- `scipy`: Statistical analysis (linear regression, EMA)
- `matplotlib`: Alternative plotting (not actively used in main flow)
- `requests`: GitHub API calls

WebDriver:
- Chrome WebDriver required for Selenium automation

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

## Auxiliary Files

- `web_macro_tools.py`: Standalone GUI tool for recording and replaying web interactions (not used in main pipeline)
- `run/`: Contains duplicate output files and shortcuts
- `cookies.pkl`: Pickled session cookies (currently unused)
- `*.html` and `*.png`: Generated chart outputs
