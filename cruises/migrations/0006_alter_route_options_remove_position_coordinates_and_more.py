# Generated by Django 5.0.3 on 2024-08-04 13:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cruises', '0005_alter_route_options_route_color_route_description_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='route',
            options={'ordering': ['cruise__cruise_name'], 'verbose_name': 'Route', 'verbose_name_plural': 'Routes'},
        ),
        migrations.RemoveField(
            model_name='position',
            name='coordinates',
        ),
        migrations.RemoveField(
            model_name='route',
            name='color',
        ),
        migrations.RemoveField(
            model_name='route',
            name='description',
        ),
        migrations.RemoveField(
            model_name='route',
            name='end_date',
        ),
        migrations.RemoveField(
            model_name='route',
            name='length',
        ),
        migrations.RemoveField(
            model_name='route',
            name='name',
        ),
        migrations.RemoveField(
            model_name='route',
            name='start_date',
        ),
    ]