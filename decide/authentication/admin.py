from django.contrib import admin

from authentication.models import CustomUser, UserChange

@admin.register(CustomUser)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name']
    search_fields = ['email', 'username']

@admin.register(UserChange)
class UserChangeAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'fecha', 'campo_modificado', 'dato_anterior', 'dato_nuevo']
    
