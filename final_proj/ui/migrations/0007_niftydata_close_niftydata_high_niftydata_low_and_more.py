# Generated by Django 5.0.6 on 2024-07-10 22:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ui', '0006_userprofile'),
    ]

    operations = [
        migrations.AddField(
            model_name='niftydata',
            name='close',
            field=models.FloatField(default=0.0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='niftydata',
            name='high',
            field=models.FloatField(default=0.0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='niftydata',
            name='low',
            field=models.FloatField(default=0.0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='niftydata',
            name='open',
            field=models.FloatField(default=0.0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='stockdata',
            name='close',
            field=models.FloatField(default=0.0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='stockdata',
            name='high',
            field=models.FloatField(default=0.0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='stockdata',
            name='low',
            field=models.FloatField(default=0.0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='stockdata',
            name='open',
            field=models.FloatField(default=0.0),
            preserve_default=False,
        ),
    ]