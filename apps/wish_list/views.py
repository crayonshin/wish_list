from django.shortcuts import render, redirect
from .models import User, Item, Wish
from django.contrib import messages

# Create your views here.
def index(request):
    if "id" in request.session:
        return redirect("/dashboard")
    return render(request, "wish_list/index.html")

def validate(request):
    if request.method != "POST":
        return redirect("/")
    if request.POST["action"] == "login":
        result = User.objects.login(request.POST["email"], request.POST["password"])
        if not result[0]:
            messages.add_message(request, messages.ERROR, result[1]) # this has a default message tag of "error". Access tags with "messages.tags". Login has a max of 1 error message per attempt so I don't iterate like I do with registration
            return redirect("/")
        request.session["id"] = result[1].id
        request.session["first_name"] = result[1].first_name
        return redirect("/dashboard")
    if request.POST["action"] == "register":
        kwargs = {"first_name": request.POST["first_name"], "last_name": request.POST["last_name"], "email": request.POST["email"], "password": request.POST["password"], "vpassword": request.POST["vpassword"]}
        result = User.objects.register(**kwargs)
        if not result[0]:
            errors = result[1]
            for error in errors:
                messages.add_message(request, messages.ERROR, error) # loop though errors list returned and add each error to messages
            return redirect("/")
        request.session["id"] = result[1].id
        request.session["first_name"] = result[1].first_name
        return redirect("/dashboard")

def dashboard(request):
    if "id" not in request.session:
        return redirect("/")
    wishes = Wish.objects.all().filter(user_id = request.session["id"])
    allWishes = Wish.objects.all().exclude(user_id = request.session["id"])
    context = {"wishes": wishes, "allWishes": allWishes}
    return render(request, "wish_list/dashboard.html", context)

def create(request):
    if "id" not in request.session:
        return redirect("/")
    return render(request, "wish_list/create.html")

def additem(request):
    if request.method != "POST":
        return redirect("/dashboard")
    item = request.POST["item"]
    if len(item) < 4:
        messages.add_message(request, messages.ERROR, "Item must contain at least four characters.")
        return redirect("/create")
    checkItem = Item.objects.filter(item__icontains = request.POST["item"]) # perform CASE INSENSITIVE search for the item to see if it's already in the Item model
    if not checkItem: # if that item doesn't exist, create it and put it on creator's wish list
        newItem = Item.objects.create(item = request.POST["item"], user_id = User.objects.get(id = request.session["id"])) # item is new here and not foreign key so use value entered, user exists and is foreign key so use the user object
        Wish.objects.create(item_id = newItem, user_id = User.objects.get(id = request.session["id"])) # now have to plug both of these existing items into the Wish foreign key fields item_id and user_id
        return redirect("/dashboard")
    if Wish.objects.filter(item_id = checkItem, user_id = request.session["id"]): # here I can just put in the checkItem object and django will filter any objects in checkItem queryset whose id match Wish primary key field item_id since it knows the relationship (will only be ONE object since no dupe items or wishes get created). Seems filter can use object OR value but create must be object for foreign key fields.
        messages.add_message(request, messages.ERROR, "Item already on your wish list.")
        return redirect("/create")
    Wish.objects.create(item_id = checkItem[0], user_id = User.objects.get(id = request.session["id"])) # item exists and is not in user's wish list so have to pluck actual item object from checkItem queryset with [0] to use in new wish record. Again, this queryset would only be empty or have ONLY one object.
    return redirect("/dashboard")

def wishes(request, id):
    if "id" not in request.session:
        return redirect("/")
    context = {"wishes": Wish.objects.all().filter(item_id = id)}
    return render(request, "wish_list/wishes.html", context)

def logout(request):
    if "id" not in request.session:
        return redirect("/")
    del request.session["id"]
    del request.session["first_name"]
    return redirect("/")

def removeitem(request, id):
    if "id" not in request.session:
        return redirect("/") # no need to check URL like "deleteitem" since this will only remove from logged in user's list based on session anyway
    Wish.objects.filter(user_id = request.session["id"], item_id = id).delete() # the filter part should be a queryset on ONLY one but just in case a dupe wish got in there, I don't specify [0]
    return redirect("/dashboard")

def deleteitem(request, id):
    if "id" not in request.session or not Item.objects.filter(id = id) or Item.objects.filter(id = id)[0].user_id.id != request.session["id"]: # if somebody crafted URL to delete an item they didn't create or delete and item id that doesn't exist, it redirects to dashboard
        return redirect("/")
    Item.objects.filter(id = id).delete() # again, items should not be repeated so only deleting one thing here
    return redirect("/dashboard")

def addfromanother(request, id):
    if "id" not in request.session or not Item.objects.filter(id = id): # in case logged in user tries to craft URL to add an item that does not exist
        return redirect("/")
    item = Item.objects.filter(id = id)[0] # if above conditional failed, I should have a queryset with one item so I reference it with [0] to access the one object's table columns
    if Wish.objects.filter(item_id = id, user_id = request.session["id"]): # here I can just use the IDs to query the existing objects
        messages.add_message(request, messages.ERROR, "Item already on your wish list.")
    else:
        Wish.objects.create(item_id = item, user_id = User.objects.get(id = request.session["id"])) # when creating however, have to use the existing item and user objects in the foreign key fields, values in other fields (if any)
    return redirect("/dashboard")
