from django.db import migrations, models


def seed_vehicles(apps, schema_editor):
    Vehiculo = apps.get_model('app_deportivos_guadalupe', 'Vehiculo')
    vehicles = [
        {
            'marca': 'Porsche', 'modelo': '911 GT3 RS', 'precio': '220000', 'anio': 2024,
            'imagen_url': 'https://images.unsplash.com/photo-1503376780353-7e6692767b70?auto=format&fit=crop&w=1200&q=85',
            'modelo_3d_url': '', 'combustible': 'Gasolina', 'motor': '4.0L bóxer, 6 cilindros',
            'transmision': 'Automática PDK de 7 velocidades', 'potencia': '518 hp / 296 km/h',
            'traccion': 'Trasera', 'carroceria': 'Coupé', 'sillas': 2, 'puertas': 2, 'stock': 2,
            'descripcion': 'Un deportivo de circuito homologado para carretera, con aerodinámica activa, respuesta inmediata y una experiencia de conducción purista.',
        },
        {
            'marca': 'Ferrari', 'modelo': 'F8 Tributo', 'precio': '280000', 'anio': 2023,
            'imagen_url': 'https://images.unsplash.com/photo-1592198084033-aade902d1aae?auto=format&fit=crop&w=1200&q=85',
            'modelo_3d_url': '', 'combustible': 'Gasolina', 'motor': '3.9L V8 biturbo',
            'transmision': 'Automática de 7 velocidades', 'potencia': '710 hp / 340 km/h',
            'traccion': 'Trasera', 'carroceria': 'Berlinetta', 'sillas': 2, 'puertas': 2, 'stock': 1,
            'descripcion': 'La esencia de Ferrari en una berlinetta de motor central: ligera, explosiva y diseñada para convertir cada curva en una experiencia memorable.',
        },
        {
            'marca': 'Chevrolet', 'modelo': 'Corvette Z06', 'precio': '110000', 'anio': 2024,
            'imagen_url': 'https://images.unsplash.com/photo-1617814076367-b759c7d7e738?auto=format&fit=crop&w=1200&q=85',
            'modelo_3d_url': '', 'combustible': 'Gasolina', 'motor': '5.5L V8 atmosférico',
            'transmision': 'Doble embrague de 8 velocidades', 'potencia': '670 hp / 312 km/h',
            'traccion': 'Trasera', 'carroceria': 'Coupé', 'sillas': 2, 'puertas': 2, 'stock': 4,
            'descripcion': 'Un V8 de altas revoluciones con arquitectura de competición, equilibrio preciso y una presencia que no pasa desapercibida.',
        },
        {
            'marca': 'Nissan', 'modelo': 'GT-R Nismo', 'precio': '210000', 'anio': 2024,
            'imagen_url': 'https://images.unsplash.com/photo-1558981806-ec527fa84c39?auto=format&fit=crop&w=1200&q=85',
            'modelo_3d_url': '', 'combustible': 'Gasolina', 'motor': '3.8L V6 biturbo',
            'transmision': 'Doble embrague de 6 velocidades', 'potencia': '600 hp / 315 km/h',
            'traccion': 'Integral ATTESA E-TS', 'carroceria': 'Coupé', 'sillas': 4, 'puertas': 2, 'stock': 1,
            'descripcion': 'Tecnología de competición para la calle: tracción integral, precisión japonesa y una aceleración capaz de desafiar cualquier expectativa.',
        },
    ]
    for vehicle in vehicles:
        Vehiculo.objects.create(**vehicle)


class Migration(migrations.Migration):
    dependencies = [('app_deportivos_guadalupe', '0002_ubicacion_trayectoria')]

    operations = [
        migrations.CreateModel(
            name='Vehiculo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('marca', models.CharField(max_length=80)),
                ('modelo', models.CharField(max_length=120)),
                ('precio', models.DecimalField(decimal_places=2, max_digits=12)),
                ('anio', models.PositiveSmallIntegerField()),
                ('imagen_url', models.URLField(blank=True, max_length=500)),
                ('modelo_3d_url', models.URLField(blank=True, max_length=500)),
                ('combustible', models.CharField(blank=True, max_length=60)),
                ('motor', models.CharField(blank=True, max_length=100)),
                ('transmision', models.CharField(blank=True, max_length=80)),
                ('potencia', models.CharField(blank=True, max_length=80)),
                ('traccion', models.CharField(blank=True, max_length=60)),
                ('carroceria', models.CharField(blank=True, max_length=80)),
                ('sillas', models.PositiveSmallIntegerField(default=2)),
                ('puertas', models.PositiveSmallIntegerField(default=2)),
                ('stock', models.PositiveIntegerField(default=0)),
                ('descripcion', models.TextField(blank=True)),
                ('disponible', models.BooleanField(default=True)),
                ('fecha_actualizacion', models.DateTimeField(auto_now=True)),
            ],
            options={'ordering': ['marca', '-anio', 'modelo']},
        ),
        migrations.RunPython(seed_vehicles, migrations.RunPython.noop),
    ]
