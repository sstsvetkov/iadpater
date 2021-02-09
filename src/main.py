from aiohttp import web
import asyncpg
from ldap3 import Server, Connection, ALL, NTLM
import requests
from requests_ntlm import HttpNtlmAuth
import re
import json
import base64
import os

users = []


def laps(server, user, password, computer_name):
    server = Server(server, get_info=ALL)
    conn = Connection(server=server, user=user, password=password, authentication=NTLM)
    conn.bind()
    conn.search('dc=Dixy,dc=local', f'(&(objectclass=computer)(name={computer_name}))', attributes=['ms-Mcs-AdmPwd'])
    if conn.entries:
        return str(conn.entries[0]['ms-Mcs-AdmPwd'])
    else:
        return None


async def handle_laps(request):
    text = await request.text()
    try:
        body = json.loads(text or '{}')
    except json.JSONDecodeError:
        return web.Response(status=400)
    server = body.get('server', None)
    user = body.get('user', None)
    password = body.get('password', None)
    computer_name = body.get('computerName', None)
    if server and user and password and computer_name is not None:
        text = laps(server=server, user=user, password=password, computer_name=computer_name) or '0'
    else:
        text = '0'
    return web.Response(text=text)


def bio(user, password, computer_name):
    response = requests.get(
        f"http://10.0.17.148/ReportServer/Pages/ReportViewer.aspx?%2fBiolink%2fBioTime+Manager+pwd&rs:Command=Value&Login={computer_name}",
        auth=HttpNtlmAuth(username=user, password=password))
    result = re.findall("<div style=\"width:28.09mm;min-width: 28.09mm;\">(\d+)</div>", response.text)
    if result:
        return result[0]
    else:
        return None


async def handle_bio(request):
    text = await request.text()
    try:
        body = json.loads(text or '{}')
    except json.JSONDecodeError:
        return web.Response(status=400)
    user = body.get('user', None)
    password = body.get('password', None)
    shop_num = body.get('shopNum', None)
    if user and password and shop_num is not None:
        text = bio(user=user, password=password, computer_name=shop_num) or '0'
    else:
        text = '0'
    return web.Response(text=text)


def basic_auth(username, password):
    auth_str = f'{username}:{password}'
    try:
        return base64.b64encode(auth_str.encode('utf-8')).decode('utf-8')
    except:
        return None


async def handle_basic_auth(request):
    text = await request.text()
    try:
        body = json.loads(text or '{}')
    except json.JSONDecodeError:
        return web.Response(status=400)
    username = body.get('username', None)
    password = body.get('password', None)
    if username and password is not None:
        text = basic_auth(username=username, password=password)
        if text is None:
            return web.Response(status=500)
    else:
        return web.Response(status=400)
    return web.Response(text=text)


async def handle_auth_get(request):
    email = request.rel_url.query.get('email', None)
    phone = request.rel_url.query.get('phone', None)
    user_info = {'state': False}

    conn = request.app['db']
    user = await conn.fetchrow('''
        SELECT * 
        FROM users 
        WHERE email = $1 OR phone = $2
    ''', email, phone)
    if user:
        user_info['state'] = True
        user_info['full_name'] = user['full_name']
        user_info['position'] = user['position']
    return web.Response(text=json.dumps(user_info), charset='utf-8')


def get_user_info(username, password):
    try:
        server = Server('10.0.7.122', get_info=ALL)
        conn = Connection(server=server, user=f'dixy\\{username}', password=password, authentication=NTLM)
        conn.bind()
        conn.search('dc=Dixy,dc=local', f'(&(objectclass=person)(sAMAccountName={username}))',
                    attributes=['title', 'cn'])
    except:
        return None
    if conn.entries:
        user = conn.entries[0]
        return {
            'full_name': str(user['cn']),
            'position': str(user['title'])
        }
    else:
        return None


async def handle_auth_post(request):
    text = await request.text()
    try:
        body = json.loads(text or '{}')
    except json.JSONDecodeError:
        return web.Response(status=400)
    username = body.get('username', None)
    password = body.get('password', None)
    email = body.get('email', None)
    phone = body.get('phone', None)
    if (username and password is not None) and ((email or phone) is not None):
        user = get_user_info(username=username, password=password)
        if user:
            user['email'] = email
            user['phone'] = phone
            conn = request.app['db']
            await conn.execute('''
                INSERT INTO Users(phone, email, full_name, position)
                VALUES($1, $2, $3, $4)
            ''', user['phone'], user['email'], user['full_name'], user['position'])
        else:
            return web.Response(status=401)
    else:
        return web.Response(status=400)
    return web.Response(text=text)


async def init_app():
    app = web.Application()
    db = await asyncpg.connect(user=os.environ['POSTGRES_USER'], password=os.environ['POSTGRES_PASSWORD'],
                               database=os.environ['POSTGRES_DB'], host='localhost', port=5432)
    app['db'] = db
    app.add_routes([web.post('/laps', handle_laps)])
    app.add_routes([web.post('/bio', handle_bio)])
    app.add_routes([web.post('/basic_auth', handle_basic_auth)])
    app.add_routes([web.post('/auth', handle_auth_post)])
    app.add_routes([web.get('/auth', handle_auth_get)])

    return app


if __name__ == '__main__':
    web.run_app(init_app(), port=4444)
