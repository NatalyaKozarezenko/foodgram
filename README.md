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

Python
Django
Djangorestframework
PostgreSQL
Git
Docker

## Развертивание

### 1. Установка проекта
1.1. Клонируйте репозиторий и перейдите в него:

```
git clone https://github.com/NatalyaKozarezenko/foodgram
cd foodgram
```

1.2. Cоздайте и активируйте виртуальное окружение:

```
python3 -m venv env
source venv/bin/activate
```

1.3. По необходимости установите/обновите пакетный менеджер pip:

```
python3 -m pip install --upgrade pip
```

1.4. Установите зависимости из файла requirements.txt:

```
pip install -r requirements.txt
```

1.5. Выполните миграции:

```
python3 manage.py migrate
```

## 2. Настройка .env файла
2.1. В корне проекта создайте файл .env и заполните следующими данными:

```
POSTGRES_DB=foodgram                                 - имя базы данных
POSTGRES_USER=foodgram_user                          - имя пользователя в БД
POSTGRES_PASSWORD=foodgram_password                  - пароль для пользователя к БД
DB_HOST=db                                           - имя Хоста
DB_PORT=5432                                         - порт соединения к БД
SECRET_KEY=SECRET_KEY                                - SECRET_KEY
ALLOWED_HOSTS=127.0.0.1 localhost                    - перечень разрешённых хостов (пример)
SQLITE = False                                       - False для работы с postgresql и True для sqlite.
DEBUG = False                                        - статус режима отладки
```


### 4. Деплой проекта на сервер

4.1. Создайте на сервере директорию foodgram и скопируйте в неё файлы docker-compose.production.yml и .env и nginx.conf

```
scp -i path_to_SSH/SSH_name docker-compose.production.yml \
    username@server_ip:/home/username/taski/docker-compose.production.yml
```

4.2. В файле .env и дозаполните следующими данными:

```
ALLOWED_HOSTS=allfood.zapto.org 127.0.0.1 localhost    - перечень разрешённых хостов (пример)
CSRF_TRUSTED_ORIGINS=https://allfood.zapto.org         - список доверенных доменов
HOST=https://allfood.zapto.org                         - доменное имя сервера

4.3. Запустите Docker Compose

```
sudo docker compose -f docker-compose.production.yml up -d
```

4.4. Выполните миграции, соберите статические файлы бэкенда и скопируйте их в /backend_static/static/

```
sudo docker compose -f docker-compose.production.yml exec backend python manage.py migrate
sudo docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic
sudo docker compose -f docker-compose.production.yml exec backend cp -r /app/collected_static/. /backend_static/static/
```
4.5. Загрузите данные из json-файлов:
Разместите json-файлы в дирректории директории foodgram/data/ и запустите скрипт командой:

```
sudo docker compose -f docker-compose.production.yml exec backend python manage.py into_json_ingredients
sudo docker compose -f docker-compose.production.yml exec backend python manage.py into_json_tags
```

4.6. Добавьте суперпользователя:

```
sudo docker compose -f docker-compose.production.yml exec backend python manage.py createsuperuser
```
Приятного использования.

## техническая документация
Полная [документация](https://allfood.zapto.org/api/docs/)

## Автор
[Наталья Козарезенко](https://github.com/NatalyaKozarezenko/) 
