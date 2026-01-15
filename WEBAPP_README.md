# Health Tracker Web Application

A lightweight web interface for the Nutracheck health data tracker. This Flask-based web app serves interactive charts and allows you to refresh data on-demand.

## Features

- **Two interactive chart tabs:**
  - Daily Calories (food intake and exercise)
  - Mass & Body Fat (weight tracking and body fat percentage)

- **On-demand data refresh:** Click the "Refresh Data" button to fetch the latest data from Nutracheck
- **Real-time updates:** Charts automatically reload after data refresh
- **Single-user design:** Lightweight and simple, perfect for home server deployment

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables (REQUIRED)

Copy the example environment file and configure your Nutracheck credentials:

```bash
cp .env.example .env
nano .env  # or use your preferred editor
```

**Important:** You MUST set your Nutracheck email and password in the `.env` file:
```bash
NUTRACHECK_EMAIL=your_email@example.com
NUTRACHECK_PASSWORD=your_password
```

The other variables are optional and have sensible defaults.

### 3. Run the Web App

**Option A: Using the launch script (recommended)**
```bash
./run_webapp.sh
```

**Option B: Direct Python execution**
```bash
python app.py
```

The web app will be available at `http://localhost:5000`

## Deploying on a Home Server

### Auto-start with systemd

1. Edit `health-tracker.service` and update the paths:
   - Change `/home/user/Nutracheck` to your actual installation path
   - Change `User=user` to your username

2. Copy the service file:
```bash
sudo cp health-tracker.service /etc/systemd/system/
```

3. Enable and start the service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable health-tracker
sudo systemctl start health-tracker
```

4. Check status:
```bash
sudo systemctl status health-tracker
```

### Firewall Configuration

If you want to access the dashboard from other devices on your network:

```bash
# Allow port 5000
sudo ufw allow 5000/tcp
```

Then access from other devices: `http://[server-ip]:5000`

## Usage

1. **View Charts:** Navigate between tabs to see different charts
2. **Refresh Data:** Click "Refresh Data" button to fetch latest data from Nutracheck
3. **Wait for Update:** The app will show progress messages and automatically reload charts when done

## Architecture

### How It Works

1. **Data Fetching:** Uses Selenium to scrape Nutracheck.co.uk (same as original script)
2. **Data Storage:** Stores in TinyDB JSON database (`daily_data.json`)
3. **Chart Generation:** Creates Plotly HTML charts (interactive)
4. **Web Serving:** Flask serves the charts through a tabbed interface

### Files

- `app.py` - Flask web application
- `templates/index.html` - Web interface with tabs and refresh button
- `run_webapp.sh` - Launch script
- `health-tracker.service` - systemd service configuration

### Original Files (Still Used)

- `fetch_site_data.py` - Data scraping logic
- `plot_charts.py` - Chart generation
- `daily_data.json` - Data storage
- `*.html` - Generated Plotly charts (served by web app)

## Differences from Original

**Original Script:**
- Runs as a batch job
- Generates PNG charts
- Uploads to GitHub

**Web App:**
- Runs as a persistent web server
- Serves interactive HTML charts
- No GitHub upload (charts are viewed locally)
- On-demand data refresh via web button

## Troubleshooting

**Charts don't appear:**
- Click "Refresh Data" to generate initial charts
- Check that `daily_data.json` exists and has data

**Refresh button doesn't work:**
- Check Chrome WebDriver is installed
- Verify Nutracheck credentials in `.env` or source code

**Port 5000 already in use:**
- Edit `app.py` and change port in the last line: `app.run(host='0.0.0.0', port=XXXX)`

## Performance

This is a lightweight single-user application:
- Minimal CPU usage when idle
- Data refresh takes ~30-60 seconds (depends on Nutracheck scraping)
- Chart generation takes ~5-10 seconds
- Memory usage: ~100-200MB

Perfect for Raspberry Pi or any home server!
