from django.contrib import admin

from .models import Vehiculo


@admin.register(Vehiculo)
class VehiculoAdmin(admin.ModelAdmin):
    list_display = ('marca', 'modelo', 'anio', 'precio', 'stock', 'disponible', 'fecha_publicacion')
    list_filter = ('marca', 'anio', 'disponible')
    search_fields = ('marca', 'modelo')
