import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from .models import Task
from .factories import TaskFactory, UserFactory

@pytest.fixture
def api_client():
    """Client API pour les tests"""
    return APIClient()

@pytest.fixture
def auth_client(api_client):
    """Client API authentifié"""
    user = User.objects.create_user(username='testuser', password='testpass123')
    token = Token.objects.create(user=user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
    api_client.user = user
    return api_client

@pytest.fixture
def auth_client_with_tasks(auth_client):
    """Client API avec des tâches pré-créées"""
    user = auth_client.user
    tasks = TaskFactory.create_batch(5, user=user)
    return auth_client, tasks

@pytest.mark.django_db
class TestTaskAPI:
    
    def test_create_task(self, auth_client):
        """Test de création d'une tâche via l'API"""
        data = {
            'title': 'Nouvelle tâche API',
            'description': 'Description de la tâche API',
            'priority': 'HIGH',
            'due_date': '2025-01-01T10:00:00Z'
        }
        response = auth_client.post('/api/tasks/', data)
        assert response.status_code == 201
        assert response.data['title'] == 'Nouvelle tâche API'
        assert response.data['user'] == auth_client.user.username
    
    def test_list_tasks(self, auth_client):
        """Test de la liste des tâches"""
        user = auth_client.user
        Task.objects.create(title='Tâche 1', user=user)
        Task.objects.create(title='Tâche 2', user=user)
        
        response = auth_client.get('/api/tasks/')
        assert response.status_code == 200
        assert len(response.data['results']) == 2
    
    def test_retrieve_task(self, auth_client):
        """Test de récupération d'une tâche spécifique"""
        user = auth_client.user
        task = Task.objects.create(title='Tâche spécifique', user=user)
        
        response = auth_client.get(f'/api/tasks/{task.id}/')
        assert response.status_code == 200
        assert response.data['title'] == 'Tâche spécifique'
    
    def test_update_task(self, auth_client):
        """Test de mise à jour d'une tâche"""
        user = auth_client.user
        task = Task.objects.create(title='Ancien titre', user=user)
        
        data = {'title': 'Nouveau titre', 'status': 'IN_PROGRESS'}
        response = auth_client.patch(f'/api/tasks/{task.id}/', data)
        assert response.status_code == 200
        assert response.data['title'] == 'Nouveau titre'
        assert response.data['status'] == 'IN_PROGRESS'
    
    def test_delete_task(self, auth_client):
        """Test de suppression d'une tâche"""
        user = auth_client.user
        task = Task.objects.create(title='Tâche à supprimer', user=user)
        
        response = auth_client.delete(f'/api/tasks/{task.id}/')
        assert response.status_code == 204
        assert not Task.objects.filter(id=task.id).exists()
    
    def test_complete_task_action(self, auth_client):
        """Test de l'action complète d'une tâche"""
        user = auth_client.user
        task = Task.objects.create(title='Tâche à compléter', user=user)
        
        response = auth_client.post(f'/api/tasks/{task.id}/complete/')
        assert response.status_code == 200
        assert response.data['task']['status'] == 'DONE'
    
    def test_cancel_task_action(self, auth_client):
        """Test de l'action annuler une tâche"""
        user = auth_client.user
        task = Task.objects.create(title='Tâche à annuler', user=user)
        
        response = auth_client.post(f'/api/tasks/{task.id}/cancel/')
        assert response.status_code == 200
        assert response.data['task']['status'] == 'CANCELLED'
    
    def test_task_stats(self, auth_client):
        """Test des statistiques des tâches"""
        user = auth_client.user
        Task.objects.create(title='Todo 1', status='TODO', user=user)
        Task.objects.create(title='Todo 2', status='TODO', user=user)
        Task.objects.create(title='In Progress', status='IN_PROGRESS', user=user)
        Task.objects.create(title='Done', status='DONE', user=user)
        
        response = auth_client.get('/api/tasks/stats/')
        assert response.status_code == 200
        assert response.data['total'] == 4
        assert response.data['todo'] == 2
        assert response.data['in_progress'] == 1
        assert response.data['done'] == 1
    
    def test_task_filtering(self, auth_client):
        """Test du filtrage des tâches"""
        user = auth_client.user
        Task.objects.create(title='Tâche haute', priority='HIGH', user=user)
        Task.objects.create(title='Tâche moyenne', priority='MEDIUM', user=user)
        Task.objects.create(title='Tâche basse', priority='LOW', user=user)
        
        response = auth_client.get('/api/tasks/?priority=HIGH')
        assert response.status_code == 200
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['priority'] == 'HIGH'
    
    def test_task_search(self, auth_client):
        """Test de recherche dans les tâches"""
        user = auth_client.user
        Task.objects.create(title='Projet urgent', user=user)
        Task.objects.create(title='Projet normal', user=user)
        Task.objects.create(title='Autre tâche', user=user)
        
        response = auth_client.get('/api/tasks/?search=urgent')
        assert response.status_code == 200
        assert len(response.data['results']) == 1
        assert 'urgent' in response.data['results'][0]['title'].lower()

@pytest.mark.django_db
class TestAuthentication:
    
    def test_unauthorized_access(self, api_client):
        """Test d'accès non authentifié"""
        response = api_client.get('/api/tasks/')
        assert response.status_code == 401
    
    def test_token_authentication(self, api_client):
        """Test d'authentification par token"""
        user = User.objects.create_user(username='testuser', password='test123')
        token = Token.objects.create(user=user)
        
        api_client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        response = api_client.get('/api/tasks/')
        assert response.status_code == 200
    
    def test_invalid_token(self, api_client):
        """Test avec token invalide"""
        api_client.credentials(HTTP_AUTHORIZATION='Token invalidtoken123')
        response = api_client.get('/api/tasks/')
        assert response.status_code == 401