# Deploying to Portainer

This guide explains how to deploy the Nutracheck Health Tracker web app as a Portainer stack on your home server.

## Prerequisites

- Portainer installed and running on your home server
- Access to Portainer web interface
- Your Nutracheck.co.uk login credentials

## Deployment Steps

### 1. Access Portainer

Navigate to your Portainer instance (e.g., `http://your-server-ip:9000`)

### 2. Create a New Stack

1. Click on **Stacks** in the left sidebar
2. Click **+ Add stack** button
3. Give your stack a name: `nutracheck-health-tracker`

### 3. Configure the Stack

**Option A: Use the Web Editor (Recommended)**

1. Select **Web editor** tab
2. Copy the entire contents of `portainer-stack.yml` into the editor
3. **IMPORTANT:** Update these values in the YAML:
   ```yaml
   NUTRACHECK_EMAIL: your_actual_email@example.com
   NUTRACHECK_PASSWORD: your_actual_password
   TZ: Your/Timezone  # e.g., America/New_York, Europe/London
   ```

**Option B: Use Git Repository**

1. Select **Repository** tab
2. Enter repository URL: `https://github.com/liamgwallace/Nutracheck`
3. Repository reference: `claude/health-tracker-visualization-OawZf`
4. Compose path: `portainer-stack.yml`
5. Under **Environment variables**, add:
   - `NUTRACHECK_EMAIL` = your email
   - `NUTRACHECK_PASSWORD` = your password
   - `TZ` = your timezone

### 4. Deploy the Stack

1. Scroll down and click **Deploy the stack**
2. Wait for the image to pull (first time will take a few minutes)
3. Check the stack status - it should show as "running"

### 5. Access the Web App

Once deployed, access your health tracker at:
```
http://your-server-ip:5000
```

## Configuration Options

### Port Mapping

By default, the app runs on port 5000. To use a different port:

```yaml
ports:
  - "8080:5000"  # Access on port 8080 instead
```

### Run on Startup

To generate charts automatically when the container starts:

```yaml
RUN_ON_STARTUP: true
```

Note: This will make container startup slower (30-60 seconds) but charts will be ready immediately.

### Timezone

Set your local timezone for accurate logging:

```yaml
TZ: America/New_York     # Eastern Time
TZ: Europe/London        # UK Time
TZ: Australia/Sydney     # Australian Eastern Time
TZ: UTC                  # Default
```

### Data Persistence

All data (charts, database, cookies) is stored in the `nutracheck-data` Docker volume. This persists between container restarts and updates.

## Updating the App

When a new version is pushed to GitHub Container Registry:

1. Go to **Stacks** in Portainer
2. Select your `nutracheck-health-tracker` stack
3. Click **Update the stack**
4. Enable **Re-pull image and redeploy**
5. Click **Update**

Portainer will pull the latest image and restart the container automatically.

## Troubleshooting

### Container won't start

Check the logs:
1. Click on **Containers** in Portainer
2. Click on `nutracheck-health-tracker`
3. Click **Logs**

Common issues:
- Missing `NUTRACHECK_EMAIL` or `NUTRACHECK_PASSWORD`
- Invalid credentials

### Can't access web app

1. Check container is running in Portainer
2. Verify port 5000 is not blocked by firewall:
   ```bash
   sudo ufw allow 5000/tcp
   ```
3. Try accessing from the server itself:
   ```bash
   curl http://localhost:5000
   ```

### Charts not loading

1. Click the **Refresh Data** button in the web interface
2. Wait 30-60 seconds for data fetch and chart generation
3. Charts will auto-reload when ready

### Data fetch fails

Check your Nutracheck credentials are correct and your account is active. The container needs internet access to reach nutracheck.co.uk.

## Switching to Cron Mode

If you want to run in the original cron mode (scheduled uploads to GitHub):

```yaml
environment:
  MODE: cron
  RUN_ON_STARTUP: true
  GITHUB_TOKEN: your_github_token_here
  GITHUB_REPO: username/repository
```

In cron mode:
- The web interface is not available
- Port 5000 doesn't need to be exposed
- Data is uploaded to GitHub every 4 hours

## Resource Usage

The container uses:
- **CPU:** Very low when idle (~1%)
- **RAM:** ~150-200MB
- **Disk:** ~500MB (image) + data files
- **Network:** Minimal (only when refreshing data)

Perfect for Raspberry Pi or any home server!

## Security Notes

**Important:** This is a single-user application with no authentication. Security recommendations:

1. **Do NOT expose port 5000 to the internet** (only access on your local network)
2. If you need remote access, use:
   - VPN to your home network
   - Reverse proxy with authentication (nginx + basic auth)
   - Cloudflare Tunnel with Cloudflare Access
3. Your Nutracheck credentials are stored as environment variables in Portainer
4. Consider using Portainer's "Environment variables" feature instead of hardcoding credentials in the stack YAML

## Backup

To backup your data:

1. In Portainer, go to **Volumes**
2. Find `nutracheck-data` volume
3. Use docker commands to backup:
   ```bash
   docker run --rm -v nutracheck-data:/data -v $(pwd):/backup ubuntu tar czf /backup/nutracheck-backup.tar.gz /data
   ```

## Support

For issues:
- Check container logs in Portainer
- Review the main `WEBAPP_README.md` for general app documentation
- Check GitHub issues: https://github.com/liamgwallace/Nutracheck/issues
