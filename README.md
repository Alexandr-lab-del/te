# Трекер Привычек

Этот проект представляет собой бекенд для системы трекера привычек, вдохновлённой книгой Джеймса Клира "Атомные привычки". Бекенд разработан на Python с использованием фреймворка Django и Django REST Framework (DRF). Проект предназначен для управления здоровыми привычками, предоставляя пользователям функции аутентификации, CRUD-операций для привычек, и регулярных напоминаний с интеграцией в Telegram.

---

## Основные возможности

### Функционал:
- **Аутентификация пользователей**:  
  Использование токенов JWT для безопасной аутентификации, включая регистрацию и вход в систему.

- **Управление привычками**:
  - CRUD-операции с привычками (создание, чтение, обновление, удаление).
  - Поля привычки включают: действие, место, время, продолжительность, периодичность и награды.
  - Поддержка как частных, так и общедоступных привычек.

- **Общедоступные привычки**:  
  Пользователи могут просматривать привычки, опубликованные другими, но не могут их редактировать.

- **Интеграция Telegram**:  
  - Получение напоминаний о привычках через Telegram-бота.
  - Использование команд Telegram для вывода списка привычек и настройки напоминаний.

- **Кастомные валидаторы**:
  - Запрещение создания привычки с определёнными конфликтующими параметрами (например, нельзя выбрать одновременно награду и "антипривычку").

- **Планирование задач с Celery**:  
  - Использование Celery и Redis для отправки напоминаний и автоматизации задач.

---

## Установка и настройка
Что делать? (пример для windows powershell):
* Нажимаем win + R
* Пишем Powershell
* В открывшемся окне вводим следующие комманды:
```
   sudo apt-get update && sudo apt-get upgrade
   sudo apt install apt-transport-https ca-certificates curl software-properties-common -y
     curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
     sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
     sudo apt update
     sudo apt install docker-ce -y
   sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
     sudo chmod +x /usr/local/bin/docker-compose
     sudo apt install nginx
     sudo nano /etc/nginx/sites-available/te
     docker-compose --version
```
* Подключаемся к серверу и клонируем репозиторий:
```
ssh test@158.160.157.141
git clone git@github.com:Alexandr-lab-del/te.git
cd te
```
* Создаем файл .env:
```
nano .env
Внутри пишем:
POSTGRES_USER=
POSTGRES_PASSWORD=
POSTGRES_DB=
POSTGRES_PORT=
POSTGRES_HOST=
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_BACKEND=redis://redis:6379/0
EMAIL_HOST_USER=
REDIS_URL=redis://redis:6379/0
DJANGO_SECRET_KEY=
DJANGO_DEBUG=
DJANGO_ALLOWED_HOSTS=
TEST_DATABASE_NAME=test_db
```
* Запускаем контейнеры:
```
   docker-compose up --build -d
   docker ps 
```
