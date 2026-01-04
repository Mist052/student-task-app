from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils import timezone


class Course(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='courses',
    )
    name = models.CharField(max_length=120)
    color = models.CharField(max_length=7, default='#3B82F6')  # Hex like #RRGGBB
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [('owner', 'name')]
        ordering = ['name']

    def __str__(self) -> str:
        return self.name


class Tag(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='tags',
    )
    name = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [('owner', 'name')]
        ordering = ['name']

    def __str__(self) -> str:
        return self.name


class Task(models.Model):
    class Priority(models.TextChoices):
        LOW = 'LOW', 'Low'
        MEDIUM = 'MED', 'Medium'
        HIGH = 'HIGH', 'High'
        URGENT = 'URG', 'Urgent'

    class Status(models.TextChoices):
        TODO = 'TODO', 'To do'
        IN_PROGRESS = 'INPR', 'In progress'
        DONE = 'DONE', 'Done'

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='tasks',
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    course = models.ForeignKey(
        Course,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tasks',
    )
    tags = models.ManyToManyField(Tag, blank=True, related_name='tasks')

    due_at = models.DateTimeField(null=True, blank=True)
    priority = models.CharField(max_length=5, choices=Priority.choices, default=Priority.MEDIUM)
    status = models.CharField(max_length=4, choices=Status.choices, default=Status.TODO)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['status', 'due_at', '-created_at']

    def __str__(self) -> str:
        return self.title

    def mark_done(self) -> None:
        self.status = self.Status.DONE
        if not self.completed_at:
            self.completed_at = timezone.now()

    def mark_not_done(self) -> None:
        if self.status == self.Status.DONE:
            self.status = self.Status.TODO
        self.completed_at = None

    @property
    def is_overdue(self) -> bool:
        return bool(self.due_at and self.status != self.Status.DONE and self.due_at < timezone.now())
