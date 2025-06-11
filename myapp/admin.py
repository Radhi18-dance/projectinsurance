from django.contrib import admin
from .models import *
# Register your models here.
class loginAdmin(admin.ModelAdmin):
    list_display=['username','password']
    

admin.site.register(login_tbl,loginAdmin)