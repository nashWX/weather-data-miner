# Generated by Django 3.2.5 on 2021-12-16 13:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0008_location_can_retrive_population'),
    ]

    operations = [
        migrations.AlterField(
            model_name='location',
            name='lat',
            field=models.FloatField(blank=True, max_length=50, null=True, verbose_name='Latitude'),
        ),
        migrations.AlterField(
            model_name='location',
            name='lng',
            field=models.FloatField(blank=True, max_length=50, null=True, verbose_name='Longitude'),
        ),
    ]