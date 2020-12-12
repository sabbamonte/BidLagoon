from django.contrib import admin

from .models import User, auction_listings, bids, comment, watchlists, inactive

# Register your models here.
admin.site.register(User)
admin.site.register(auction_listings)
admin.site.register(bids)
admin.site.register(comment)
admin.site.register(watchlists)
admin.site.register(inactive)
