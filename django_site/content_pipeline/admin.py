from django.contrib import admin

from .models import PipelineJob


@admin.register(PipelineJob)
class PipelineJobAdmin(admin.ModelAdmin):
    list_display = ('job_type', 'status', 'started_at', 'finished_at', 'created_at')
    list_filter = ('job_type', 'status')
    readonly_fields = ('job_type', 'status', 'log', 'started_at', 'finished_at', 'created_at')

    def has_add_permission(self, request):
        return False
