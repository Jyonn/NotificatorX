# Generated by Django 3.1.12 on 2022-11-20 14:21

import SmartDjango.models.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Config',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', SmartDjango.models.fields.CharField(max_length=255, unique=True)),
                ('value', SmartDjango.models.fields.CharField(max_length=255)),
            ],
            options={
                'abstract': False,
                'default_manager_name': 'objects',
            },
        ),
    ]
