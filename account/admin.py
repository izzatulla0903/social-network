from django.contrib import admin

from .models import CustomUser
from account.models import CustomUser
from .models import Contact

admin.site.register(CustomUser)
admin.site.register(Contact)