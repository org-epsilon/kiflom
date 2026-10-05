from django.db import models
from django.utils import timezone

# Create your models here.
class Reporte(models.Model):
    nombre      = models.CharField(max_length=100)
    descripcion = models.TextField()
    #Cada tipo de arhivo va a su subcarpeta dentro de 'media/'
    foto        = models.ImageField(upload_to='reports/images/')
    documento   = models.FileField(upload_to='reports/docs/')
    audio       = models.FileField(upload_to='reports/audios/')
    video       = models.FileField(upload_to='reports/videos/')
    fecha       = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.nombre


class Ubicacion(models.Model):
    TAMANOS_SEDE = [
        ('pequena', 'Pequeña'),
        ('mediana', 'Mediana'),
        ('grande', 'Grande'),
    ]

    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    tamano_sede = models.CharField(max_length=20, choices=TAMANOS_SEDE)
    direccion = models.CharField(max_length=255)
    latitud = models.DecimalField(max_digits=9, decimal_places=6)
    longitud = models.DecimalField(max_digits=9, decimal_places=6)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-fecha_creacion']

    def __str__(self):
        return self.nombre


class Trayectoria(models.Model):
    nombre = models.CharField(max_length=120)
    puntos = models.JSONField(default=list)
    geometria = models.JSONField(default=list)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-fecha_creacion']

    def __str__(self):
        return self.nombre


class Vehiculo(models.Model):
    marca = models.CharField(max_length=80)
    modelo = models.CharField(max_length=120)
    precio = models.DecimalField(max_digits=12, decimal_places=2)
    anio = models.PositiveSmallIntegerField()
    fecha_publicacion = models.DateTimeField(default=timezone.now, editable=False)
    imagen_archivo = models.ImageField(upload_to='vehicles/images/', blank=True)
    imagen_url = models.URLField(max_length=500, blank=True)
    modelo_3d_archivo = models.FileField(upload_to='vehicles/models/', blank=True)
    modelo_3d_url = models.TextField(blank=True)
    modelo_3d_embed_html = models.TextField(blank=True, editable=False)
    combustible = models.CharField(max_length=255, blank=True)
    motor = models.CharField(max_length=255, blank=True)
    transmision = models.CharField(max_length=255, blank=True)
    potencia = models.CharField(max_length=255, blank=True)
    traccion = models.CharField(max_length=255, blank=True)
    carroceria = models.CharField(max_length=255, blank=True)
    sillas = models.PositiveSmallIntegerField(default=2)
    puertas = models.PositiveSmallIntegerField(default=2)
    stock = models.PositiveIntegerField(default=0)
    descripcion = models.TextField(blank=True)
    disponible = models.BooleanField(default=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-fecha_publicacion', '-id']

    def __str__(self):
        return f'{self.marca} {self.modelo}'