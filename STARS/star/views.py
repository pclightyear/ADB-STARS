from django.shortcuts import render
from django.http import HttpResponse,HttpResponseRedirect

from django.db import connection
from .Declination_limit_of_location import declination_limit
from django.utils.decorators import method_decorator
from django.contrib import auth

from neo4j import GraphDatabase
# Create your views here.

"""
    Utils
"""
def _create_and_return_greeting(tx, message):
        result = tx.run("CREATE (a:Greeting) "
                        "SET a.message = $message "
                        "RETURN a.message + ', from node ' + id(a)", message=message)
        return result.single()[0]

def neo4jdb_test(request):
    driver = GraphDatabase.driver('bolt://localhost:7687', auth=("neo4j", "1234"))
    with driver.session() as session:
        greeting = session.write_transaction(_create_and_return_greeting,"hello, world")
        print(greeting)
    driver.close()
    return HttpResponse(greeting)


def getuid(request):
    try:
        return str(request.session['uid'])
    except(KeyError):
        return str(-1)

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
    uid = getuid(request)
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
    uid = getuid(request)
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
        sucess = (cursor.rowcount == 1)
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
def register(request):
    return render(request, 'register.html')

def register_submit(request):
    username = request.POST['username']
    name = request.POST['name']
    email = request.POST['email']
    affiliation = request.POST['affiliation']
    title = request.POST['title']
    country = request.POST['country']
    password = request.POST['password']
    
    with connection.cursor() as cursor:
        try:
            cursor.execute("SELECT max(uid) FROM user_db")
            data = processData(cursor)
            uid = int(data[0]['max']) + 1
            cursor.execute(
                "INSERT INTO user_db(uid,username,name,email,affiliation,title,country,password)"
                + " VALUES(" + str(uid) + ",\'" + username + "\',\'" + name + "\',\'" + email + "\',\'"
                + affiliation + "\',\'" + title + "\',\'" + country + "\',\'" + password +"\')")
            result = []
            result.append({'success' : True})
        except(IndexError):
            result = []
            result.append({'success' : False})
    return HttpResponseRedirect("../login")
"""
    Log In
"""
def login(request):
    return render(request, 'login.html')
    
def login_submit(request):
    print('login submit')
    username = request.POST['username']
    password = request.POST['password']
    with connection.cursor() as cursor:
        try:
            cursor.execute("SELECT * FROM user_db WHERE username = \'" + username + "\' AND password = \'" + password + "\'")
            data = processData(cursor)
            data[0]['success'] = True
            request.session['uid'] = data[0]['uid']
            request.session['username'] = data[0]['username']
        except(IndexError):
            data = []
            data.append({'success': False})
    return HttpResponseRedirect("../home")

"""
    Log Out
"""
def logout(request):
    try:
        del request.session['uid']
        del request.session['username']
    except(KeyError):
        pass
    return HttpResponseRedirect("../login")
"""
    Home
"""
def home(request):
    print('home: ')
    uid = getuid(request)
    print('uid: ' + uid)
    # uid = str(request.GET.get('uid'))
    available_project_id = []
    available_project_title = []
    available_project_project_type = []
    available_project_description = []
    results = []
    participating_pid = []
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM equipment_db AS e JOIN own_db AS o ON e.eid = o.eid WHERE o.uid = " + uid)
        equipments = processData(cursor)
        cursor.execute("SELECT pid FROM participate_db WHERE uid = " + uid)
        participates = processData(cursor)
        if not participates:
            participating_pid = []
        else:
            for participate in participates:
                participating_pid.append(participate['pid'])
        for equipment in equipments:
            longitude = equipment['longitude']
            latitude = equipment['latitude']
            altitude = equipment['altitude']
            elevation_limit = equipment['elevation_limit']
            decline_limitation = declination_limit(longitude,latitude,altitude,elevation_limit)
            if decline_limitation < 0:
                cursor.execute("SELECT * FROM target_db WHERE latitude < 90  AND latitude >" + str(decline_limitation))
            else:
                cursor.execute("SELECT * FROM target_db WHERE latitude > -90  AND latitude <" + str(decline_limitation))
            targets = processData(cursor)
            for target in targets:
                tid = target['tid']
                cursor.execute("SELECT * FROM project_db AS p JOIN observe_db AS o ON o.pid = p.pid WHERE o.tid = " + str(tid) + " AND " +
                    str(equipment['aperture']) + " < p.aperture_upper_limit AND " + str(equipment['aperture']) + " > p.aperture_lower_limit AND " +
                    str(equipment['fov']) + " < p.fov_upper_limit AND " + str(equipment['fov']) + " > p.fov_lower_limit AND " +
                    str(equipment['pixel_scale']) + " < p.pixel_scale_upper_limit AND " + str(equipment['pixel_scale']) + " > p.pixel_scale_lower_limit AND \'" +
                    str(equipment['mount_type']) + "\' = p.mount_type AND \'" + str(equipment['camera_type_colored_mono']) + "\' = p.camera_type_colored_mono AND \'" +
                    str(equipment['camera_type_cooled_uncooled']) + "\' = p.camera_type_cooled_uncooled"
                )
                projects = processData(cursor)
                for project in projects:
                    if project['pid'] in available_project_id or project['pid'] in participating_pid:
                        continue
                    else:
                        available_project_id.append(project['pid'])
                        results.append(project)


    #print(data)
    return render(request,'home.html',{'projects':results})

def home_project_info_target(request):
    pid = request.GET.get('pid')
    with connection.cursor() as cursor:
        cursor.execute("SELECT tid FROM observe_db WHERE pid = " + str(pid))
        tids = processData(cursor)
        targets = []
        for i in range(len(tids)):
            tid = tids[i]['tid']
            cursor.execute("SELECT * FROM target_db WHERE tid = " + str(tid))
            targets.append(processData(cursor)[0])
        cursor.execute("SELECT * FROM project_db WHERE pid = " + str(pid))
        projectInfo = processData(cursor)
    return render(request,'project-info-target.html',{'projectInfo':projectInfo,'targets':targets})

def home_project_info_target_submit(request):
    uid = getuid(request)
    pid = request.POST['pid']
    with connection.cursor() as cursor:
        try:
            cursor.execute(
                "INSERT INTO participate_db(uid,pid)"
                + " VALUES(" + str(uid) + ",\'" + str(pid) + "\')")
            result = []
            result.append({'success' : True})
        except(IndexError):
            result = []
            result.append({'success' : False})
    return HttpResponseRedirect("../home")

"""
    Project
"""
def join_project(request):
    uid = getuid(request)
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
    pid = request.GET['pid']
    sql_q = \
    """
        SELECT *
        FROM project_db
        WHERE pid = {pid}
    """.format(pid=pid)

    with connection.cursor() as cursor:
        cursor.execute(sql_q)
        project = processData(cursor)

    print(project)

    sql_t = \
    """
        SELECT t.tid, t.Name as targetName, t.longitude, t.latitude
        FROM target_db as t
        INNER JOIN (
            SELECT tid
            FROM observe_db 
            WHERE pid = {pid} 
        ) as o
        ON t.tid = o.tid
    """.format(pid=pid)

    with connection.cursor() as cursor:
        cursor.execute(sql_t)
        targets = processData(cursor)

    print(targets)
    
    res = {
        "project": project[0],
        "targets": targets
    }
    
    return HttpResponse("get join project info: {}".format(res))

def manage_project(request):
    uid = getuid(request)
    sql = \
    """
        SELECT project.pid, project.title, project.project_type, project.description, COALESCE(num_participants, 0) as num_participants
        FROM project_db as project
        INNER JOIN (
            SELECT pid
            FROM manage_db 
            WHERE uid = {uid}
        ) as m
        ON project.pid = m.pid
        LEFT JOIN (
            SELECT participate.pid, COUNT(*) as num_participants
            FROM participate_db as participate
            GROUP BY participate.pid
        ) as num_participate
        ON project.pid = num_participate.pid
    """.format(uid=uid)

    with connection.cursor() as cursor:
        cursor.execute(sql)
        res = processData(cursor)

    print(res)

    return HttpResponse("get manage projects: {}".format(res))

def project_create_project_submit(request):
    uid = getuid(request)
    project = request.POST['project']
    p_title = str(project['title'])
    p_project_type =  str(project['project_type'])
    p_description = str(project['description'])
    p_aperture_upper_limit = str(project['aperture_upper_limit'])
    p_aperture_lower_limit = str(project['aperture_lower_limit'])
    p_FoV_upper_limit = str(project['FoV_upper_limit'])
    p_FoV_lower_limit = str(project['FoV_lower_limit'])
    p_pixel_scale_upper_limit = str(project['pixel_scale_upper_limit'])
    p_pixel_scale_lower_limit = str(project['pixel_scale_lower_limit'])
    p_mount_type = str(project['mount_type'])
    p_camera_type_colored_mono = str(project['camera_type_(colored,mono)'])
    p_camera_type_cooled_uncooled = str(project['camera_type(cooled,uncooled)'])
    p_Johnson_B = str(project['Johnson_B'])
    p_Johnson_V = str(project['Johnson_V'])
    p_Johnson_R = str(project['Johnson_R'])
    p_SDSS_u = str(project['SDSS_u'])
    p_SDSS_g = str(project['SDSS_g'])
    p_SDSS_r = str(project['SDSS_r'])
    p_SDSS_i = str(project['SDSS_i'])
    p_SDSS_z = str(project['SDSS_z'])

    targets = request.POST['targets']
    

    with connection.cursor() as cursor:
        try:
            cursor.execute("SELECT max(pid) FROM project_db")
            data = processData(cursor)
            pid = int(data[0]['max']) + 1
            cursor.execute(
                "INSERT INTO project_db(pid,title,project_type,description,aperture_upper_limit,"+
                "aperture_lower_limit,fov_upper_limit,fov_lower_limit,pixel_scale_upper_limit,pixel_scale_lower_limit,"+
                "mount_type,camera_type_colored_mono,camera_type_cooled_uncooled,johnson_b,johnson_v,johnson_r,"+
                "sdss_u,sdss_g,sdss_r,sdss_i,sdss_z)"
                + " VALUES(" + str(pid) + ",\'" + p_title + "\',\'" + p_project_type + "\',\'" + p_description + "\',"
                + p_aperture_upper_limit + "," + p_aperture_lower_limit + "," + p_FoV_upper_limit + "," + p_FoV_lower_limit + "," + p_pixel_scale_upper_limit + "," + p_pixel_scale_lower_limit + ",\'"
                + p_mount_type + "\',\'" + p_camera_type_colored_mono + "\',\'" + p_camera_type_cooled_uncooled + "\',\'" 
                + p_Johnson_B + "\',\'" + p_Johnson_V + "\',\'" + p_Johnson_R + "\',\'" + p_SDSS_u + "\',\'"
                + p_SDSS_g + "\',\'" + p_SDSS_r + "\',\'" + p_SDSS_i + "\',\'" + p_SDSS_z + "\')")
            cursor.execute(
                "INSERT INTO manage_db(uid,pid) VALUES(" + str(uid) + "," + str(pid) + ")"
            )

            for idx in range(len(targets)):
                target = targets[idx]
                t_name = str(target['name'])
                t_longitude = str(target['longitude'])
                t_latitude = str(target['latitude'])
                cursor.execute("SELECT max(tid) FROM target_db")
                data = processData(cursor)
                tid = int(data[0]['max']) + 1
                cursor.execute(
                    "INSERT INTO target_db(tid,name,longitude,latitude) VALUES(" + 
                    str(tid) + ",\'" + t_name + "\'," + str(t_longitude) + "," + str(t_latitude) + ")"
                )
                cursor.execute(
                    "INSERT INTO observe_db(pid,tid,johnson_b,johnson_v,johnson_r,"+
                    "sdss_u,sdss_g,sdss_r,sdss_i,sdss_z) VALUES(" + str(pid) + "," + str(tid) + ",\'"
                    + p_Johnson_B + "\',\'" + p_Johnson_V + "\',\'" + p_Johnson_R + "\',\'" + p_SDSS_u + "\',\'"
                    + p_SDSS_g + "\',\'" + p_SDSS_r + "\',\'" + p_SDSS_i + "\',\'" + p_SDSS_z + "\')"
                )
            result = []
            result.append({'success' : True})
        except(IndexError):
            result = []
            result.append({'success' : False})
    return HttpResponseRedirect("../manage-project.html")






"""
    Schedule
"""
def schedule(request):
    uid = getuid(request)
    sql_p = \
    """
        SELECT p.pid, p.title
        FROM project_db as p
        INNER JOIN (
            SELECT pid
            FROM participate_db 
            WHERE uid = {uid} 
        ) as j
        ON p.pid = j.pid
    """.format(uid=uid)

    with connection.cursor() as cursor:
        cursor.execute(sql_p)
        projects = processData(cursor)

    print(projects)

    sql_e = \
    """
        SELECT eid, site
        FROM own_db
        WHERE uid = {uid} 
    """.format(uid=uid)

    with connection.cursor() as cursor:
        cursor.execute(sql_e)
        equipments = processData(cursor)

    print(equipments)
    
    res = {
        "projects": projects,
        "equipments": equipments
    }
    
    return HttpResponse("get schedule choose form: {}".format(res))
"""
    Equipment
"""
def equipment(request):
    uid = getuid(request)
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM own_db WHERE uid = " + str(uid))
        data = processData(cursor)
    return HttpResponse(request,"equipment.html",{"equipments":data})

def equipment_add_equipment_submit(request):
    uid = getuid(request)
    equipment = request.POST['equipment']
    e_site = str(equipment['site'])
    e_longitude = str(equipment['longitude'])
    e_latitude = str(equipment['latitude'])
    e_altitude = str(equipment['altitude'])
    e_time_zone = str(equipment['time_zone'])
    e_daylight_saving = str(equipment['daylight_saving'])
    e_water_vapor = str(equipment['water_vapor'])
    e_light_pollution = str(equipment['light_pollution'])
    e_aperture = str(equipment['aperture'])
    e_fov = str(equipment['FoV'])
    e_pixel_scale = str(equipment['pixel_scale'])
    e_tracking_accuracy = str(equipment['tracking_accuracy'])
    e_limiting_magnitude = str(equipment['limiting_magnitude'])
    e_elevation_limit = str(equipment['elevation_limit'])
    e_mount_type = str(equipment['mount_type'])
    e_camera_type_colored_mono = str(equipment['camera_type_(colored,mono)'])
    e_camera_type_cooled_uncooled = str(equipment['camera_type(cooled,uncooled)'])
    e_Johnson_B = str(equipment['Johnson_B'])
    e_Johnson_V = str(equipment['Johnson_V'])
    e_Johnson_R = str(equipment['Johnson_R'])
    e_SDSS_u = str(equipment['SDSS_u'])
    e_SDSS_g = str(equipment['SDSS_g'])
    e_SDSS_r = str(equipment['SDSS_r'])
    e_SDSS_i = str(equipment['SDSS_i'])
    e_SDSS_z = str(equipment['SDSS_z'])
    with connection.cursor() as cursor:
        try:
            cursor.execute("SELECT max(eid) FROM equipment_db")
            data = processData(cursor)
            eid = str(int(data[0]['max']) + 1)
            cursor.execute(
                "INSERT INTO equipment_db(eid,aperture,fov,pixel_scale,tracking_accuracy,limiting_magnitude,elevation_limit,mount_type," +
                "camera_type_colored_mono,camera_type_cooled_uncooled,johnson_b,johnson_v,johnson_r,sdss_u,sdss_g,sdss_r,sdss_i,sdss_z)"
                + " VALUES(" + eid + "," + e_aperture + "," + e_fov + "," + e_pixel_scale + "," + e_tracking_accuracy + "," + e_limiting_magnitude + ","
                + e_elevation_limit + ",\'" + e_mount_type + "\',\'" + e_camera_type_colored_mono + "\',\'" + e_camera_type_cooled_uncooled + "\',\'"
                + e_Johnson_B + "\',\'" + e_Johnson_V + "\',\'" + e_Johnson_R + "\',\'" + e_SDSS_u + "\',\'"
                + e_SDSS_g + "\',\'" + e_SDSS_r + "\',\'" + e_SDSS_i + "\',\'" + e_SDSS_z + "\')")
            cursor.execute(
                "INSERT INTO own_db(uid,eid,site,longitude,latitude,altitude,time_zone,daylight_saving,water_vapor,light_pollution) " +
                "VALUES(" + uid + "," + eid + ",\'" + e_site + "\'," + e_longitude + "," + e_latitude + "," + e_altitude + ",\'" + e_time_zone + "\',\'" + e_daylight_saving + "\',"
                + e_water_vapor + "," + e_light_pollution + ")")
            result = []
            result.append({'success' : True})
        except(IndexError):
            result = []
            result.append({'success' : False})
    return HttpResponseRedirect("../equipment.html")

"""
    Relation
"""