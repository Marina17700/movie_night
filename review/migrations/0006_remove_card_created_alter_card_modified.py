# Generated by Django 4.0.2 on 2022-06-02 14:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('review', '0005_rename_imdb_rating_card_imdbrating_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='card',
            name='created',
        ),
        migrations.AlterField(
            model_name='card',
            name='modified',
            field=models.DateTimeField(blank=True),
        ),
    ]
