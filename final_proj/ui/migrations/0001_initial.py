# Generated by Django 5.0.6 on 2024-07-06 02:44

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='NiftyData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('adj_close', models.FloatField()),
                ('daily_return', models.FloatField()),
                ('cumulative_return', models.FloatField()),
                ('sma_50', models.FloatField()),
                ('sma_200', models.FloatField()),
                ('rsi', models.FloatField()),
                ('upper_bb', models.FloatField()),
                ('lower_bb', models.FloatField()),
                ('obv', models.FloatField()),
                ('force_index', models.FloatField()),
                ('standard_deviation', models.FloatField()),
                ('final_decision', models.CharField(max_length=10)),
                ('market_condition', models.CharField(max_length=10)),
            ],
        ),
    ]
