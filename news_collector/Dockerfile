FROM python:3.13-slim

WORKDIR /usr/src/app

# Copy requirements first for better caching
COPY requirements.txt .

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3-dev \
    python3-pip \
    libxml2-dev \
    libxslt1-dev \
    zlib1g-dev \
    libffi-dev \
    libssl-dev \
    cron

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Make startup script executable and ensure Unix line endings
RUN chmod +x /usr/src/app/start.sh && \
    sed -i 's/\r$//' /usr/src/app/start.sh

# Create the cron job to run every 12 hours
RUN echo "0 */12 * * * cd /usr/src/app && python run_spider.py >> /var/log/spider.log 2>&1" | crontab -

# Create log file and set permissions
RUN touch /var/log/spider.log && chmod 666 /var/log/spider.log

# Start the startup script
CMD ["/usr/src/app/start.sh"]