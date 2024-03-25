from .models import User, Card, Item, Review
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from django.shortcuts import render
import json
from django.utils import timezone
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.template.defaulttags import register
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, HttpResponseBadRequest


@register.filter
def get_value(dictionary, key):
    return dictionary.get(key)


def page(request, results):
    paginator = Paginator(results, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj


def buttons(request):
    cards = []
    watchlist = []

    if request.user.is_authenticated:
        user = request.user

        # Get reviewed movies
        cards = Review.objects.filter(user=user).values_list(
            'card', flat=True).distinct()
        # Get watchlist movies
        watchlist = user.watchlist.values_list(
            'card', flat=True).distinct()
    return cards, watchlist


def get_reviews(cards, user=None):
    reviews = {}

    # Get reviews for each card
    for card in cards:
        one = []
        if Review.objects.filter(user=user, card=card).exists() and user is not None:
            lists = [Review.objects.filter(user=user).get(card=card)]
        elif user is not None:
            lists = []
        else:
            lists = Review.objects.filter(
                card=card).order_by("-timestamp").all()

        for review in lists:
            reviewer = review.user.username
            rating = review.rating
            text = review.review
            date = review.timestamp
            one.append({'reviewer': reviewer, 'rating': {
                       '0': "*"*rating, "1": "*"*(5-rating)}, 'text': text, 'date': date})
        reviews[card] = one
    return reviews


def index(request):

    reviewed = Review.objects.values_list('card', flat=True).distinct().all()
    not_reviewed = Card.objects.exclude(id__in=reviewed).values_list(
        'id', flat=True).all()
    results = Card.objects.exclude(
        id__in=not_reviewed).order_by("-modified").all()

    reviews = get_reviews(results.values_list('id', flat=True))

    cards, watchlist = buttons(request)

    return render(request, "review/index.html", {
        "cards": cards,
        "watchlist": watchlist,
        "reviews": reviews,
        "username": None,
        "list_": False,
        'page_obj': page(request, results)
    })


@csrf_exempt
def search(request, username=None, list_=False, top=False):
    reviews = {}
    timestamps = []
    user = None

    # Create new session if none exists
    if "results" not in request.session:
        request.session["results"] = []

    results = request.session["results"]

    if username is not None:

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return HttpResponseBadRequest("Bad Request: user does not exist")
        if list_:
            results = Card.objects.filter(watched__user=user).order_by(
                "-watched__added").all()
        elif top:
            results = Card.objects.filter(card_reviews__user=user).order_by(
                "-card_reviews__rating", "-card_reviews__timestamp").all()
        else:
            results = Card.objects.filter(card_reviews__user=user).order_by(
                "-card_reviews__timestamp").all()

        cards = results.values_list("id", flat=True).distinct()

        # Get timestamps
        for card in cards:
            if list_:
                added_on = Item.objects.filter(user=user).get(card=card).added
                timestamps.append([card, added_on])

        reviews = get_reviews(cards, user)
        timestamps = dict(timestamps)

    cards, watchlist = buttons(request)

    if request.method == "POST":
        data = json.loads(request.body)

        # Check if results are empty
        if data.get("results") is not None:
            results = [i for i in data["results"] if i]
            results = [i for i in results if i["imdbRating"] != "N/A" or i["image"] !=
                       'https://imdb-api.com/images/original/nopicture.jpg']
        if results != [""]:
            request.session["results"] = results

        return JsonResponse({"message": "Successful."}, status=201)
    else:
        return render(request, "review/search.html", {
            "cards": cards,
            "watchlist": watchlist,
            "reviews": reviews,
            "username": username,
            "timestamps": timestamps,
            "list_": list_,
            'page_obj': page(request, results),
            "top": top
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
            return render(request, "review/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "review/login.html")


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
            return render(request, "review/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "review/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "review/register.html")


@csrf_exempt
@login_required
def rating(request):
    # Rating a movie must be via POST
    if request.method != "POST":
        return JsonResponse({"message": "POST request required."}, status=400)

    # Get contents of post
    data = json.loads(request.body)
    card = get_card(data)
    rating = data.get("rating")
    text = data.get("review", "")

    # Get the user
    try:
        user = User.objects.get(pk=request.user.id)
    except User.DoesNotExist:
        return JsonResponse({
            "message": f"User with id {request.user.id} does not exist."
        }, status=400)

    try:
        # Get the review
        review = Review.objects.get(card=card, user=user)
        review.rating = rating
        review.review = text
    except Review.DoesNotExist:
        # Create a new review
        review = Review(user=user, card=card, rating=rating, review=text)
        card.modified = timezone.now()
        card.save()

    review.save()

    return JsonResponse({"message": "Successful."}, status=201)


@csrf_exempt
@login_required
def add(request):
    # Add a movie must be via POST
    if request.method != "POST":
        return JsonResponse({"message": "POST request required."}, status=400)

    # Get contents of post
    data = json.loads(request.body)
    card = get_card(data)

    # Get the user
    try:
        user = User.objects.get(pk=request.user.id)
    except User.DoesNotExist:
        return JsonResponse({"message": f"User with id {request.user.id} does not exist."}, status=400)

    # Add card to user's watchlist
    item = Item(user=user, card=card)
    item.save()
    return JsonResponse({"message": "Successful."}, status=201)


@csrf_exempt
@login_required
def remove(request):

    # Remove a movie must be via POST
    if request.method != "POST":
        return JsonResponse({"message": "POST request required."}, status=400)

    # Get contents of post
    data = json.loads(request.body)

    # Get id of post
    imdb_id = data.get("imdb_id")

    # Get the post
    try:
        card = Card.objects.get(pk=imdb_id)
    except Card.DoesNotExist:
        return JsonResponse({
            "message": f"Movie with id {imdb_id} does not exist."
        }, status=400)

    # Get the user
    try:
        user = User.objects.get(pk=request.user.id)
    except User.DoesNotExist:
        return JsonResponse({
            "message": f"User with id {request.user.id} does not exist."
        }, status=400)

    # Remove card from user's watchlist
    try:
        item = Item.objects.filter(user=user.id).get(card=card.id)
    except Item.DoesNotExist:
        return JsonResponse({
            "message": f"Movie with id {imdb_id} is not in your watchlist."
        }, status=400)

    # Delete item
    item.delete()
    return JsonResponse({"message": "Successful."}, status=201)


def get_card(data):

    # Get id of post
    imdb_id = data.get("imdb_id")

    # Get the post
    try:
        card = Card.objects.get(pk=imdb_id)
    except Card.DoesNotExist:
        title = data.get("title")
        description = data.get("description")
        image = data.get(
            "image", "https://imdb-api.com/images/original/nopicture.jpg")
        imdbRating = data.get("imdbRating")
        imdbVotes = data.get("imdbVotes")
        # Create a new card
        card = Card(id=imdb_id, title=title, description=description,
                    image=image, imdbRating=imdbRating, imdbVotes=imdbVotes,
                    modified=timezone.now())
        card.save()

    return card


def watchlist(request, username):
    return search(request, username, list_=True)


def profile(request, username):
    return search(request, username)


def profile_top(request, username):
    return search(request, username, top=True)
