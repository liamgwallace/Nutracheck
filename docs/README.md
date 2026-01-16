# Nutracheck Health Tracker

Automated health data tracker that scrapes nutrition and fitness data from Nutracheck.co.uk, generates visualizations, and uploads them to GitHub.

## Features

- 🔄 Scrapes daily calorie intake, exercise, weight, and body measurements from Nutracheck
- 📊 Generates interactive charts with trend analysis and goal tracking
- ☁️ Automatically uploads charts to GitHub repository
- 🐳 Dockerized with automated scheduling (runs every 4 hours)
- 🔐 Secure credential management via environment variables

## Quick Start with Docker

### Prerequisites

- Docker and Docker Compose installed
- GitHub Personal Access Token with `repo` scope
- Nutracheck account credentials

### 1. Create Environment File

Create a `.env` file in the project directory:

```bash
# GitHub Configuration
GITHUB_TOKEN=your_github_token_here
GITHUB_REPO=username/repository

# Nutracheck Credentials
NUTRACHECK_EMAIL=your_email@example.com
NUTRACHECK_PASSWORD=your_password

# Optional: Timezone for cron (default: UTC)
TZ=America/New_York
```

### 2. Pull and Run with Docker Compose

```bash
# Pull the latest image and start the container
docker-compose pull
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the container
docker-compose down
```

The container will:
- Run immediately on startup
- Execute every 4 hours at 00:00, 04:00, 08:00, 12:00, 16:00, 20:00 (in your configured timezone)
- Automatically restart if it crashes
- Persist data between restarts

## Manual Setup (Without Docker)

### Prerequisites

- Python 3.9+
- Chrome browser
- ChromeDriver

### Installation

```bash
# Clone the repository
git clone https://github.com/liamgwallace/Nutracheck.git
cd Nutracheck

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template and configure
cp .env.example .env
# Edit .env with your credentials
```

### Usage

```bash
# Run the complete pipeline
python main.py

# Or run individual components
python fetch_site_data.py  # Scrape data only
python plot_charts.py      # Generate charts only
python git_upload.py       # Upload to GitHub only
```

## Configuration

All configuration is managed through environment variables in `.env`:

### Required Variables

- `GITHUB_TOKEN` - GitHub Personal Access Token (needs `repo` scope)
- `GITHUB_REPO` - Target repository (format: `username/repository`)
- `NUTRACHECK_EMAIL` - Nutracheck login email
- `NUTRACHECK_PASSWORD` - Nutracheck login password

### Optional Variables

- `KCAL_PLOT_FILE` - Calorie chart filename (default: `liam_kcal_plot.png`)
- `MASS_FAT_PLOT_FILE` - Weight/fat chart filename (default: `liam_mass_fat_plot.png`)
- `DATA_FILE` - JSON database file (default: `daily_data.json`)
- `COOKIES_FILE` - Cookie storage file (default: `cookies.pkl`)
- `TZ` - Timezone for Docker cron (default: `UTC`)
- `RUN_ON_STARTUP` - Run immediately when container starts (default: `true`)

## Docker Commands

```bash
# Build locally (optional, GitHub Actions builds automatically)
docker build -t nutracheck:local .

# Run with custom environment file
docker-compose --env-file .env.production up -d

# View real-time logs
docker-compose logs -f nutracheck

# Restart the service
docker-compose restart

# Stop and remove containers
docker-compose down

# Stop and remove containers + volumes (clears all data)
docker-compose down -v

# Run immediately (manual trigger)
docker-compose exec nutracheck python main.py
```

## Generated Charts

### Mass and Body Fat Chart
- Tracks body weight (kg) and body fat percentage
- Shows trend lines with future projections
- Goal milestones at 100kg and 86kg
- Updates date range: 2026-01-01 to 2026-11-15

### Calorie Intake Chart
- Stacked bars showing meals (Breakfast, Lunch, Dinner, Snacks, Drinks)
- Exercise calories shown below zero
- 7-day exponential moving average
- 1500 kcal daily goal line

## Data Flow

1. **Web Scraping** - Selenium automation logs into Nutracheck and extracts data
2. **Processing** - BeautifulSoup parses HTML, calculates metrics (net calories, body fat %)
3. **Storage** - TinyDB stores data in JSON format with two tables (kcal, mass/waist)
4. **Visualization** - Plotly generates interactive HTML and static PNG charts
5. **Upload** - GitHub API uploads PNG files to repository

## Architecture

See [CLAUDE.md](CLAUDE.md) for detailed technical architecture and implementation notes.

## Scheduling

The Docker container uses cron to run every 4 hours starting from midnight:
- **00:00** - Midnight run
- **04:00** - Early morning
- **08:00** - Morning
- **12:00** - Noon
- **16:00** - Afternoon
- **20:00** - Evening

Times are in the timezone specified by the `TZ` environment variable (default: UTC).

## Troubleshooting

### Container not running

```bash
# Check container status
docker-compose ps

# View detailed logs
docker-compose logs -f

# Check if environment variables are set
docker-compose config
```

### Authentication failures

- **GitHub 401 error**: Token expired or invalid, generate new token
- **Nutracheck login fails**: Check credentials in `.env`, verify account is active

### Missing data or charts

```bash
# Execute manual run to see detailed output
docker-compose exec nutracheck python main.py

# Check if files are being created
docker-compose exec nutracheck ls -la
```

### Timezone issues

```bash
# Set timezone in .env
TZ=America/New_York

# Verify timezone in container
docker-compose exec nutracheck date
```

## Development

```bash
# Run tests (if available)
pytest

# Format code
black *.py

# Lint code
flake8 *.py
```

## Security Notes

⚠️ **Never commit `.env` files to version control!**

The `.gitignore` file is configured to exclude:
- `.env` (credentials)
- `cookies.pkl` (session cookies)
- Generated output files (*.png, *.html, daily_data.json)

## License

[Add your license here]

## Contributing

[Add contribution guidelines here]

## Author

Liam Wallace - [liamgwallace@gmail.com](mailto:liamgwallace@gmail.com)
