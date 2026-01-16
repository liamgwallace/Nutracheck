import requests
import base64
import json
import os

def get_sha_for_file(token, repo, path):
    """
    Gets the SHA hash of a file in the repository, if it exists.

    Parameters:
    token (str): GitHub Personal Access Token
    repo (str): Repository name like 'username/repo'
    path (str): Path in the repository to the file
    """
    api_url = f"https://api.github.com/repos/{repo}/contents/{path}"
    headers = {'Authorization': f'token {token}'}
    response = requests.get(api_url, headers=headers)

    if response.status_code == 200:
        sha = response.json()['sha']
        print(f"[git_upload] File exists, updating: {path}")
        return sha
    else:
        print(f"[git_upload] Creating new file: {path}")
        return None

def upload_file_to_github(token, repo, path, file_path):
    """
    Uploads or updates a file in GitHub.

    Parameters:
    token (str): GitHub Personal Access Token
    repo (str): Repository name like 'username/repo'
    path (str): Path in the repository to store the file
    file_path (str): Local path to the file
    """
    api_url = f"https://api.github.com/repos/{repo}/contents/{path}"

    # Read file and encode it in base64
    try:
        with open(file_path, 'rb') as file:
            file_content = file.read()
            content = base64.b64encode(file_content).decode('utf-8')
    except FileNotFoundError:
        print(f"[git_upload] ERROR: File not found: {file_path}")
        return False
    except Exception as e:
        print(f"[git_upload] ERROR reading file: {e}")
        return False

    # Create request headers
    headers = {'Authorization': f'token {token}', 'Content-Type': 'application/json'}

    # Create request payload
    data = {'message': 'Update health tracking charts', 'content': content}
    sha = get_sha_for_file(token, repo, path)
    if sha:
        data['sha'] = sha

    # Send request to GitHub API
    response = requests.put(api_url, headers=headers, data=json.dumps(data))

    # Check response status
    if response.status_code in [200, 201]:
        print(f"[git_upload] Successfully uploaded: {path}")
        return True
    else:
        print(f"[git_upload] Upload failed with status {response.status_code}")
        try:
            error_data = response.json()
            print(f"[git_upload] Error: {error_data.get('message', 'Unknown error')}")
        except:
            print(f"[git_upload] Error response: {response.text}")
        return False

if __name__ == "__main__":
    # Load environment variables from .env file if it exists
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except:
        pass

    # Get configuration from environment variables
    token = os.getenv('GITHUB_TOKEN')
    repo = os.getenv('GITHUB_REPO', 'liamgwallace/HealthData')
    file_path = os.getenv('KCAL_PLOT_FILE', 'liam_kcal_plot.png')

    # Validate required environment variables
    if not token:
        print("[git_upload] ERROR: GITHUB_TOKEN environment variable is required!")
        exit(1)

    print(f"[git_upload] Testing upload with file: {file_path}")

    # Example usage - use basename for GitHub path
    github_path = os.path.basename(file_path)
    response = upload_file_to_github(token, repo, github_path, file_path)
    if response:
        print("[git_upload] Test successful")
    else:
        print("[git_upload] Test failed")
