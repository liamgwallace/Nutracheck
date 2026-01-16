# Docker Deployment Guide

The Nutracheck Health Tracker can run in two modes:

## Mode 1: Web App (Default)

Interactive web dashboard for viewing charts and refreshing data on-demand.

**Quick Start:**
```bash
# Create .env file with credentials
cat > .env << EOF
NUTRACHECK_EMAIL=your_email@example.com
NUTRACHECK_PASSWORD=your_password
EOF

# Start with docker-compose
docker-compose up -d

# Access at http://localhost:5000
```

**Features:**
- Web interface with tabbed charts
- On-demand data refresh button
- Real-time status updates
- Port 5000 exposed

**For Portainer deployment, see [PORTAINER_DEPLOY.md](PORTAINER_DEPLOY.md)**

## Mode 2: Cron/Batch

Original scheduled mode - fetches data every 4 hours and uploads to GitHub.

**Usage:**
```bash
# Set MODE=cron in .env
cat > .env << EOF
MODE=cron
NUTRACHECK_EMAIL=your_email@example.com
NUTRACHECK_PASSWORD=your_password
GITHUB_TOKEN=your_token_here
GITHUB_REPO=username/repository
RUN_ON_STARTUP=true
EOF

# Start with docker-compose
docker-compose up -d
```

**Features:**
- Runs on schedule (every 4 hours)
- Uploads charts to GitHub
- No web interface
- No port exposure needed

## Environment Variables

### Required (Both Modes)
- `NUTRACHECK_EMAIL` - Your Nutracheck login email
- `NUTRACHECK_PASSWORD` - Your Nutracheck password

### Mode Selection
- `MODE` - Set to `webapp` (default) or `cron`

### Cron Mode Only
- `GITHUB_TOKEN` - GitHub personal access token (required for cron mode)
- `GITHUB_REPO` - Target repository (e.g., username/repo)
- `RUN_ON_STARTUP` - Run immediately on start (default: true for cron)

### Web App Mode
- `RUN_ON_STARTUP` - Generate charts on startup (default: false, use refresh button instead)
- `HOST_PORT` - Host port for web access (default: 5000)

### Optional (Both Modes)
- `TZ` - Timezone (e.g., America/New_York, Europe/London)
- `DATA_FILE` - Path to data JSON file
- `KCAL_PLOT_FILE` - Path to calorie chart
- `MASS_FAT_PLOT_FILE` - Path to mass/fat chart
- `COOKIES_FILE` - Path to cookies file

## Docker Commands

**Build locally:**
```bash
docker build -t nutracheck-tracker .
```

**Run web app:**
```bash
docker run -d \
  -p 5000:5000 \
  -e MODE=webapp \
  -e NUTRACHECK_EMAIL=your_email@example.com \
  -e NUTRACHECK_PASSWORD=your_password \
  -v nutracheck-data:/app/output \
  --name nutracheck \
  ghcr.io/liamgwallace/nutracheck:latest
```

**Run cron mode:**
```bash
docker run -d \
  -e MODE=cron \
  -e NUTRACHECK_EMAIL=your_email@example.com \
  -e NUTRACHECK_PASSWORD=your_password \
  -e GITHUB_TOKEN=your_token \
  -e GITHUB_REPO=username/repo \
  -v nutracheck-data:/app/output \
  --name nutracheck \
  ghcr.io/liamgwallace/nutracheck:latest
```

**View logs:**
```bash
docker logs -f nutracheck
```

**Restart:**
```bash
docker restart nutracheck
```

**Stop:**
```bash
docker stop nutracheck
docker rm nutracheck
```

## GitHub Actions

The repository includes GitHub Actions workflow that automatically builds and pushes Docker images to GitHub Container Registry (ghcr.io) when code is pushed to the main branch.

**Workflow:** `.github/workflows/docker-build.yml`

Images are tagged as:
- `latest` - Most recent main branch build
- `<branch>` - Branch-specific builds
- `<branch>-<sha>` - Commit-specific builds

Pull the latest image:
```bash
docker pull ghcr.io/liamgwallace/nutracheck:latest
```

## Data Persistence

All data is stored in the `nutracheck-data` Docker volume at `/app/output`:
- `daily_data.json` - Health data database
- `liam_kcal_plot.png/html` - Calorie charts
- `liam_mass_fat_plot.png/html` - Mass/fat charts
- `cookies.pkl` - Session cookies

This volume persists between container restarts and updates.

## Updating

**Using docker-compose:**
```bash
docker-compose pull
docker-compose up -d
```

**Using Portainer:**
See [PORTAINER_DEPLOY.md](PORTAINER_DEPLOY.md)

## Troubleshooting

**Container exits immediately:**
- Check logs: `docker logs nutracheck`
- Verify credentials are set correctly

**Charts not generating:**
- Web app mode: Click "Refresh Data" button
- Cron mode: Check logs for errors

**Cannot access web interface:**
- Verify MODE=webapp is set
- Check port 5000 is exposed: `docker ps`
- Allow port in firewall: `sudo ufw allow 5000/tcp`

**GitHub upload fails (cron mode):**
- Verify GITHUB_TOKEN is valid
- Check token has `repo` scope
- Verify repository exists

## Architecture

The Docker image includes:
- Python 3.9
- Google Chrome (for Selenium)
- ChromeDriver (auto-matched to Chrome version)
- All Python dependencies from requirements.txt
- Flask web application
- Cron for scheduled execution

**Image size:** ~500MB (includes Chrome)

## Security

- Store credentials in `.env` file (never commit!)
- Web app has no authentication - only use on trusted networks
- Use VPN or reverse proxy for remote access
- Keep Docker image updated for security patches
