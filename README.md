# Проект «Фудграм»
![example workflow](https://github.com/NatalyaKozarezenko/foodgram/actions/workflows/main.yml/badge.svg)

## Описание проекта

«Фудграм» — сайт, на котором пользователи будут публиковать свои рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Зарегистрированным пользователям также будет доступен сервис «Список покупок». Он позволит создавать список продуктов, которые нужно купить для приготовления выбранных блюд.

Страницы проекта:
**Главная**
Содержимое главной — список первых шести рецептов, отсортированных по дате публикации «от новых к старым». На этой странице подразумевается постраничная пагинация. Остальные рецепты должны быть доступны на следующих страницах.

**Страница регистрации**
В проекте доступна система регистрации и аутентификации пользователей.

**Страница входа**
После регистрации пользователь переадресовывается на страницу входа.

**Страница рецепта**
Здесь — полное описание рецепта. Залогиненные пользователи могут добавить рецепт в избранное и список покупок, а также подписаться на автора рецепта. Для каждого рецепта можно получить прямую короткую ссылку, нажав на соответствующую иконку справа от названия рецепта. Эта ссылка не меняется после редактирования рецепта.

**Страница пользователя**
На странице — имя пользователя, все рецепты, опубликованные пользователем, и кнопка, чтобы подписаться или отписаться от него.

**Страница подписок**
Только владелец аккаунта может просмотреть свою страницу подписок. Ссылка на неё находится в выпадающем меню в правом верхнем углу.
Подписаться на публикации могут только залогиненные пользователи.

**Избранное**
Добавлять рецепты в избранное может только залогиненный пользователь. Добавить рецепт в избранное можно с главной страницы и со страницы самого рецепта, нажав на соответствующую иконку. Сам список избранного может просмотреть только его владелец.

**Список покупок**
Работать со списком покупок могут только залогиненные пользователи. Доступ к собственному списку покупок есть только у владельца аккаунта. Пользователь может скачать свой список покупок в формате .txt

**Создание и редактирование рецепта**
Эта страница доступна только для залогиненных пользователей. Также пользователь может отредактировать любой рецепт, который он создал.

**Страница изменения пароля**
Доступ к этой странице есть только у залогиненных пользователей, через кнопку Сменить пароль в выпадающем меню в правом верхнем углу страницы.

**Фильтрация по тегам**
При добавлении рецепта обязательно указывается один или несколько тегов. Новые теги может добавить только администратор сайта.
На страницах с рецептами при нажатии на название тега выводится список рецептов, отмеченных этим тегом. Фильтрация может проводиться по нескольким тегам в комбинации «или»: если выбрано несколько тегов, в результате должны быть показаны рецепты, которые отмечены хотя бы одним из этих тегов. 
При фильтрации на странице пользователя фильтруются только рецепты выбранного пользователя. Такой же принцип должен соблюдаться при фильтрации списка избранного.

**Смена аватара**
После регистрации новый пользователь получает изображение профиля по умолчанию. При клике на аватар у пользователя в шапке сайта появляется возможность поменять его или удалить.

## Стек
asgiref
certifi
charset-normalizer
Django
idna
packaging
python-dotenv
requests
sqlparse
tomli
typing_extensions
urllib3
gunicorn
djangorestframework
djangorestframework_simplejwt
djoser
python-dotenv
django-filter
short-url
Pillow
tzdata
cffi
cryptography
defusedxml
oauthlib
pycparser
drf-extra-fields
PyJWT
PyYAML
python3-openid
requests
requests-oauthlib
social-auth-app-django
social-auth-core


## Развертивание

## 1. Настройка .env файла
1.1. В корне проекта создайте файл .env и заполните следующими данными:

```
POSTGRES_DB=foodgram                                   - имя базы данных
POSTGRES_USER=foodgram_user                            - имя пользователя в БД
POSTGRES_PASSWORD=foodgram_password                    - пароль для пользователя к БД
DB_HOST=db                                             - имя Хоста
DB_PORT=5432                                           - порт соединения к БД
SECRET_KEY=SECRET_KEY                                  - SECRET_KEY
ALLOWED_HOSTS=allfood.zapto.org 127.0.0.1 localhost    - перечень разрешённых хостов (пример)
CSRF_TRUSTED_ORIGINS=https://allfood.zapto.org         - список доверенных доменов
SQLITE = False                                         - False для работы с postgresql и True для sqlite.
DEBUG = False                                          - статус режима отладки  
```


## 4. Деплой проекта на сервер
4.1. Подключитесь к серверу:

```
ssh -i путь_до_файла_с_SSH_ключом/название_файла_с_SSH_ключом имя_пользователя@ip_адрес_сервера
```

4.2. Установите Docker Compose

```
sudo apt update
sudo apt install curl
curl -fSL https://get.docker.com -o get-docker.sh
sudo sh ./get-docker.sh
sudo apt install docker-compose-plugin
```

4.3. Создайте на сервере директорию foodgram и скопируйте в неё файлы docker-compose.production.yml и .env и nginx.conf

```
scp -i path_to_SSH/SSH_name docker-compose.production.yml \
    username@server_ip:/home/username/taski/docker-compose.production.yml
```

4.4. Запустите Docker Compose

```
sudo docker compose -f docker-compose.production.yml up -d
```

4.5. Выполните миграции, соберите статические файлы бэкенда и скопируйте их в /backend_static/static/

```
sudo docker compose -f docker-compose.production.yml exec backend python manage.py migrate
sudo docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic
sudo docker compose -f docker-compose.production.yml exec backend cp -r /app/collected_static/. /backend_static/static/
```
4.6. Загрузите данные из csv-файлов:
Разместите csv-файлы в дирректории директории foodgram/data/ и запустите скрипт командой:

```
sudo docker compose -f docker-compose.production.yml exec backend python manage.py csv_loader
```
После загрузки всех данных выведется сообщение "Загрузка закончена."

4.7. Добавте суперпользователя:

```
sudo docker compose -f docker-compose.production.yml exec backend python manage.py createsuperuser
```
Приятного использования.


## Автор
[Наталья Козарезенко](https://github.com/NatalyaKozarezenko/) 