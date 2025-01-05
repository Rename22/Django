# Generated by Django 5.1.4 on 2025-01-02 15:18

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Compra_venta', '0003_orden'),
    ]

    operations = [
        migrations.CreateModel(
            name='Notificacion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mensaje', models.TextField()),
                ('tipo', models.CharField(choices=[('Nueva solicitud', 'Nueva solicitud'), ('Aceptada', 'Aceptada'), ('Rechazada', 'Rechazada'), ('Completada', 'Completada')], max_length=50)),
                ('leida', models.BooleanField(default=False)),
                ('creado_en', models.DateTimeField(auto_now_add=True)),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notificaciones', to='Compra_venta.usuario')),
            ],
        ),
    ]
