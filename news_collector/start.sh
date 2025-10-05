#!/bin/bash

echo "Starting initial spider run..."
cd /usr/src/app && python run_spider.py >> /var/log/spider.log 2>&1
echo "Initial run completed. Starting cron service..."
service cron start
echo "Cron started. Container will now run spider every 12 hours."
tail -f /var/log/spider.log
