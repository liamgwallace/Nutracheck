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
    print(f"[get_sha_for_file] Checking if file exists at: {api_url}")
    print(f"[get_sha_for_file] Using token: {token[:7]}...{token[-4:]}")

    headers = {'Authorization': f'token {token}'}
    response = requests.get(api_url, headers=headers)

    print(f"[get_sha_for_file] Response status code: {response.status_code}")

    if response.status_code == 200:
        sha = response.json()['sha']
        print(f"[get_sha_for_file] File {path} found. SHA: {sha[:10]}...")
        return sha
    else:
        print(f"[get_sha_for_file] File {path} not found. Will create a new one.")
        print(f"[get_sha_for_file] Response: {response.text}")
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
    print(f"\n[upload_file_to_github] Starting upload process...")
    print(f"[upload_file_to_github] Repo: {repo}")
    print(f"[upload_file_to_github] Remote path: {path}")
    print(f"[upload_file_to_github] Local file: {file_path}")

    api_url = f"https://api.github.com/repos/{repo}/contents/{path}"

    # Read file and encode it in base64
    try:
        print(f"[upload_file_to_github] Reading file: {file_path}")
        with open(file_path, 'rb') as file:
            file_content = file.read()
            file_size = len(file_content)
            print(f"[upload_file_to_github] File size: {file_size} bytes ({file_size/1024:.2f} KB)")
            content = base64.b64encode(file_content).decode('utf-8')
            print(f"[upload_file_to_github] Base64 encoded size: {len(content)} characters")
    except FileNotFoundError:
        print(f"[upload_file_to_github] ERROR: File not found: {file_path}")
        return False
    except Exception as e:
        print(f"[upload_file_to_github] ERROR reading file: {e}")
        return False

    # Create request headers
    headers = {'Authorization': f'token {token}', 'Content-Type': 'application/json'}

    # Create request payload
    data = {'message': 'Upload/Update PNG file', 'content': content}
    sha = get_sha_for_file(token, repo, path)
    if sha:
        data['sha'] = sha
        print(f"[upload_file_to_github] Updating existing file {path}.")
    else:
        print(f"[upload_file_to_github] Creating new file {path}.")

    # Send request to GitHub API
    print(f"[upload_file_to_github] Sending PUT request to: {api_url}")
    response = requests.put(api_url, headers=headers, data=json.dumps(data))

    print(f"[upload_file_to_github] Response status code: {response.status_code}")

    # Check response status
    if response.status_code in [200, 201]:
        print(f"[upload_file_to_github] SUCCESS: File uploaded/updated successfully.")
        return True
    else:
        print(f"[upload_file_to_github] FAILED: Upload failed with status {response.status_code}")
        try:
            error_data = response.json()
            print(f"[upload_file_to_github] Error response: {json.dumps(error_data, indent=2)}")
        except:
            print(f"[upload_file_to_github] Error response text: {response.text}")
        return False

if __name__ == "__main__":
    # Load environment variables from .env file if it exists
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("[git_upload] Loaded environment variables from .env file")
    except ImportError:
        print("[git_upload] python-dotenv not installed, using system environment variables only")
    except Exception as e:
        print(f"[git_upload] Warning: Could not load .env file: {e}")

    # Get configuration from environment variables
    token = os.getenv('GITHUB_TOKEN')
    repo = os.getenv('GITHUB_REPO', 'liamgwallace/HealthData')
    file_path = os.getenv('KCAL_PLOT_FILE', 'liam_kcal_plot.png')
    path = file_path

    # Validate required environment variables
    if not token:
        print("[git_upload] ERROR: GITHUB_TOKEN environment variable is required!")
        print("[git_upload] Please set it in .env file or as an environment variable")
        exit(1)

    print(f"[git_upload] Testing upload with file: {file_path}")

    # Example usage
    response = upload_file_to_github(token, repo, path, file_path)
    if response:
        print("[git_upload] File uploaded/updated successfully.")
    else:
        print("[git_upload] Failed to upload/update file")
