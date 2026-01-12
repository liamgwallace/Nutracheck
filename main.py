import os
from fetch_site_data import fetch_nutracheck_site_data
from plot_charts import create_charts
from git_upload import upload_file_to_github

# Load environment variables from .env file if it exists
try:
    from dotenv import load_dotenv
    load_dotenv()
except:
    pass

# Get configuration from environment variables
token = os.getenv('GITHUB_TOKEN')
repo = os.getenv('GITHUB_REPO', 'liamgwallace/HealthData')
file_path_kcal = os.getenv('KCAL_PLOT_FILE', 'liam_kcal_plot.png')
file_path_mass_fat = os.getenv('MASS_FAT_PLOT_FILE', 'liam_mass_fat_plot.png')

# Validate required environment variables
if not token:
    print("[main] ERROR: GITHUB_TOKEN environment variable is required!")
    exit(1)

print(f"[main] Starting pipeline - Repo: {repo}")

# Run the data pipeline
print("\n[main] Step 1: Fetching data from Nutracheck...")
fetch_nutracheck_site_data()

print("\n[main] Step 2: Creating charts...")
create_charts(show_charts=False)

print("\n[main] Step 3: Uploading to GitHub...")
# Upload mass/fat plot (use basename for GitHub path)
github_path_mass_fat = os.path.basename(file_path_mass_fat)
response = upload_file_to_github(token, repo, github_path_mass_fat, file_path_mass_fat)
if response:
    print(f"[main] SUCCESS: {github_path_mass_fat} uploaded to GitHub")
else:
    print(f"[main] FAILED: {github_path_mass_fat} upload failed")

# Upload kcal plot (use basename for GitHub path)
github_path_kcal = os.path.basename(file_path_kcal)
response = upload_file_to_github(token, repo, github_path_kcal, file_path_kcal)
if response:
    print(f"[main] SUCCESS: {github_path_kcal} uploaded to GitHub")
else:
    print(f"[main] FAILED: {github_path_kcal} upload failed")

print("\n[main] Pipeline complete!")
