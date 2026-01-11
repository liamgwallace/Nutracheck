import os
from fetch_site_data import fetch_nutracheck_site_data
from plot_charts import create_charts
from git_upload import upload_file_to_github

# Load environment variables from .env file if it exists
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("[main] Loaded environment variables from .env file")
except ImportError:
    print("[main] python-dotenv not installed, using system environment variables only")
except Exception as e:
    print(f"[main] Warning: Could not load .env file: {e}")

# Get configuration from environment variables
token = os.getenv('GITHUB_TOKEN')
repo = os.getenv('GITHUB_REPO', 'liamgwallace/HealthData')
file_path_kcal = os.getenv('KCAL_PLOT_FILE', 'liam_kcal_plot.png')
file_path_mass_fat = os.getenv('MASS_FAT_PLOT_FILE', 'liam_mass_fat_plot.png')

# Validate required environment variables
if not token:
    print("[main] ERROR: GITHUB_TOKEN environment variable is required!")
    print("[main] Please set it in .env file or as an environment variable")
    exit(1)

print(f"[main] Configuration loaded:")
print(f"[main]   Repo: {repo}")
print(f"[main]   Kcal plot: {file_path_kcal}")
print(f"[main]   Mass/Fat plot: {file_path_mass_fat}")

# Run the data pipeline
print("\n[main] Step 1: Fetching data from Nutracheck...")
fetch_nutracheck_site_data()

print("\n[main] Step 2: Creating charts...")
create_charts(show_charts=False)

print("\n[main] Step 3: Uploading to GitHub...")
# Upload mass/fat plot
response = upload_file_to_github(token, repo, file_path_mass_fat, file_path_mass_fat)
if response:
    print(f"[main] SUCCESS: {file_path_mass_fat} uploaded/updated successfully.")
else:
    print(f"[main] FAILED: {file_path_mass_fat} upload failed.")

# Upload kcal plot
response = upload_file_to_github(token, repo, file_path_kcal, file_path_kcal)
if response:
    print(f"[main] SUCCESS: {file_path_kcal} uploaded/updated successfully.")
else:
    print(f"[main] FAILED: {file_path_kcal} upload failed.")

print("\n[main] Pipeline complete!")
