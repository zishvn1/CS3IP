# Generated by Django 5.1.1 on 2024-10-08 05:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('listings', '0010_remove_car_color_remove_car_number_of_doors_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='car',
            name='number_of_doors',
            field=models.IntegerField(default=1),
        ),
    ]
