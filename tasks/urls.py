from django.urls import path
from . import views

app_name = "tasks"

urlpatterns = [
    path("", views.DashboardView.as_view(), name="dashboard"),

    path("tasks/", views.TaskListView.as_view(), name="task_list"),
    path("tasks/new/", views.TaskCreateView.as_view(), name="task_create"),
    path("tasks/<int:pk>/", views.TaskDetailView.as_view(), name="task_detail"),
    path("tasks/<int:pk>/edit/", views.TaskUpdateView.as_view(), name="task_update"),
    path("tasks/<int:pk>/delete/", views.TaskDeleteView.as_view(), name="task_delete"),
    path("tasks/<int:pk>/toggle-done/", views.toggle_task_done, name="task_toggle_done"),

    path("courses/", views.CourseListView.as_view(), name="course_list"),
    path("courses/new/", views.CourseCreateView.as_view(), name="course_create"),
    path("courses/<int:pk>/edit/", views.CourseUpdateView.as_view(), name="course_update"),
    path("courses/<int:pk>/delete/", views.CourseDeleteView.as_view(), name="course_delete"),

    path("tags/", views.TagListView.as_view(), name="tag_list"),
    path("tags/new/", views.TagCreateView.as_view(), name="tag_create"),
    path("tags/<int:pk>/delete/", views.TagDeleteView.as_view(), name="tag_delete"),
]
