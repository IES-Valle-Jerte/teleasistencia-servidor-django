# Generated by Django 3.2.3 on 2023-03-10 17:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('teleasistenciaApp', '0015_relacion_terminal_recurso_comunitario_tiempo_estimado'),
    ]

    operations = [
        migrations.AlterField(
            model_name='terminal',
            name='id_titular',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='teleasistenciaApp.paciente'),
        ),
    ]
