from django.contrib import admin
from .models import Feedback
# Register your models here.

from .models import Complaint

@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'title', 'category', 'status', 'created_at')
    list_filter = ('status', 'category')
    search_fields = ('title', 'user__username')
    list_editable = ('status',)
    ordering = ('-created_at',)
    
@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'message', 'created_at')
    list_filter = ('created_at', 'user')
    search_fields = ('message', 'user__username')
    ordering = ('-created_at',)