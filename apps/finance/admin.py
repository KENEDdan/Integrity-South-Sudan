from django.contrib import admin
from .models import FinanceBalance, Transaction, FinancialRequest

admin.site.register(FinanceBalance)
admin.site.register(Transaction)
admin.site.register(FinancialRequest)