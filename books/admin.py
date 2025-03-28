from django.contrib import admin
from .models import *
# Register your models here.
@admin.register(Books)
class AdminBooks(admin.ModelAdmin):
    list_display = ['id', 'name', 'version']

@admin.register(Descriptions)
class AdminBooks(admin.ModelAdmin):
    list_display = ['id', 'book', 'code', 'description']

@admin.register(SubDescriptions)
class AdminBooks(admin.ModelAdmin):
    list_display = ['id', 'description', 'code', 'sub_description']

@admin.register(CodeReaction)
class AdminCodeReaction(admin.ModelAdmin):
    list_display = ['id', 'user', 'description', 'like', 'dislike']
    list_filter = ['like', 'dislike']
    search_fields = ['user__username', 'description__code']