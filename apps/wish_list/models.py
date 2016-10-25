from __future__ import unicode_literals
import re
from django.db import models
import bcrypt

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
NAME_REGEX = re.compile(r'^[a-zA-z]*$')

# Create your models here.
class UserManager(models.Manager):
    def login(self, email, password):
        encodedPassword = password.encode(encoding="utf-8", errors="strict") # encode the password or hashing it with bcrypt might fail
        if len(email) < 1:
            return (False, "Please enter an email address.")
        elif not EMAIL_REGEX.match(email):
            return (False, "Invalid email address entered.")
        elif not User.objects.filter(email = email):
            return (False, "That email is not registered.")
        elif User.objects.get(email = email).password != bcrypt.hashpw(encodedPassword, User.objects.get(email = email).password.encode(encoding="utf-8", errors="strict")): # use the encoded and hased password in the database as the salt argument for hashpw
            return (False, "Check password and try again.")
        else:
            loggedInUser = User.objects.get(email = email)
            return (True, loggedInUser)
    def register(self, **kwargs):
        errors = []
        success = True
        if len(kwargs["first_name"]) < 3 or len(kwargs["last_name"]) < 3:
            success = False
            errors.append("First and last name must be at least two characters long.")
        elif not NAME_REGEX.match(kwargs["first_name"]) or not NAME_REGEX.match(kwargs["last_name"]):
            success = False
            errors.append("First and last name must contain letters only.")
        if len(kwargs["email"]) < 1:
            success = False
            errors.append("Please enter an email address.")
        elif not EMAIL_REGEX.match(kwargs["email"]):
            success = False
            errors.append("Invalid email address entered.")
        elif User.objects.filter(email = kwargs["email"]):
            success = False
            errors.append("Email address already registered.")
        if len(kwargs["password"]) < 8:
            success = False
            errors.append("Password must be at least eight characters long.")
        elif kwargs["password"] != kwargs["vpassword"]:
            success = False
            errors.append("Passwords do not match.")
        if not success:
            return (False, errors)
        else:
            encodedPassword = kwargs["password"].encode(encoding="utf-8", errors="strict")
            addedUser = User.objects.create(first_name = kwargs["first_name"], last_name = kwargs["last_name"], email = kwargs["email"], password = bcrypt.hashpw(encodedPassword, bcrypt.gensalt()))
            return (True, addedUser)

class User(models.Model):
    first_name = models.CharField(max_length = 30)
    last_name = models.CharField(max_length = 30)
    email = models.CharField(max_length = 255)
    password = models.CharField(max_length = 50)
    objects = UserManager()
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)

class Item(models.Model):
    item = models.CharField(max_length = 30)
    user_id = models.ForeignKey(User)
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)

class Wish(models.Model):
    user_id = models.ForeignKey(User)
    item_id = models.ForeignKey(Item)
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)
