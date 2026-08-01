from django.contrib import admin

from .models import Mailing, MailingAttempt


class MailingAttemptInline(admin.TabularInline):
    model = MailingAttempt
    extra = 0
    readonly_fields = ('attempt_time', 'status', 'server_response', 'recipient')
    can_delete = False


@admin.register(Mailing)
class MailingAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'status', 'start_time', 'end_time', 'owner', 'is_disabled')
    list_filter = ('status', 'is_disabled')
    filter_horizontal = ('recipients',)
    inlines = [MailingAttemptInline]


@admin.register(MailingAttempt)
class MailingAttemptAdmin(admin.ModelAdmin):
    list_display = ('mailing', 'recipient', 'status', 'attempt_time')
    list_filter = ('status',)
    readonly_fields = ('attempt_time',)
