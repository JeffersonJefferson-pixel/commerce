from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from operator import attrgetter


from .models import User, Listing, Bid


def index(request):
    
    return render(request, "auctions/index.html", {
        "listings": Listing.objects.filter(is_active=True)
    })


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

def wishlist(request):
    wishlist = request.user.wishlist
    if request.method=="POST":
        listing_id = request.POST["listing_id"]
        listing = Listing.objects.get(pk=listing_id)

        if 'add' in request.POST:
            wishlist.add(listing)
        elif 'remove' in request.POST:
            wishlist.remove(listing)

        return render(request, "auctions/wishlist.html", {
            "wishlist": wishlist.all()
        })

    else:
        return render(request, "auctions/wishlist.html", {
        "wishlist": wishlist.all()
    })

def newListing(request):
    if request.method == "POST":
        
        title = request.POST["title"]
        image = request.POST["image"]
        description = request.POST["description"]
        starting_bid = request.POST["starting_bid"]

        listing = Listing(title=title, image=image, description=description, creator=request.user)
        listing.save()
        bid = Bid(bidder=request.user, bid=starting_bid, item=listing)
        bid.save()

        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/newListing.html")

def listings(request, listing_id):
    user = request.user
    listing = Listing.objects.get(id=listing_id)
    if user.is_authenticated:
        is_in_wishlist = listing in user.wishlist.all()
        is_in_listings = listing in user.listings.all()
    message = ""
    bids = listing.on_bid.all()
    num_bid = len(bids)
    highest_bidder = bids.last().bidder
    highest_bid = bids.last().bid
    starting_bid = bids.first().bid
    is_highest_bidder = user == highest_bidder

    if request.method == "POST":
        
       
        if 'place' in request.POST:
            bid =  int(request.POST["bid"])

            if bid >= starting_bid and (num_bid==1 or bid > highest_bid) :
                message = "Successful"
                new_bid = Bid(bidder=user, bid=bid, item=listing)
                new_bid.save()
                return render(request, "auctions/listing.html", {
                    "listing": listing,
                    "is_in_wishlist": is_in_wishlist,
                    "is_in_listings": is_in_listings,
                    "num_bid": num_bid,
                    "bid": bid,
                    "is_highest_bidder": True,
                    "message": message
                })
            else:
                message = "Unsucessful"
                return render(request, "auctions/listing.html", {
                    "listing": listing,
                    "is_in_wishlist": is_in_wishlist,
                    "is_in_listings": is_in_listings,
                    "num_bid": num_bid,
                    "bid": highest_bid,
                    "is_highest_bidder": is_highest_bidder,
                    "message": message
                })

        elif 'close' in request.POST:
            listing.is_active = False
            listing.save()
            return HttpResponseRedirect(reverse("index"))

    else: 
        if user.is_authenticated:
            message = "You won" if user == highest_bidder and not listing.is_active else ""

        return render(request, "auctions/listing.html", {
            "listing": listing,
            "is_in_wishlist": is_in_wishlist,
            "is_in_listings": is_in_listings,
            "num_bid": num_bid,
            "bid": highest_bid,
            "is_highest_bidder": is_highest_bidder,
            "message": message 

        })
