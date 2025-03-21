from django.contrib import admin
from .models import CommonQuestion, CommonTest, StatementOption

# Register your models here.
admin.site.register(CommonQuestion)

admin.site.register(CommonTest)

admin.site.register(StatementOption)

