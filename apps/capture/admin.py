from django.contrib import admin

from .models import InboxItem


@admin.register(InboxItem)
class InboxItemAdmin(admin.ModelAdmin):
    list_display = ['title', 'captured_at', 'disposition', 'is_processed']
    list_filter = ['disposition']
    search_fields = ['title', 'body']
    readonly_fields = ['captured_at']

    def is_processed(self, obj):
        return obj.is_processed
    is_processed.boolean = True
    is_processed.short_description = 'Processed'
