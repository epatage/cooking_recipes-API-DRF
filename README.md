# Foodgram

## Описание

Яндекс практикум, дипломный проект.

## Что использовалось

Django, Django REST framework, Postgresql, Docker

## Функционал

Пользователи публикуют свои рецепты с указанием состава и количества ингредиентов, времени приготовления, фотографией готового блюда, закрепляют теги по соответствующим темам, благодаря которым другие пользователи будут фильтровать рецепты.

### Примеры запросов
Регистрация нового пользователя.
Отправить POST запрос к 'api/users/':
```
{
    "email": "vpupkin@yandex.ru",
    "username": "vasya.pupkin",
    "first_name": "Вася",
    "last_name": "Пупкин",
    "password": "Qwerty123"
}
```
Авторизация пользователя (по email).
Отправить POST запрос к 'api/auth/token/login/':
```
{
    "password": "string",
    "email": "string"
}
```
Создание рецепта.
Отправить POST запрос к '/api/recipes/' c прикреплением токена:
```
{
  "ingredients": [
    {
      "id": 1123,
      "amount": 10
    }
  ],
  "tags": [
    1,
    2
  ],
  "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAgMAAABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg==",
  "name": "string",
  "text": "string",
  "cooking_time": 1
}
```


### Как запустить проект:

Клонировать репозиторий:

```
git clone git@github.com:epatage/foodgram-project-react.git
```


Cоздать и активировать виртуальное окружение:
```
cd backned
```

```
python -m venv venv
```

```
source venv/scripts/activate
```

Установить зависимости из файла requirements.txt:


```
pip install -r requirements.txt
```

Выполнить миграции:

```
python manage.py migrate
```
В директории /data/ находится
база данных ингредиентов.
Для автоматического добавления тестовых записей
в базу данных запустите команду 
(также см. пункт ниже):

```
python manage.py download_data --delete-existing
```


Запустить проект:

```
python manage.py runserver

```



