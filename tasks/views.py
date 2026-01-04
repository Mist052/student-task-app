from __future__ import annotations

from datetime import timedelta

from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.views.generic import (
    TemplateView,
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)

from .forms import TaskForm, CourseForm, TagForm
from .models import Task, Course, Tag


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "tasks/dashboard.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user
        now = timezone.now()
        soon = now + timedelta(days=3)

        open_tasks = Task.objects.filter(owner=user).exclude(status=Task.Status.DONE)
        ctx["counts"] = {
            "open": open_tasks.count(),
            "overdue": open_tasks.filter(due_at__lt=now).count(),
            "due_soon": open_tasks.filter(due_at__gte=now, due_at__lte=soon).count(),
            "done": Task.objects.filter(owner=user, status=Task.Status.DONE).count(),
        }
        ctx["next_up"] = open_tasks.filter(Q(due_at__isnull=False)).order_by("due_at")[:8]
        ctx["recent_done"] = Task.objects.filter(owner=user, status=Task.Status.DONE).order_by("-completed_at")[:6]
        return ctx


class OwnedQuerysetMixin:
    """
    Enforces that objects belong to request.user.
    Works for views that use `model = ...`.
    """
    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(owner=self.request.user)


class TaskListView(LoginRequiredMixin, ListView):
    model = Task
    template_name = "tasks/task_list.html"
    context_object_name = "tasks"
    paginate_by = 20

    def get_queryset(self):
        user = self.request.user
        qs = Task.objects.filter(owner=user).select_related("course").prefetch_related("tags")

        q = (self.request.GET.get("q") or "").strip()
        status = (self.request.GET.get("status") or "").strip()
        course_id = (self.request.GET.get("course") or "").strip()
        priority = (self.request.GET.get("priority") or "").strip()
        due = (self.request.GET.get("due") or "").strip()

        if q:
            qs = qs.filter(Q(title__icontains=q) | Q(description__icontains=q) | Q(course__name__icontains=q))

        if status in {c[0] for c in Task.Status.choices}:
            qs = qs.filter(status=status)

        if priority in {c[0] for c in Task.Priority.choices}:
            qs = qs.filter(priority=priority)

        if course_id.isdigit():
            qs = qs.filter(course_id=int(course_id))

        now = timezone.now()
        if due == "overdue":
            qs = qs.exclude(status=Task.Status.DONE).filter(due_at__lt=now)
        elif due == "today":
            start = timezone.localtime(now).replace(hour=0, minute=0, second=0, microsecond=0)
            end = start + timedelta(days=1)
            qs = qs.filter(due_at__gte=start, due_at__lt=end)
        elif due == "soon":
            qs = qs.exclude(status=Task.Status.DONE).filter(due_at__gte=now, due_at__lte=now + timedelta(days=3))

        # Default sort: open tasks first, then due date, then newest
        return qs.order_by("status", "due_at", "-created_at")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user
        ctx["courses"] = Course.objects.filter(owner=user).order_by("name")
        ctx["status_choices"] = Task.Status.choices
        ctx["priority_choices"] = Task.Priority.choices
        ctx["filters"] = {
            "q": self.request.GET.get("q", ""),
            "status": self.request.GET.get("status", ""),
            "course": self.request.GET.get("course", ""),
            "priority": self.request.GET.get("priority", ""),
            "due": self.request.GET.get("due", ""),
        }
        return ctx


class TaskDetailView(LoginRequiredMixin, OwnedQuerysetMixin, DetailView):
    model = Task
    template_name = "tasks/task_detail.html"
    context_object_name = "task"


class TaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    form_class = TaskForm
    template_name = "tasks/task_form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        task: Task = form.save(commit=False)
        task.owner = self.request.user
        if task.status == Task.Status.DONE and not task.completed_at:
            task.completed_at = timezone.now()
        task.save()
        form.save_m2m()
        return redirect("tasks:task_detail", pk=task.pk)


class TaskUpdateView(LoginRequiredMixin, OwnedQuerysetMixin, UpdateView):
    model = Task
    form_class = TaskForm
    template_name = "tasks/task_form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        task: Task = form.save(commit=False)
        if task.status == Task.Status.DONE and not task.completed_at:
            task.completed_at = timezone.now()
        if task.status != Task.Status.DONE:
            task.completed_at = None
        task.save()
        form.save_m2m()
        return redirect("tasks:task_detail", pk=task.pk)


class TaskDeleteView(LoginRequiredMixin, OwnedQuerysetMixin, DeleteView):
    model = Task
    template_name = "tasks/task_confirm_delete.html"
    success_url = reverse_lazy("tasks:task_list")


@require_POST
def toggle_task_done(request: HttpRequest, pk: int) -> HttpResponse:
    if not request.user.is_authenticated:
        return redirect("login")
    task = get_object_or_404(Task, pk=pk, owner=request.user)
    if task.status == Task.Status.DONE:
        task.mark_not_done()
    else:
        task.mark_done()
    task.save()
    next_url = request.POST.get("next") or request.META.get("HTTP_REFERER") or reverse_lazy("tasks:task_list")
    return redirect(next_url)


class CourseListView(LoginRequiredMixin, ListView):
    model = Course
    template_name = "tasks/course_list.html"
    context_object_name = "courses"

    def get_queryset(self):
        return Course.objects.filter(owner=self.request.user).order_by("name")


class CourseCreateView(LoginRequiredMixin, CreateView):
    model = Course
    form_class = CourseForm
    template_name = "tasks/course_form.html"
    success_url = reverse_lazy("tasks:course_list")

    def form_valid(self, form):
        course: Course = form.save(commit=False)
        course.owner = self.request.user
        course.save()
        return redirect(self.success_url)


class CourseUpdateView(LoginRequiredMixin, OwnedQuerysetMixin, UpdateView):
    model = Course
    form_class = CourseForm
    template_name = "tasks/course_form.html"
    success_url = reverse_lazy("tasks:course_list")


class CourseDeleteView(LoginRequiredMixin, OwnedQuerysetMixin, DeleteView):
    model = Course
    template_name = "tasks/course_confirm_delete.html"
    success_url = reverse_lazy("tasks:course_list")


class TagListView(LoginRequiredMixin, ListView):
    model = Tag
    template_name = "tasks/tag_list.html"
    context_object_name = "tags"

    def get_queryset(self):
        return Tag.objects.filter(owner=self.request.user).order_by("name")


class TagCreateView(LoginRequiredMixin, CreateView):
    model = Tag
    form_class = TagForm
    template_name = "tasks/tag_form.html"
    success_url = reverse_lazy("tasks:tag_list")

    def form_valid(self, form):
        tag: Tag = form.save(commit=False)
        tag.owner = self.request.user
        tag.save()
        return redirect(self.success_url)


class TagDeleteView(LoginRequiredMixin, OwnedQuerysetMixin, DeleteView):
    model = Tag
    template_name = "tasks/tag_confirm_delete.html"
    success_url = reverse_lazy("tasks:tag_list")


def signup(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        return redirect("tasks:dashboard")

    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("tasks:dashboard")
    else:
        form = UserCreationForm()
    return render(request, "registration/signup.html", {"form": form})
