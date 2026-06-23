from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from .models import Task

class TaskModelTest(TestCase):
    """Tests pour le modèle Task"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='test123'
        )
    
    def test_create_task(self):
        """Test de création d'une tâche"""
        task = Task.objects.create(
            title='Ma tâche de test',
            description='Description de test',
            user=self.user,
            priority='HIGH'
        )
        self.assertEqual(task.title, 'Ma tâche de test')
        self.assertEqual(task.status, 'TODO')
        self.assertEqual(str(task), 'Ma tâche de test')
    
    def test_complete_task(self):
        """Test de la méthode complete()"""
        task = Task.objects.create(
            title='Tâche à compléter',
            user=self.user
        )
        task.complete()
        self.assertEqual(task.status, 'DONE')
        self.assertIsNotNone(task.completed_at)
    
    def test_cancel_task(self):
        """Test de la méthode cancel()"""
        task = Task.objects.create(
            title='Tâche à annuler',
            user=self.user
        )
        task.cancel()
        self.assertEqual(task.status, 'CANCELLED')
    
    def test_is_overdue(self):
        """Test de la vérification de retard"""
        # Tâche en retard
        overdue_task = Task.objects.create(
            title='Tâche en retard',
            user=self.user,
            due_date=timezone.now() - timezone.timedelta(days=1)
        )
        self.assertTrue(overdue_task.is_overdue())
        
        # Tâche pas en retard
        not_overdue_task = Task.objects.create(
            title='Tâche dans le futur',
            user=self.user,
            due_date=timezone.now() + timezone.timedelta(days=1)
        )
        self.assertFalse(not_overdue_task.is_overdue())

class TaskAPITest(TestCase):
    """Tests pour l'API des tâches"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='test123'
        )
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
    
    def test_create_task_api(self):
        """Test de création d'une tâche via l'API"""
        data = {
            'title': 'Nouvelle tâche API',
            'description': 'Description de la tâche API',
            'priority': 'HIGH'
        }
        response = self.client.post('/api/tasks/', data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['title'], 'Nouvelle tâche API')
        self.assertEqual(response.data['user'], self.user.username)
    
    def test_list_tasks_api(self):
        """Test de la liste des tâches"""
        Task.objects.create(title='Tâche 1', user=self.user)
        Task.objects.create(title='Tâche 2', user=self.user)
        
        response = self.client.get('/api/tasks/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('results', response.data)
        self.assertEqual(len(response.data['results']), 2)
    
    def test_retrieve_task_api(self):
        """Test de récupération d'une tâche spécifique"""
        task = Task.objects.create(title='Tâche spécifique', user=self.user)
        
        response = self.client.get(f'/api/tasks/{task.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['title'], 'Tâche spécifique')
    
    def test_update_task_api(self):
        """Test de mise à jour d'une tâche"""
        task = Task.objects.create(title='Ancien titre', user=self.user)
        
        data = {'title': 'Nouveau titre', 'status': 'IN_PROGRESS'}
        response = self.client.patch(f'/api/tasks/{task.id}/', data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['title'], 'Nouveau titre')
        self.assertEqual(response.data['status'], 'IN_PROGRESS')
    
    def test_delete_task_api(self):
        """Test de suppression d'une tâche"""
        task = Task.objects.create(title='Tâche à supprimer', user=self.user)
        
        response = self.client.delete(f'/api/tasks/{task.id}/')
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Task.objects.filter(id=task.id).exists())
    
    def test_complete_task_action(self):
        """Test de l'action complète d'une tâche"""
        task = Task.objects.create(title='Tâche à compléter', user=self.user)
        
        response = self.client.post(f'/api/tasks/{task.id}/complete/')
        self.assertEqual(response.status_code, 200)
        task.refresh_from_db()
        self.assertEqual(task.status, 'DONE')
    
    def test_cancel_task_action(self):
        """Test de l'action annuler une tâche"""
        task = Task.objects.create(title='Tâche à annuler', user=self.user)
        
        response = self.client.post(f'/api/tasks/{task.id}/cancel/')
        self.assertEqual(response.status_code, 200)
        task.refresh_from_db()
        self.assertEqual(task.status, 'CANCELLED')
    
    def test_task_stats_api(self):
        """Test des statistiques des tâches"""
        Task.objects.create(title='Todo 1', status='TODO', user=self.user)
        Task.objects.create(title='Todo 2', status='TODO', user=self.user)
        Task.objects.create(title='In Progress', status='IN_PROGRESS', user=self.user)
        Task.objects.create(title='Done', status='DONE', user=self.user)
        
        response = self.client.get('/api/tasks/stats/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['total'], 4)
        self.assertEqual(response.data['todo'], 2)
        self.assertEqual(response.data['in_progress'], 1)
        self.assertEqual(response.data['done'], 1)
    
    def test_task_overdue_api(self):
        """Test de récupération des tâches en retard"""
        # Créer une tâche en retard
        overdue_task = Task.objects.create(
            title='Tâche en retard',
            user=self.user,
            due_date=timezone.now() - timezone.timedelta(days=1)
        )
        
        # Créer une tâche à jour
        not_overdue_task = Task.objects.create(
            title='Tâche à jour',
            user=self.user,
            due_date=timezone.now() + timezone.timedelta(days=1)
        )
        
        response = self.client.get('/api/tasks/overdue/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Tâche en retard')

class AuthenticationTest(TestCase):
    """Tests d'authentification"""
    
    def test_unauthorized_access(self):
        """Test d'accès non authentifié"""
        client = APIClient()
        response = client.get('/api/tasks/')
        self.assertEqual(response.status_code, 401)
    
    def test_token_authentication(self):
        """Test d'authentification par token"""
        user = User.objects.create_user(username='testuser', password='test123')
        token = Token.objects.create(user=user)
        
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        response = client.get('/api/tasks/')
        self.assertEqual(response.status_code, 200)
    
    def test_invalid_token(self):
        """Test avec token invalide"""
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token invalidtoken123')
        response = client.get('/api/tasks/')
        self.assertEqual(response.status_code, 401)

class UserViewSetTest(TestCase):
    """Tests pour UserViewSet"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='test123',
            email='test@example.com',
            first_name='Test',
            last_name='User'
        )
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
    
    def test_get_me(self):
        """Test de récupération de l'utilisateur connecté"""
        response = self.client.get('/api/users/me/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['username'], 'testuser')
        self.assertEqual(response.data['email'], 'test@example.com')