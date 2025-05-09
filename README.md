# Проект «API для Yatube»
api_yamdb

YaMDb — это платформа для сбора и обмена отзывами пользователей о различных произведениях, таких как книги, фильмы и музыка. Проект реализован с использованием Django и Django REST Framework.

## Описание проекта

Проект YaMDb позволяет пользователям оставлять отзывы на произведения в разных категориях (например, книги, фильмы, музыка). Каждое произведение может принадлежать только одной категории, но может иметь несколько жанров. Пользователи могут оценивать произведения по шкале от 1 до 10, а также оставлять комментарии к отзывам. Средний рейтинг произведения рассчитывается автоматически на основе оценок пользователей.

## Возможности

- **Регистрация и аутентификация пользователей**: Пользователи могут зарегистрироваться и войти в систему. После регистрации они получают код подтверждения по электронной почте, который необходимо использовать для подтверждения аккаунта и получения JWT токена для авторизованных запросов.

- **Управление ролями**: Платформа имеет различные роли пользователей:
  - **Аноним**: Может просматривать описания произведений и читать отзывы и комментарии.
  - **Пользователь**: Может читать весь контент, оставлять отзывы, оценивать произведения и комментировать отзывы. Пользователи могут редактировать и удалять свои собственные отзывы и комментарии.
  - **Модератор**: Имеет все права пользователя, плюс возможность удалять и редактировать любые отзывы и комментарии.
  - **Администратор**: Имеет полный контроль над контентом, включая управление произведениями, категориями, жанрами и ролями пользователей.

- **Ресурсы API**:
  - **auth**: Управление аутентификацией пользователей.
  - **users**: Управление аккаунтами и профилями пользователей.
  - **titles**: Представляет произведения, которые пользователи могут оценивать.
  - **categories**: Представляет типы произведений (например, книги, фильмы, музыка).
  - **genres**: Представляет жанры, к которым могут относиться произведения.
  - **reviews**: Представляет отзывы пользователей на произведения.
  - **comments**: Представляет комментарии к отзывам пользователей.

- **Импорт данных**: Проект позволяет загружать данные из файлов CSV для начальной загрузки базы данных.

### Стек:
```
Python 3.11
Django 3.2.
Django Rest Framework 3.12
Django Rest Framework Simplejwt==5.3.1
Django filter 23.1
```

## Установка

1. Клонируйте репозиторий:
    ```bash
    git clone git@github.com:GoarikMkrtchyan/api_yamdb.git
    ```
2. Перейдите в директорию проекта:
    ```bash
    cd api_yamdb
    ```
3. Создайте и активируйте виртуальное окружение (рекомендуется):
    ```bash
    python -m venv venv
    source venv/bin/activate  # Для Windows используйте `venv\Scripts\activate`
    ```
4. Установите зависимости:
    ```bash
    pip install -r requirements.txt
    ```
5. Примените миграции:
    ```bash
    python manage.py migrate
    ```
6. Запустите сервер:
    ```bash
    python manage.py runserver
    ```
7. Загрузите файлы csv в БД:
    ```bash
    python manage.py load_data_csv
    ```
## Документация API:
Документация API по проекту находится по адресу
(доступно после запуска проекта):

```
http://127.0.0.1:8000/redoc/

```

### Авторы:
1. Мкртчян Гоарик - Разработчик 1(Управление пользователями) 
2. Чуйко Полина - Разработчик 2 (Произведения/категории/жанр/load_data_csv)
3. Бачурин Станислав - Разработчик 3(Отзывы/Комменты/рейтинги)

https://github.com/GoarikMkrtchyan/api_yamdb
