# Generated by Django 5.0.6 on 2024-06-29 04:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ECom', '0005_checkout'),
    ]

    operations = [
        migrations.AddField(
            model_name='checkout',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]
