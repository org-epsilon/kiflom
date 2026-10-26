from django.contrib import admin

from .models import ImagenVehiculo, RegistroAuditoria, Vehiculo


class ImagenVehiculoInline(admin.TabularInline):
    model = ImagenVehiculo
    extra = 1


@admin.register(Vehiculo)
class VehiculoAdmin(admin.ModelAdmin):
    list_display = ('marca', 'modelo', 'anio', 'precio', 'stock', 'disponible', 'fecha_publicacion')
    list_filter = ('marca', 'anio', 'disponible')
    search_fields = ('marca', 'modelo')
    inlines = [ImagenVehiculoInline]


@admin.register(RegistroAuditoria)
class RegistroAuditoriaAdmin(admin.ModelAdmin):
    list_display = ('fecha', 'accion', 'vehiculo_nombre', 'motor_origen', 'motor_destino', 'estado')
    list_filter = ('accion', 'motor_origen', 'estado', 'fecha')
    search_fields = ('vehiculo_nombre', 'vehiculo_uuid', 'detalles')
    readonly_fields = ('fecha',)
