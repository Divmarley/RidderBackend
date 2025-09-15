from django.contrib import admin

from accounts.models import CustomUser

# Register your models here.

from .models import APKUpload

@admin.register(APKUpload)
class APKUploadAdmin(admin.ModelAdmin):
    list_display = ('name', 'version', 'uploaded_at')
    search_fields = ('name', 'version')
admin.site.register(CustomUser)