# Generated by Django 5.0.3 on 2024-08-05 01:31

import django.contrib.gis.db.models.fields
import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cruises', '0006_alter_route_options_remove_position_coordinates_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='route',
            options={'ordering': ['cruise'], 'verbose_name': 'Route', 'verbose_name_plural': 'Routes'},
        ),
        migrations.AddField(
            model_name='position',
            name='coordinates',
            field=django.contrib.gis.db.models.fields.PointField(blank=True, geography=True, null=True, srid=4326),
        ),
        migrations.CreateModel(
            name='Segment',
            fields=[
                ('segment_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('path', django.contrib.gis.db.models.fields.LineStringField(geography=True, srid=4326)),
                ('end_position', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='end_segments', to='cruises.position')),
                ('leg', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='segments', to='cruises.leg')),
                ('route', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='segments', to='cruises.route')),
                ('start_position', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='start_segments', to='cruises.position')),
            ],
            options={
                'ordering': ['segment_id'],
            },
        ),
    ]
