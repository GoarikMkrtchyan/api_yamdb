from django.contrib import admin

from .models import Category, Comment, Genre, GenreTitle, Review, Title


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'year', 'category', 'description')
    search_fields = ('name',)
    list_filter = ('year', 'category')
    raw_id_fields = ('category',)
    autocomplete_fields = ('genre',)


@admin.register(GenreTitle)
class GenreTitleAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'genre')
    search_fields = ('title', 'genre')


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'author', 'score', 'pub_date')
    search_fields = ('title', 'author')
    list_filter = ('score', 'pub_date')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'review', 'text', 'author', 'pub_date')
    search_fields = ('review', 'author')
