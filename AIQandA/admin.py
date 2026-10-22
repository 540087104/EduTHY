from django.contrib import admin
from .models import Course, Chapter, QuestionAnswerPair, ChatHistory

admin.site.register(Course)
admin.site.register(Chapter)
admin.site.register(QuestionAnswerPair)
admin.site.register(ChatHistory)
