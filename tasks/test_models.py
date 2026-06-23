import pytest
from django.utils import timezone
from django.contrib.auth.models import User
from .models import Task

@pytest.mark.django_db
class TestTaskModel:
    
    def test_create_task(self):
        """Test de création d'une tâche"""
        user = User.objects.create_user(username='testuser', password='test123')
        task = Task.objects.create(
            title='Ma tâche de test',
            description='Description de test',
            user=user,
            priority='HIGH'
        )
        assert task.title == 'Ma tâche de test'
        assert task.status == 'TODO'
        assert str(task) == 'Ma tâche de test'
    
    def test_complete_task(self):
        """Test de la méthode complete()"""
        user = User.objects.create_user(username='testuser', password='test123')
        task = Task.objects.create(
            title='Tâche à compléter',
            user=user
        )
        task.complete()
        assert task.status == 'DONE'
        assert task.completed_at is not None
    
    def test_cancel_task(self):
        """Test de la méthode cancel()"""
        user = User.objects.create_user(username='testuser', password='test123')
        task = Task.objects.create(
            title='Tâche à annuler',
            user=user
        )
        task.cancel()
        assert task.status == 'CANCELLED'
    
    def test_is_overdue(self):
        """Test de la vérification de retard"""
        user = User.objects.create_user(username='testuser', password='test123')
        
        # Tâche en retard
        overdue_task = Task.objects.create(
            title='Tâche en retard',
            user=user,
            due_date=timezone.now() - timezone.timedelta(days=1)
        )
        assert overdue_task.is_overdue() is True
        
        # Tâche pas en retard
        not_overdue_task = Task.objects.create(
            title='Tâche dans le futur',
            user=user,
            due_date=timezone.now() + timezone.timedelta(days=1)
        )
        assert not_overdue_task.is_overdue() is False
        
        # Tâche terminée
        done_task = Task.objects.create(
            title='Tâche terminée',
            user=user,
            status='DONE',
            due_date=timezone.now() - timezone.timedelta(days=1)
        )
        assert done_task.is_overdue() is False