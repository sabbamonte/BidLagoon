# Generated by Django 3.1.1 on 2020-10-02 18:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0005_auto_20201002_1806'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='title',
            field=models.CharField(default=None, max_length=64),
        ),
    ]