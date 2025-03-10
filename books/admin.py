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