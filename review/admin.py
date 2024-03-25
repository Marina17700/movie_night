from django.contrib import admin

from .models import User, Card, Item, Review


admin.site.register(User)
admin.site.register(Card)
admin.site.register(Item)
admin.site.register(Review)
