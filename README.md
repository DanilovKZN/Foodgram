# Проект **Продуктовый помощник**

![example workflow](https://github.com/DanilovKZN/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg)

## Коротко о проекте

Онлайн-сервис "Продуктовый помощник" на котором пользователи могут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.


## Как запустить проект:

1. Установить Docker и Docker-compose на свой сервер:
```Shell
sudo apt upgrade -y
sudo apt install docker.io
sudo apt-get -y install python-pip
sudo pip install docker-compose
chmod +x /usr/local/bin/docker-compose
```

2. Создать файл <в созданной ранее директории проекта> docker-compose.yaml и заполнить его :
```Dockerfile
version: '3.3'
services:
  db:
    image: postgres:13.0-alpine
    volumes:
      - postgres_data:/var/lib/postgresql/data/
    env_file:
      - ./.env
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER} -d ${DB_NAME}"]
      timeout: 10s
      interval: 1s
      retries: 10

  backend:
    depends_on:
      db:
        condition: service_healthy
    image: danilovkzn/foodgram_backend:ver.1.0.8
    restart: always
    volumes:
      - static_value:/app/back_static/
      - media_value:/app/media/
    env_file:
      - ./.env

  frontend:
    depends_on:
      - backend
    image: danilovkzn/foodgram_frontend:latest
    volumes:
      - frontend_data:/app/result_build/

  nginx:
    image: nginx:1.19.3
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/conf.d/default.conf
      - frontend_data:/usr/share/nginx/html/
      - ../docs/:/usr/share/nginx/html/api/docs/
      - static_value:/var/html/back_static/
      - media_value:/var/html/media/
    depends_on:
      - frontend

volumes: 
  static_value:
  media_value:
  postgres_data:
  frontend_data:

```

3.  В этой же директории создать папку nginx:
```Shell
sudo mkdir nginx/
cd nginx/
```
   В папке nginx создать файл конфигурации для nginx:
```Shell
sudo touch default.conf
```
И заполнить его:
```Nginx
server {
    listen 80;

    server_name 178.154.195.187;

    location /back_static/ {
        root /var/html/;
    }

    location /media/ {
        root /var/html/;
    }

    location /api/docs/ {
        root /usr/share/nginx/html;
        try_files $uri $uri/redoc.html;
    }

    location /static/admin/ {
        root /var/html/static/;
    }

    location /static/rest_framework/ {
        root /var/html/static/;
    }

    location /api/ {
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Forwarded-Server $host;
        proxy_pass http://backend:8000/api/;
    }

    location /admin/ {
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Forwarded-Server $host;
        proxy_pass http://backend:8000/admin/;
    }

    location / {
        root /usr/share/nginx/html;
        index  index.html index.htm;
        try_files $uri /index.html;
        proxy_set_header        Host $host;
        proxy_set_header        X-Real-IP $remote_addr;
        proxy_set_header        X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header        X-Forwarded-Proto $scheme;
    }
    error_page   500 502 503 504  /50x.html;
    location = /50x.html {
        root   /var/html/frontend/;
    }

    server_tokens off;

}


```

4.  Создать и заполнить файл .env в директории , где расположен docker-compose:
```Python
SECRET_KEY = 'Ключ приложения'
DB_ENGINE = 'Используемая БД'
DB_NAME = 'Имя БД'
POSTGRES_USER = 'Имя пользователя'
POSTGRES_PASSWORD = 'Пароль'
DB_HOST = 'Название кониейнера в docker-compose'
DB_PORT = 'Порт для подключения к БД'
HOSTS = 'IP сервера и внутренние адреса списком'
```

5. Собрать образы 
```Shell
sudo docker-compose stop
sudo docker-compose rm web
sudo systemctl stop nginx
sudo docker pull danilovkzn/backend:latest
sudo docker pull danilovkzn/frontend:latest
sudo docker-compose up -d --build
```

6. Заполнить БД данными и создать пользователя из папки, где расположен docker-compose файл:

```Shell
sudo docker-compose exec backend python manage.py migrate
sudo docker-compose exec backend python manage.py createsuperuser
sudo docker-compose exec backend python manage.py collectstatic --no-input
sudo docker-compose exec backend python manage.py load_data_ingr
```

8. Технологии
```
Python
Docker
Docker-compose
Nginx
Postgres
Gunicorn
```
9. Автор
```
Данилов Николай
``` 

10. Ссылка на проект
```
http://178.154.195.187/api/v1/
```
