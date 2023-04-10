# Generated by Django 3.2.3 on 2023-04-10 09:08

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('teleasistenciaApp', '0015_relacion_terminal_recurso_comunitario_tiempo_estimado'),
    ]

    operations = [
        migrations.CreateModel(
            name='Alarma_Programada',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_registro', models.DateTimeField(default=django.utils.timezone.now)),
                ('id_paciente_ucr', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='teleasistenciaApp.paciente')),
                ('id_terminal', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='teleasistenciaApp.terminal')),
                ('id_tipo_alarma', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='teleasistenciaApp.tipo_alarma')),
            ],
        ),
    ]