# Generated by Django 3.2.3 on 2023-03-30 09:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teleasistenciaApp', '0016_alter_terminal_id_titular'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tipo_agenda',
            name='codigo',
            field=models.CharField(max_length=100),
        ),
    ]
