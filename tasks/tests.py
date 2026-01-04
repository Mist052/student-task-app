from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Task


User = get_user_model()


class OwnershipTests(TestCase):
    def setUp(self):
        self.u1 = User.objects.create_user(username="u1", password="pass12345")
        self.u2 = User.objects.create_user(username="u2", password="pass12345")
        self.t1 = Task.objects.create(owner=self.u1, title="Task 1")
        self.t2 = Task.objects.create(owner=self.u2, title="Task 2")

    def test_user_cannot_view_other_users_task_detail(self):
        self.client.login(username="u1", password="pass12345")
        resp = self.client.get(reverse("tasks:task_detail", kwargs={"pk": self.t2.pk}))
        self.assertEqual(resp.status_code, 404)

    def test_task_list_only_shows_own_tasks(self):
        self.client.login(username="u1", password="pass12345")
        resp = self.client.get(reverse("tasks:task_list"))
        self.assertContains(resp, "Task 1")
        self.assertNotContains(resp, "Task 2")
