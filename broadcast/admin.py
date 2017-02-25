from django.contrib import admin
from models import CallStatus, RecordedCall, BroadcastCall

class CallStatusAdmin(admin.ModelAdmin):
    list_display = (
        'from_number',
        'to_number',
        'created',
        'direction',
        'call_status',
        'call_duration',
        'duration',
    )
admin.site.register(CallStatus, CallStatusAdmin)

class RecordedCallAdmin(admin.ModelAdmin):
    list_display = (
        'from_number',
        'to_number',
        'created',
        'direction',
        'call_status',
        'recording_duration',
        'recording_url',
        'digits',
    )
admin.site.register(RecordedCall, RecordedCallAdmin)

class BroadcastCallAdmin(admin.ModelAdmin):
    list_display = (
        'contact_groups_list',
        'access_code',
        'recorded_call',
    )

    def contact_groups_list(self, obj):
        return u", ".join(
            [unicode(group) for group in obj.contact_groups.all()]
        )
admin.site.register(BroadcastCall, BroadcastCallAdmin)
