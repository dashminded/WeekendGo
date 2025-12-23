from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import feedback

@admin.register(feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('user', 'feedback', 'sentiment')
