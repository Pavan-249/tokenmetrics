FROM python:3.11-slim

WORKDIR /app

# Install cron + system deps
RUN apt-get update && \
    apt-get install -y cron && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
COPY cronjob /etc/cron.d/funding-cron

# Register cron
RUN chmod 0644 /etc/cron.d/funding-cron && \
    crontab /etc/cron.d/funding-cron

# Run cron in foreground so container stays alive
CMD ["cron", "-f"]
