# Generated by Django 5.0.6 on 2024-06-28 04:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ECom', '0003_alter_cart_table'),
    ]

    operations = [
        migrations.AddField(
            model_name='cart',
            name='count',
            field=models.IntegerField(null=True),
        ),
    ]
