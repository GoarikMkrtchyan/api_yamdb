import csv
import os

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import IntegrityError

from reviews.models import Category, Comment, Genre, GenreTitle, Review, Title
from users.models import User


def category_create(row):
    Category.objects.get_or_create(
        id=row[0],
        name=row[1],
        slug=row[2],
    )


def genre_create(row):
    Genre.objects.get_or_create(
        id=row[0],
        name=row[1],
        slug=row[2],
    )


def titles_create(row):
    Title.objects.get_or_create(
        id=row[0],
        name=row[1],
        year=row[2],
        category_id=row[3],
    )


def users_create(row):
    email = row[2]
    if User.objects.filter(email=email).exists():
        print(f"Пользователь с email {email} уже существует.")
        return None, False
    try:
        user = User.objects.create(
            id=row[0],
            username=row[1],
            email=email,
            role=row[3],
            bio=row[4],
            first_name=row[5],
            last_name=row[6],
        )
        return user, True
    except IntegrityError:
        print(f"Ошибка при создании пользователя с email {email}.")
        return None, False


def review_create(row):
    title, _ = Title.objects.get_or_create(id=row[1])
    author, _ = User.objects.get_or_create(id=row[3])
    Review.objects.update_or_create(
        id=row[0],
        defaults={
            'title': title,
            'text': row[2],
            'author': author,
            'score': row[4],
            'pub_date': row[5]
        }
    )


def comment_create(row):
    review, _ = Review.objects.get_or_create(id=row[1])
    author, _ = User.objects.get_or_create(id=row[3])
    Comment.objects.get_or_create(
        id=row[0],
        review=review,
        text=row[2],
        author=author,
        pub_date=row[4],
    )


def genre_title_create(row):
    title, _ = Title.objects.get_or_create(id=row[1])
    genre, _ = Genre.objects.get_or_create(id=row[2])
    GenreTitle.objects.get_or_create(
        id=row[0],
        title=title,
        genre=genre,
    )

TABLES = {
    'category.csv': category_create,
    'genre.csv': genre_create,
    'titles.csv': titles_create,
    'genre_title.csv': genre_title_create,
    'users.csv': users_create,
    'review.csv': review_create,
    'comments.csv': comment_create,
}


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        for csv_file, create_function in TABLES.items():
            self.load_csv_to_db(create_function, csv_file)

    def load_csv_to_db(self, create_function, csv_file):
        csv_file_path = os.path.join(
            settings.BASE_DIR, 'static', 'data', csv_file)
        with open(csv_file_path, mode='r', encoding='utf-8') as csv_file:
            csv_reader = csv.reader(csv_file)
            next(csv_reader)  # Пропустить заголовок, если он есть
            for row in csv_reader:
                create_function(row)

        self.stdout.write(self.style.SUCCESS(
            f'Успешная загрузка {csv_file} выполнена'))