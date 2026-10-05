from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('app_deportivos_guadalupe', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Trayectoria',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=120)),
                ('puntos', models.JSONField(default=list)),
                ('geometria', models.JSONField(default=list)),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True)),
                ('fecha_actualizacion', models.DateTimeField(auto_now=True)),
            ],
            options={'ordering': ['-fecha_creacion']},
        ),
        migrations.CreateModel(
            name='Ubicacion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
                ('descripcion', models.TextField(blank=True)),
                ('tamano_sede', models.CharField(choices=[('pequena', 'Pequeña'), ('mediana', 'Mediana'), ('grande', 'Grande')], max_length=20)),
                ('direccion', models.CharField(max_length=255)),
                ('latitud', models.DecimalField(decimal_places=6, max_digits=9)),
                ('longitud', models.DecimalField(decimal_places=6, max_digits=9)),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True)),
                ('fecha_actualizacion', models.DateTimeField(auto_now=True)),
            ],
            options={'ordering': ['-fecha_creacion']},
        ),
    ]