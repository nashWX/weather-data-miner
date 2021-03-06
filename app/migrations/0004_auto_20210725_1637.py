# Generated by Django 3.2.5 on 2021-07-25 10:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_auto_20210724_1455'),
    ]

    operations = [
        migrations.AlterField(
            model_name='location',
            name='location_id',
            field=models.CharField(max_length=100, null=True, verbose_name='Location id'),
        ),
        migrations.AlterField(
            model_name='warning',
            name='warning_type',
            field=models.CharField(choices=[('TORNADO', 'Tornado'), ('FLOOD', 'Flood'), ('TSTORM', 'T Storm')], default='TORNADO', max_length=20),
        ),
    ]
