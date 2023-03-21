# Generated by Django 4.1.6 on 2023-02-24 22:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0010_post'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='post',
            name='receiver',
        ),
        migrations.AddField(
            model_name='post',
            name='receivers',
            field=models.ManyToManyField(blank=True, null=True, related_name='private_posts', to='app.author'),
        ),
        migrations.AlterField(
            model_name='post',
            name='description',
            field=models.CharField(blank=True, max_length=150, null=True, unique=True),
        ),
    ]