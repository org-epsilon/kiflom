from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_deportivos_guadalupe', '0006_vehiculo_modelo_3d_embed_html_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vehiculo',
            name='carroceria',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='vehiculo',
            name='combustible',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='vehiculo',
            name='motor',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='vehiculo',
            name='potencia',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='vehiculo',
            name='transmision',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='vehiculo',
            name='traccion',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
