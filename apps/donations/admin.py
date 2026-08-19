from django.contrib import admin
from .models import Donation, DonationSettings

admin.site.register(Donation)
admin.site.register(DonationSettings)