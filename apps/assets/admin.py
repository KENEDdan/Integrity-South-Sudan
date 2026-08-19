from django.contrib import admin
from .models import Asset, AssetLog

admin.site.register(Asset)
admin.site.register(AssetLog)