FROM python:3.11-slim

ENV TZ=Europe/Warsaw
RUN apt-get update && apt-get install -y cron curl procps tzdata && \
    ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ .

# Copy the cron job file into container
COPY scraper_cron /etc/cron.d/scraper_cron
COPY setup_cron.sh /setup_cron.sh

# Give execution rights on the cron job
RUN chmod 0644 /etc/cron.d/scraper_cron
RUN chmod +x /setup_cron.sh

# Create log file for cron logs and give permissions
RUN touch /var/log/cron.log

# By default, run cron in foreground and keep container alive
CMD ["/setup_cron.sh"]
