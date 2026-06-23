import factory
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Task

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
    
    username = factory.Sequence(lambda n: f'user{n}')
    email = factory.Sequence(lambda n: f'user{n}@example.com')
    password = factory.PostGenerationMethodCall('set_password', 'testpass123')
    first_name = 'Test'
    last_name = 'User'

class TaskFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Task
    
    title = factory.Sequence(lambda n: f'Tâche {n}')
    description = factory.Faker('text', max_nb_chars=200)
    status = 'TODO'
    priority = 'MEDIUM'
    user = factory.SubFactory(UserFactory)
    due_date = factory.LazyFunction(lambda: timezone.now() + timezone.timedelta(days=7))