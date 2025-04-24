from django.contrib import admin
from .models import CommonQuestion, CommonTest, StatementOption, QuizName, NewQuiz, QuizResult

# Register your models here.
admin.site.register(CommonQuestion)

admin.site.register(CommonTest)

admin.site.register(StatementOption)

# admin.site.register(QuizName)

@admin.register(QuizName)
class QuizNameAdmin(admin.ModelAdmin):
    list_display = ('id', 'quiz_name','type', 'category_1', 'category_2', 'category_3', 'category_4')


@admin.register(NewQuiz)
class NewQuizAdmin(admin.ModelAdmin):
    list_display = ('id', 'question', 'option_1', 'option_2', 'option_3', 'option_4', 'quiz')
    search_fields = ('question',)
    list_filter = ('quiz',)


admin.site.register(QuizResult)