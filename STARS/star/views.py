from django.shortcuts import render
from django.http import HttpResponse

from django.db import connection
from django.utils.decorators import method_decorator
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
    uid = request.GET['uid']
    sql = \
    """
        SELECT * 
        FROM user_db 
        WHERE uid = {uid} 
    """.format(uid=uid)

    with connection.cursor() as cursor:
        cursor.execute(sql)
        res = processData(cursor)

    print(res)

    return HttpResponse("get profile: {}".format(res))

def profile_submit(request):
    # @method_decorator(csrf_exempt, name='dispatch')
    uid = request.POST['uid']
    username = request.POST['username']
    name = request.POST['name']
    email = request.POST['email']
    affiliation = request.POST['affiliation']
    title = request.POST['title']
    country = request.POST['country']

    sql = \
    """
        UPDATE user_db
        SET username = '{username}', name = '{name}', email = '{email}', affiliation = '{affiliation}', title = '{title}', country = '{country}'
        WHERE uid = {uid}
    """.format(
        username=username, 
        name=name, 
        email=email, 
        affiliation=affiliation, 
        title=title, 
        country=country, 
        uid=uid
    )

    with connection.cursor() as cursor:
        cursor.execute(sql)
        sucess = cursor.rowcount is 1
        res = {
            "sucess": sucess
        }
    
    print(res)

    if sucess:
        return HttpResponse("update profile sucess: {}".format(res))
    else:
        return HttpResponse("update profile fail: {}".format(res))
    

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
def join_project(request):
    uid = request.GET['uid']
    sql = \
    """
        SELECT p.pid, p.title, p.project_type, p.description
        FROM project_db as p
        INNER JOIN (
            SELECT pid
            FROM participate_db 
            WHERE uid = {uid} 
        ) as j
        ON p.pid = j.pid
    """.format(uid=uid)

    with connection.cursor() as cursor:
        cursor.execute(sql)
        res = processData(cursor)

    print(res)

    return HttpResponse("get join projects: {}".format(res))

def join_project_info(request):
    # pid = request.GET['pid']
    # sql = \
    # """
    #     SELECT *
    #     FROM project_db
    #     WHERE pid = {pid}
    # """.format(pid=pid)

    # with connection.cursor() as cursor:
    #     cursor.execute(sql)
    #     res = processData(cursor)

    # print(res)

    # return HttpResponse("get join project info: {}".format(res))

"""
    Schedule
"""

"""
    Equipment
"""

"""
    Relation
"""