# Generated by Django 3.1.1 on 2020-09-30 22:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bids',
            name='bid',
            field=models.DecimalField(decimal_places=2, max_digits=19),
        ),
    ]
