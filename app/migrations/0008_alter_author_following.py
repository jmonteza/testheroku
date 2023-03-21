# Generated by Django 4.1.6 on 2023-02-12 23:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0007_alter_author_following'),
    ]

    operations = [
        migrations.AlterField(
            model_name='author',
            name='following',
            field=models.ManyToManyField(blank=True, related_name='followers', to='app.author'),
        ),
    ]
