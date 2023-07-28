# Foodgram

## Описание

Яндекс практикум, дипломный проект.

https://foody-moody.hopto.org \
логин админки: admin \
пароль: admin

## Что использовалось

Django, Django REST framework, Postgresql, Docker

## Функционал

Пользователи публикуют свои рецепты с указанием состава и количества ингредиентов, времени приготовления, фотографией готового блюда, закрепляют теги по соответствующим темам, благодаря которым другие пользователи будут фильтровать рецепты.

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



