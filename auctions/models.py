from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class auction_listings(models.Model):
    objects = models.Manager()
    title = models.CharField(max_length=64)
    category = models.CharField(max_length=64, null=True, default=None)
    description = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=19, decimal_places=2, null=True)
    photo = models.URLField(blank=True, default=None)
    seller = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f"Listing: {self.title} {self.photo} {self.description} Price: {self.price}"

class bids(models.Model):
    objects = models.Manager()
    title = models.ForeignKey(auction_listings, on_delete=models.CASCADE, null=True, related_name='current_title')
    price = models.ForeignKey(auction_listings, on_delete=models.CASCADE, related_name='current_bid')
    bid = models.DecimalField(max_digits=19, decimal_places=2)
    bidder = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.title}: {self.price} to {self.bidder}"

class comment(models.Model):
    objects = models.Manager()
    comment = models.CharField(max_length=200)
    commenter = models.ForeignKey(User, on_delete=models.CASCADE)
    title = title = models.CharField(max_length=64, default=None)

    def __str__(self):
        return f"{self.title}: {self.comment} to {self.commenter}"

class watchlists(models.Model):
    objects = models.Manager()
    title = models.ForeignKey(auction_listings, on_delete=models.CASCADE, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f"{self.user}: {self.title}"

class inactive(models.Model):
    objects = models.Manager()
    title = models.CharField(max_length=64, default=None)
    price = models.DecimalField(max_digits=19, decimal_places=2, null=True)
    winner = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f"Listing: {self.title} Price: {self.price}"






