from django.contrib import admin
from .models import CustomUser,Category,Transaction,Budget

admin.site.register(CustomUser)
admin.site.register(Category)
admin.site.register(Transaction)
admin.site.register(Budget)
