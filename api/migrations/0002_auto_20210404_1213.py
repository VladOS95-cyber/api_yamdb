# Generated by Django 3.0.5 on 2021-04-04 09:13

from django.db import migrations, models

import api.validators


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='genre',
            options={'ordering': ('name',), 'verbose_name': 'Жанр', 'verbose_name_plural': 'Жанры'},
        ),
        migrations.AlterField(
            model_name='title',
            name='year',
            field=models.IntegerField(null=True, validators=[api.validators.custom_year_validator], verbose_name='Год'),
        ),
    ]
