# Generated by Django 2.1.5 on 2019-01-17 18:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('smsgateway', '0003_auto_20171012_1427'),
    ]

    operations = [
        migrations.AlterField(
            model_name='queuedsms',
            name='reliable',
            field=models.BooleanField(blank=True, default=False, verbose_name='is reliable'),
        ),
    ]
