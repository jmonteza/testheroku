# Generated by Django 4.1.7 on 2023-03-11 02:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0021_merge_20230303_1653'),
    ]

    operations = [
        migrations.CreateModel(
            name='Node',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=255)),
                ('password', models.CharField(max_length=255)),
            ],
        ),
    ]
