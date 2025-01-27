from django.contrib import admin
from .models import District, Store, QualityResolution, Marketplace, DevEmail, EmailBody, Instructions, Chat

admin.site.register(District)
admin.site.register(Store)
admin.site.register(QualityResolution)
admin.site.register(Marketplace)
admin.site.register(DevEmail)
admin.site.register(EmailBody)
admin.site.register(Instructions)
admin.site.register(Chat)
