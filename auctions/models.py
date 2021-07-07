from django.contrib.auth.models import AbstractUser
from django.db import models
from datetime import datetime

class User(AbstractUser):
    pass

class Listing(models.Model):
    title = models.CharField(max_length=64)
    image = models.CharField(max_length=128, blank=True)
    description = models.CharField(max_length=128)
    date = models.DateTimeField(default=datetime.now, blank=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings")
    wishers = models.ManyToManyField(User, blank=True, related_name="wishlist")
    is_active = models.BooleanField(default=True, blank=True)


class Bid(models.Model):
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bid_on")
    bid = models.IntegerField()
    item = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="on_bid")



