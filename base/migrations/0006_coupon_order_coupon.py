# Generated by Django 5.0.4 on 2024-11-08 02:30

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0005_orderitem_color_orderitem_size'),
    ]

    operations = [
        migrations.CreateModel(
            name='Coupon',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=15, unique=True)),
                ('percent_off', models.PositiveIntegerField(blank=True, null=True)),
                ('expiry_date', models.DateField(blank=True, null=True)),
                ('max_usage', models.PositiveIntegerField(default=1)),
                ('usage_count', models.PositiveIntegerField(default=0)),
                ('active', models.BooleanField(default=True)),
            ],
        ),
        migrations.AddField(
            model_name='order',
            name='coupon',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='orders', to='base.coupon'),
        ),
    ]
