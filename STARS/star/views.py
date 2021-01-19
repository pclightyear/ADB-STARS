from django.shortcuts import render
from django.http import HttpResponse

from django.db import connection
# Create your views here.


"""
    Utils
"""
def test_db(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM test")
        data = processData(cursor)

    print(data)

    return HttpResponse("test_db")
def processData(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row)) for row in cursor.fetchall()
    ]

"""
    Index
"""
def index(request):
    return HttpResponse("Home")

"""
    Profile
"""

def profile(request):
    return HttpResponse("get profile")

def profile_submit(request):
    return HttpResponse("update profile sucess")

"""
    Register
"""
def register_submit(request):
    return HttpResponse("register sucess")

"""
    Log In
"""
def login_submit(request):
    return HttpResponse("log in sucess")

"""
    Log Out
"""

"""
    Home
"""
def home(request):
    return HttpResponse("")

"""
    Project
"""

"""
    Schedule
"""

"""
    Equipment
"""

"""
    Relation
"""