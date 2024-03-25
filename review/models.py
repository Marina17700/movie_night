from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class Card(models.Model):
    id = models.CharField(max_length=20, primary_key=True)
    title = models.CharField(max_length=150)
    description = models.CharField(max_length=32, blank=True)
    image = models.URLField(blank=True)
    imdbRating = models.CharField(blank=True, default="N/A", max_length=8)
    imdbVotes = models.CharField(max_length=8, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField()

    def save(self, *args, **kwargs):
        if self.pk is None:
            self.modified = timezone.now()
        super(Card, self).save(*args, **kwargs)


class Item(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="watchlist")
    card = models.ForeignKey(
        Card, on_delete=models.CASCADE, related_name="watched")
    added = models.DateTimeField(auto_now_add=True)


class Review(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="user_reviews")
    rating = models.IntegerField()
    review = models.CharField(blank=True, max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    card = models.ForeignKey(
        Card, on_delete=models.CASCADE, related_name="card_reviews")
