from django.contrib import admin
from .models import Course, Tag, Task


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'created_at')
    search_fields = ('name', 'owner__username', 'owner__email')
    list_filter = ('created_at',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'created_at')
    search_fields = ('name', 'owner__username', 'owner__email')
    list_filter = ('created_at',)


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'status', 'priority', 'due_at', 'course', 'created_at')
    search_fields = ('title', 'description', 'owner__username', 'owner__email')
    list_filter = ('status', 'priority', 'course', 'created_at')
    autocomplete_fields = ('course', 'tags')
