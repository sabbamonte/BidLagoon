from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User, auction_listings, watchlists, bids, inactive, comment
import tkinter
import base64
from PIL import Image, ImageTk
from io import StringIO, BytesIO
import requests


def index(request):
    # Define user and render message if not logged in
    user = User.objects.filter(username=request.user)
    if not user:
        message = "You have to log in/register to see listings"
        return render(request, "auctions/apology.html", {'message':message})

    # return all listings
    listings = auction_listings.objects.all()
    return render(request, "auctions/index.html", {'listings':listings})

@login_required()
def won(request):
    # Iterate through ianctives and find which ones the user won
    inactives = inactive.objects.filter(winner=request.user)
    return render(request, "auctions/won.html", {'inactives':inactives})

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    # Log user out
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

@login_required()
def new(request):
    if request.method == "GET":
        return render(request,"auctions/new.html")
    else:
        # create a new listing and save it
        listing = auction_listings()

        listing.seller = request.user
        listing.title = request.POST['title']
        if not listing.title:
            message = 'Please enter a valid title'
            return render(request, "auctions/apology.html", {'message':message})
        double_title = auction_listings.objects.filter(title=listing.title)
        if double_title:
            message = 'A listing with this title already exists'
            return render(request, "auctions/apology.html", {'message':message})
        listing.description = request.POST['description']
        if not listing.description:
            message = 'Please enter a description'
            return render(request, "auctions/apology.html", {'message':message})
        listing.category = request.POST['category']
        if not request.POST['category']:
            listing.category = None
        listing.photo = request.POST['photo']
        
        listing.price = request.POST['price']
        if not listing.price:
            message = 'Please enter a starting price'
            return render(request, "auctions/apology.html", {'message':message})

        listing.save()
        return HttpResponseRedirect(reverse("index"))

@login_required()
def listing(request, title):
    # return listing
    if request.method == "GET":
        listing = auction_listings.objects.filter(title=title)
        
        watchlist = watchlists.objects.filter(user=request.user)

        # get the highest bid
        all_bids = bids.objects.all()
        highest_bid = []
        for lists in listing:
            print(lists.price)
            for bid in all_bids:
                print(bid.bid)
                if lists.price == bid.bid:
                    highest_bid.append(bid)
        
        # get all comments for this listing
        comments = comment.objects.filter(title=title)

        # check if listing is in user's watchlist
        titles = []
        match = []
        titles[:]
        for watch in watchlist:
            titles.append(watch.title)
            for tit in titles:
                if tit in listing:
                    match = tit

        # toggle watchlist button
        listings = auction_listings.objects.get(title=title)
        user = request.user
        if user == listings.seller:
            found = "activate close button"
        else:
            found = None
        
        return render(request,"auctions/listing.html", {"listings":listing, "match":match, "comments":comments, "found":found, "highest_bid":highest_bid})

    # add listing to watchlist      
    if request.method == "POST" and 'add' in request.POST:
        listing = auction_listings.objects.get(title=title)
    
        watchlist = watchlists()              
        watchlist.user = request.user
        watchlist.title = listing  
        watchlist.save()

        return HttpResponseRedirect(reverse("watchlist"))
    
    # remove listing from watchlist
    if request.method == "POST" and 'remove' in request.POST:
        listing = auction_listings.objects.get(title=title)
        watchlist = watchlists.objects.get(title=listing, user=request.user)
        watchlist.delete()
        
        return HttpResponseRedirect(reverse("watchlist"))
    
    # bid on the listing and check if user is bidding on own listing
    if request.method == "POST" and 'bid' in request.POST:
        listing = auction_listings.objects.get(title=title)
        if listing.seller == request.user:
            return render(request, "auctions/apology.html", {'message':"You cannot bid on your own listing"})
        bidds = bids.objects.filter(title=listing)
        new_bid = request.POST['bid']
        if not new_bid:
            return render(request, "auctions/apology.html", {'message':'Enter a valid bid'})

        # check if bid is lower than current price
        price = listing.price
        amount = []
        for bid in bidds:
            amount.append(bid.bid)
        if amount == None:
            if new_bid < price:
                message = 'Bid too low'
                return render(request, "auctions/apology.html", {'message':message})
        if price >= int(new_bid):
            message = 'Bid too low'
            return render(request, "auctions/apology.html", {'message':message})

        else:
            new_price = price + (int(new_bid) - price)
            auction_listings.objects.filter(title=title).update(price=new_price)

            bid = bids()
            bid.bidder = request.user
            bid.bid = new_bid
            bid.price = listing
            bid.title = listing
            bid.save()
        listings = auction_listings.objects.all()
        return render(request,"auctions/index.html", {"listings":listings})

    # close the listing and declare winner, if applicable
    if request.method == "POST" and 'close' in request.POST:
        listing = auction_listings.objects.get(title=title)
        all_bids = bids.objects.filter(title=listing)
        winner = None
        w = None
        you = None
        
        find = []
        for bid in all_bids:
            find.append(bid.bid)
        
        highest = max(find) if find else 0
        if highest != 0:
            winner = bids.objects.get(title=listing, bid=highest)
            w = winner.bidder
            if w == request.user:
                you = "You are the winner!"
        
        closed = inactive()
        closed.title = listing.title
        closed.price = listing.price
        closed.winner = w
        closed.save()
        
        auction_listings.objects.get(title=title).delete()
        inactive_listing = inactive.objects.filter(title=title)
        return render(request,"auctions/closed.html", {"listings":inactive_listing, "winner":w, "you":you})

    # add a comment to listing
    if request.method == "POST" and 'comment' in request.POST:
        add_comment = request.POST['comment']
        listing = auction_listings.objects.get(title=title)

        comments = comment()
        comments.comment = add_comment
        comments.commenter = request.user
        comments.title = listing.title
        comments.save()

        return HttpResponseRedirect(reverse("index"))

@login_required()
def closed(request,title):
    # show the winner for the auction when closed
    if request.method == "GET":
        inactives = inactive.objects.filter(winner=request.user)
        you = "You are the winner!"
        return render(request,"auctions/closed.html", {"listings":inactives, "you":you})

@login_required()
def watchlist(request):
    # return watchlist for specific user
    if request.method == "GET":
        listing = watchlists.objects.filter(user=request.user)
        titles=[]
        for li in listing:
            titles.append(li.title)
        return render(request, "auctions/watchlist.html", {'watchlist':titles})

@login_required()
def category(request,title):
    # show all categories
    if request.method == "GET":
        listings = auction_listings.objects.filter(category=title)
        print(listings)
        return render(request, "auctions/category.html", {"listings":listings})














    
        
