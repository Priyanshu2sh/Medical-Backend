from django.contrib import admin
from .models import MedicalHealthUser, CommonQuestion, CommonTest, StatementOption, QuizName, NewQuiz, QuizResult,McqQuiz, McqQuestions, McqQuizResult

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



@admin.register(McqQuiz)
class McqQuizAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'type']
    search_fields = ['name', 'description']
    # filter_horizontal = ['questions']

@admin.register(McqQuestions)
class McqQuestionsAdmin(admin.ModelAdmin):
    list_display = ['id', 'question', 'type']
    search_fields = ['question']


@admin.register(McqQuizResult)
class QuizResultAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'quiz', 'score', 'total_questions', 'submitted_at')
    search_fields = ('user_id__username', 'quiz__name')
    list_filter = ('quiz', 'score')
   
admin.site.register(MedicalHealthUser)