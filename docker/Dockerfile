# Use Python 3.11 slim image (required for MCP and LangChain)
FROM python:3.11-slim

# Install Chrome and dependencies for Selenium
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    cron \
    locales \
    jq \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libatspi2.0-0 \
    libcairo2 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgbm1 \
    libglib2.0-0 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libpango-1.0-0 \
    libx11-6 \
    libxcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxkbcommon0 \
    libxrandr2 \
    xdg-utils \
    && wget -q -O /tmp/google-chrome-key.pub https://dl-ssl.google.com/linux/linux_signing_key.pub \
    && gpg --dearmor -o /usr/share/keyrings/google-chrome-keyring.gpg /tmp/google-chrome-key.pub \
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome-keyring.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && sed -i '/en_US.UTF-8/s/^# //g' /etc/locale.gen \
    && locale-gen \
    && rm -rf /var/lib/apt/lists/* /tmp/google-chrome-key.pub

# Install ChromeDriver - use Chrome for Testing to get matching version
RUN CHROME_VERSION=$(google-chrome --version | awk '{print $3}' | cut -d '.' -f 1) \
    && echo "Detected Chrome major version: $CHROME_VERSION" \
    && CHROMEDRIVER_VERSION=$(curl -s "https://googlechromelabs.github.io/chrome-for-testing/latest-versions-per-milestone-with-downloads.json" | jq -r ".milestones.\"$CHROME_VERSION\".version") \
    && echo "Installing ChromeDriver version: $CHROMEDRIVER_VERSION" \
    && wget -q "https://storage.googleapis.com/chrome-for-testing-public/$CHROMEDRIVER_VERSION/linux64/chromedriver-linux64.zip" -O /tmp/chromedriver.zip \
    && unzip /tmp/chromedriver.zip -d /tmp/ \
    && mv /tmp/chromedriver-linux64/chromedriver /usr/local/bin/ \
    && chmod +x /usr/local/bin/chromedriver \
    && rm -rf /tmp/chromedriver* \
    && chromedriver --version \
    && echo "Testing Chrome binary..." \
    && google-chrome --version \
    && google-chrome --headless --no-sandbox --disable-gpu --dump-dom about:blank > /dev/null 2>&1 && echo "Chrome headless test successful" || echo "WARNING: Chrome headless test failed"

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files (new structure)
COPY main.py ./
COPY nutracheck/ ./nutracheck/
COPY docs/CLAUDE.md ./

# Create directory for output files
RUN mkdir -p /app/output

# Copy cron configuration (for backward compatibility with cron mode)
COPY config/crontab /etc/cron.d/nutracheck-cron
RUN chmod 0644 /etc/cron.d/nutracheck-cron && \
    crontab /etc/cron.d/nutracheck-cron && \
    touch /var/log/cron.log

# Create entrypoint script
COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Set environment variable for Chrome to run in headless mode
ENV CHROME_BIN=/usr/bin/google-chrome-stable
ENV DISPLAY=:99

# Default to web app mode (can override with MODE=cron)
ENV MODE=webapp

# Expose Flask port
EXPOSE 5000

ENTRYPOINT ["/entrypoint.sh"]
