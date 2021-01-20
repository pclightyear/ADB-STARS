from django.shortcuts import render
from django.http import HttpResponse

from django.db import connection
from .Declination_limit_of_location import declination_limit
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
    '''
    username = 'a'#request.POST['username']
    name = 'a'#request.POST['name']
    email = 'a'#request.POST['email']
    affiliation = 'a'#request.POST['affiliation']
    title = 'a'#request.POST['title']
    country = 'a'#request.POST['country']
    password = 'a'#request.POST['password']
    '''
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
    return HttpResponse(result)

"""
    Log In
"""
def login_submit(request):
    username = request.POST['username']
    password = request.POST['password']
    with connection.cursor() as cursor:
        try:
            cursor.execute("SELECT uid FROM user_db WHERE username = \'" + username + "\' AND password = \'" + password + "\'")
            data = processData(cursor)
            data[0]['success'] = True
        except(IndexError):
            data = []
            data.append({'success': False})
    return HttpResponse(data)

"""
    Log Out
"""

"""
    Home
"""
def home(request):
    uid = str(request.GET.get('uid'))
    available_project_id = []
    results = []
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM equipment_db AS e JOIN own_db AS o ON e.eid = o.eid WHERE o.uid = " + uid)
        equipments = processData(cursor)

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
                    if project['pid'] in available_project_id:
                        continue
                    else:
                        available_project_id.append(project['pid'])
                        results.append(project)


    #print(data)
    return HttpResponse(results)

def home_project_info_target(request):
    pid = request.GET.get('pid')
    with connection.cursor() as cursor:
        cursor.execute("SELECT tid FROM observe_db WHERE pid = " + str(pid))
        tids = processData(cursor)
        result = []
        for i in range(len(tids)):
            tid = tids[i]['tid']
            cursor.execute("SELECT * FROM target_db WHERE tid = " + str(tid))
            result.append(processData(cursor)[0])
        cursor.execute("SELECT * FROM project_db WHERE pid = " + str(pid))
        result.append(processData(cursor)[0])
    return HttpResponse(result)

def home_project_info_target_submit(request):
    uid = request.POST['uid']
    pid = request.POST['pid']
    with connection.cursor() as cursor:
        try:
            cursor.execute(
                "INSERT INTO user_db(uid,pid)"
                + " VALUES(" + str(uid) + ",\'" + str(pid) + "\')")
            result = []
            result.append({'success' : True})
        except(IndexError):
            result = []
            result.append({'success' : False})
    return HttpResponse(result)

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
    uid = request.GET['uid']
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
    '''
    uid = 0
    p_title = "abc"
    p_project_type =  "abc"
    p_description = "abc"
    p_aperture_upper_limit = "100.2"
    p_aperture_lower_limit = "0.2"
    p_FoV_upper_limit = "0.2"
    p_FoV_lower_limit = "0.2"
    p_pixel_scale_upper_limit = "0.2"
    p_pixel_scale_lower_limit = "0.2"
    p_mount_type =  "ss"
    p_camera_type_colored_mono = "ss"
    p_camera_type_cooled_uncooled = "ss"
    p_Johnson_B = "y"
    p_Johnson_V = "y"
    p_Johnson_R = "y"
    p_SDSS_u = "y"
    p_SDSS_g = "y"
    p_SDSS_r = "y"
    p_SDSS_i = "y"
    p_SDSS_z = "y"
    targets =[{"name":"abc","longitude":100.2,"latitude":0.2}]
    '''
    #########################
    uid = str(request.POST['uid'])
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
    return HttpResponse(result)






"""
    Schedule
"""

"""
    Equipment
"""
def equipment(request):
    uid = request.GET.get('uid')
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM own_db WHERE uid = " + str(uid))
        data = processData(cursor)
    print(data[0])
    reponse = {"equipments": data}
    return HttpResponse(reponse)

def equipment_add_equipment_submit(request):
    '''
    uid = str(0)
    e_site = str("adc")
    e_longitude = str(0.1)
    e_latitude = str(0.1)
    e_altitude = str(0.1)
    e_time_zone = str("adc")
    e_daylight_saving = str("a")
    e_water_vapor = str(0.1)
    e_light_pollution = str(0.1)
    e_aperture = str(0.1)
    e_fov = str(0.1)
    e_pixel_scale = str(0.1)
    e_tracking_accuracy = str(0.1)
    e_limiting_magnitude = str(0.1)
    e_elevation_limit = str(0.1)
    e_mount_type = str("adc")
    e_camera_type_colored_mono = str("adc")
    e_camera_type_cooled_uncooled = str("adc")
    e_Johnson_B = str("a")
    e_Johnson_V = str("a")
    e_Johnson_R = str("a")
    e_SDSS_u = str("a")
    e_SDSS_g = str("a")
    e_SDSS_r = str("a")
    e_SDSS_i = str("a")
    e_SDSS_z = str("a")
    '''
    uid = str(request.POST['uid'])
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
    return HttpResponse(result)

"""
    Relation
"""