# WallStreet

WallStreet is a real-time stock market simulation platform, where the users can subscribe for Ipos, buy and sell the stocks, view interactive charts and explore the stock news to analyze the stocks.


## Features

- **REST API :** Api endpoints for virtual stock market platform enabling users to buy/sell stocks, view charts, news & subscribe to IPOs.
  
- **Background Processing :** Celery-based asynchronous worker architecture for processing buy/sell orders.

- **Scheduled News Release :** Releasing periodic stock news via Celery Beat, allowing users to make informed trading decisions.

- **IPO Allotment :** Weighted average & pro rata allotment system for IPO subscriptions, ensuring fair distribution among users.


## Technologies Used
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Django](https://img.shields.io/badge/django-%23092E20.svg?style=for-the-badge&logo=django&logoColor=white)
![DjangoREST](https://img.shields.io/badge/DJANGO-REST-ff1709?style=for-the-badge&logo=django&logoColor=white&color=ff1709&labelColor=gray)
![Celery](https://img.shields.io/badge/celery-%23a9cc54.svg?style=for-the-badge&logo=celery&logoColor=ddf4a4)
![Redis](https://img.shields.io/badge/redis-%23DD0031.svg?style=for-the-badge&logo=redis&logoColor=white)
![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)
![Swagger](https://img.shields.io/badge/-Swagger-%23Clojure?style=for-the-badge&logo=swagger&logoColor=white)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)
![Nginx](https://img.shields.io/badge/nginx-%23009639.svg?style=for-the-badge&logo=nginx&logoColor=white)
![Gunicorn](https://img.shields.io/badge/gunicorn-%298729.svg?style=for-the-badge&logo=gunicorn&logoColor=white)

![WallStreet_SystemDiagram](https://github.com/AbhishekBhosale46/DRF-WallStreet24/assets/58450561/f5be9f90-8396-4267-8687-3c121e226242)


## DB Diagram
![WallStreet_DB](https://github.com/AbhishekBhosale46/DRF-WallStreet24/assets/58450561/3f12d389-2093-4584-8149-270d1ad525ea)


## Run Locally

Clone the project

```bash
  git clone https://github.com/AbhishekBhosale46/DRF-WallStreet24
```

Go to the project directory

```bash
  cd my-project
```

Spin Docker Containers

```bash
  docker-compose up
```

