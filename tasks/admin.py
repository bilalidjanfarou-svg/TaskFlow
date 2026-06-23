from django.contrib import admin
from .models import Task

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'status', 'priority', 'user', 'created_at', 'due_date']
    list_filter = ['status', 'priority', 'created_at', 'user']
    search_fields = ['title', 'description']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    list_editable = ['status', 'priority']
    
    fieldsets = (
        ('Informations principales', {
            'fields': ('title', 'description', 'user')
        }),
        ('Statut et Priorité', {
            'fields': ('status', 'priority')
        }),
        ('Dates', {
            'fields': ('due_date', 'created_at', 'updated_at', 'completed_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ['created_at', 'updated_at', 'completed_at']