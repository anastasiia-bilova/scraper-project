#!/bin/bash

printenv | grep -v "no_proxy" >> /etc/environment

crontab /etc/cron.d/scraper_cron

touch /var/log/cron.log

cron -f
