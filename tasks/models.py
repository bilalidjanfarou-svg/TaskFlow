from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Task(models.Model):
    """
    Modèle de tâche 
    """
    STATUS_CHOICES = [
        ('TODO', 'À faire'),
        ('IN_PROGRESS', 'En cours'),
        ('DONE', 'Terminé'),
        ('CANCELLED', 'Annulé'),
    ]
    
    PRIORITY_CHOICES = [
        ('LOW', 'Basse'),
        ('MEDIUM', 'Moyenne'),
        ('HIGH', 'Haute'),
        ('URGENT', 'Urgente'),
    ]
    
    title = models.CharField('Titre', max_length=200)
    description = models.TextField('Description', blank=True)
    status = models.CharField(
        'Statut', 
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='TODO'
    )
    priority = models.CharField(
        'Priorité', 
        max_length=20, 
        choices=PRIORITY_CHOICES, 
        default='MEDIUM'
    )
    created_at = models.DateTimeField('Créé le', auto_now_add=True)
    updated_at = models.DateTimeField('Modifié le', auto_now=True)
    due_date = models.DateTimeField('Date limite', null=True, blank=True)
    completed_at = models.DateTimeField('Terminé le', null=True, blank=True)
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='tasks',
        verbose_name='Utilisateur'
    )
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Tâche'
        verbose_name_plural = 'Tâches'
    
    def __str__(self):
        return self.title
    
    def complete(self):
        """Marquer la tâche comme terminée"""
        self.status = 'DONE'
        self.completed_at = timezone.now()
        self.save()
    
    def cancel(self):
        """Annuler la tâche"""
        self.status = 'CANCELLED'
        self.save()
    
    def is_overdue(self):
        """Vérifier si la tâche est en retard"""
        if self.due_date and self.status != 'DONE':
            return timezone.now() > self.due_date
        return False

