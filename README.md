# 🚗 AutoDataScraper

A daily car listing scraper built with Python, PostgreSQL, Docker, and scheduled using cron. 
It extracts detailed car data from a marketplace, and:

- Saves structured data to a PostgreSQL database.
- Saves raw JSON dumps to daily folders.

## 📦 Features

- Scrapes all listings from a car marketplace with headless Selenium.
- Automatically runs every day at **12:00 PM** via cron.
- Stores data in both:
  - 🗃️ PostgreSQL database
  - 📁 `/app/dumps/YYYY_MM_DD/` (raw JSON)
  - <img src="https://rb.gy/gck4wr" alt="Dumps folder screenshot" width="300"/>
  
## 🐳 Run with Docker

### Copy and configure `.env`

```shell
$ cp .env.example .env # edit PostgreSQL credentials inside .env
```

### Build and start the container:

```shell
$ docker-compose up --build
```

### Check if the cron job is scraping as expected:

```shell
$ docker exec -it scraper_app tail -f /var/log/cron.log
```

###  To view dumps:

```shell
$ docker exec -it scraper_app ls /app/dumps/$(date +%Y_%m_%d)
```

## 🔁 Cron Schedule

The scraper runs daily at 12:00 PM container time.

To update the time, edit scraper_cron file:

```console
┌───────────── minute (0 - 59)
│ ┌───────────── hour (0 - 23)
│ │ ┌───────────── day of month (1 - 31)
│ │ │ ┌───────────── month (1 - 12)
│ │ │ │ ┌───────────── day of week (0 - 6) (Sunday to Saturday)
│ │ │ │ │
* * * * * command to execute
0 12 * * * /usr/local/bin/python3 /app/main.py >> /var/log/cron.log 2>&1
```

## ✍️ Manually Trigger the Scraper

```shell
$ docker exec -it scraper_app python /app/main.py
```

## 🛠 Development Tips

To remove all containers:

```shell
$ docker rm -f $(docker ps -aq)
```

To remove all images:

```shell
$ docker rmi -f $(docker images -aq)
```

To remove the volume:

```shell
$ docker volume rm test-project_postgres_data
```

### 🛢 Accessing the PostgreSQL Database

To access your PostgreSQL database running inside a Docker container named postgres (replace user and database with your actual values):

```shell
$ docker exec -it postgres psql -U <username> -d <database>
```

Or pen bash shell first, then run psql:

```shell
$ docker exec -it postgres bash
root@id:/# psql -U <username> -d <database>
```