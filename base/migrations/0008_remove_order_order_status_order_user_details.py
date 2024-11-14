# Generated by Django 5.0.4 on 2024-11-09 23:41

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0007_userdetails'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='order_status',
        ),
        migrations.AddField(
            model_name='order',
            name='user_details',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='base.userdetails'),
        ),
    ]
