# Generated by Django 4.0.2 on 2022-06-02 14:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('review', '0004_remove_card_last_review_card_created_card_modified'),
    ]

    operations = [
        migrations.RenameField(
            model_name='card',
            old_name='imdb_rating',
            new_name='imdbRating',
        ),
        migrations.RenameField(
            model_name='card',
            old_name='votes',
            new_name='imdbVotes',
        ),
    ]
