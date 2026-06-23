

from django.apps import AppConfig

class TasksConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tasks'  
class TaskflowConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'taskflow'