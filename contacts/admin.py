from django.contrib import admin
from models import ContactGroup, Contact

class ContactGroupAdmin(admin.ModelAdmin):
    list_display = ('name',)
    filter_horizontal = ('contacts',)
admin.site.register(ContactGroup, ContactGroupAdmin)

class ContactAdmin(admin.ModelAdmin):
    list_display = ('name','phone_number','type',)
admin.site.register(Contact, ContactAdmin)
