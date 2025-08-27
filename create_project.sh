#!/bin/bash

# Создаём корневую директорию проекта
#mkdir -p rpi-trope-surveillance

# Переходим в корневую директорию
#cd rpi-trope-surveillance

# Создаём config/ и .env.example
mkdir -p config
touch config/.env.example

# Создаём raspberry-pi/ и файлы
mkdir -p raspberry-pi
touch raspberry-pi/setup_rpi.sh
touch raspberry-pi/upload_s3.sh
touch raspberry-pi/requirements.txt
touch raspberry-pi/detect_people.py

# Создаём aws/ и вложенные директории и файлы
mkdir -p aws
touch aws/setup_aws.sh
touch aws/docker-compose.yml

mkdir -p aws/nginx
touch aws/nginx/nginx.conf

mkdir -p aws/prometheus
touch aws/prometheus/prometheus.yml

# Создаём web/ и index.html
mkdir -p web
touch web/index.html

echo "Структура директорий и файлов успешно создана!"
