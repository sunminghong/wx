#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/3/28 9:47
# @Author  : dongdong Zou
# @File    : test.py.py
# @license : Copyright(C), 安锋游戏

import urllib.parse
import requests
from flask import Flask, request, jsonify, session, url_for
from flask import render_template
from flask import abort, redirect
from common_utils.common import getDate
from common_utils.config import Config
from common_utils.database import mysql_client
import uuid

from libs.recommend_articles import init, get_similar_model

app = Flask(__name__)
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

limit_size = 20
client_id = 110
port = 22222
base_url = 'https://i.anfeng.com'


debug = False
if debug:
    host = '127.0.0.1'
    redirect_url = 'http://%s:%s/config' % (host, port)
else:
    host = '172.18.253.229'
    redirect_url = 'http://toutiao.qcwanwan.com/config'

mysql = mysql_client(Config().get_config('mysql', 'host'),
                     Config().get_config('mysql', 'port'),
                     Config().get_config('mysql', 'database'),
                     Config().get_config('mysql', 'username'),
                     Config().get_config('mysql', 'password'))

model = get_similar_model()

# 存储分页条件
_wh = []
@app.route('/test')
def test():
    result = init(model, ['微信'])
    print(type(result))
    return jsonify(result)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        page = request.args.get('page', 0)
        offset = int(page) * limit_size

        where = ''
        order = 'a.create_time desc'
        if 'uid' in session:
            uid = session['uid']
            config = get_user_config(uid)
            if config and config['keywords']:

                ids = init(model, str(config['keywords']).split(','))
                if len(ids) > 0:
                    where += ' and a.id in (%s)' % ','.join(ids)
                    order = 'field(a.id, %s)' % ','.join(ids)
                if config['media']:
                    medias = ','.join(list(map(str, config['media'])))
                    where += ' and a.media in (%s)' % (medias)

        result = get_data_list(where=where, offset=offset, order=order,
                               select='a.id,a.title,a.author,a.summary,a.create_time', limit=limit_size)

        if page == 0:
            _wh.clear()
        dataList = []
        for item in result:
            dataList.append({
                'id': item['id'],
                'title': item['title'],
                'author': item['author'],
                'mname': item['mname'],
                'summary': item['summary'],
                'create_time': getDate(item['create_time'])
            })
            _wh.append(str(item['id']))
        if 'uid' in session:
            session["uid_where_%s" % session['uid']] = ','.join(_wh)
        else:
            session['uid_where_default'] = ','.join(_wh)

        return http_response(data=dataList)
    else:
        return render_template('index.html')


@app.route('/detail/<int:id>')
def getData(id):
    if not id:
        return http_response(code=0, msg='参数有误')
    else:
        sql = "select a.*,m.name as mname from af_articles a left join af_media m on m.id = a.media where a.id=%s" % id
        result = mysql.query(sql)
        key = session['uid'] if 'uid' in session else 'default'
        prev, next = page_data(key, id)

        if result and result[0]:
            current = {
                'id': result[0]['id'],
                'origin_url': result[0]['origin_url'],
                'title': result[0]['title'],
                'content': result[0]['content'],
                'media': result[0]['mname'],
                'create_time': getDate(result[0]['create_time']),
                'prev': prev,
                'next': next
            }
            return http_response(data=current)
        else:
            return http_response(code=0, msg='数据为空')


@app.route('/<int:id>')
def detail(id):
    if not id:
        abort(404)
    else:
        sql = "select a.*,m.name as mname from af_articles a left join af_media m on m.id = a.media where a.id=%s" % id
        result = mysql.query(sql)
        key = session['uid'] if 'uid' in session else 'default'
        prev, next = page_data(key, id)

        if result and result[0]:
            return render_template('detail.html', result=result[0], prev=prev, next=next)
        else:
            abort(404)


@app.route('/config', methods=['GET', 'POST'])
def config():
    if request.method == 'POST':
        if 'uid' not in session:

            state = uuid.uuid1().split('-')[0]
            session['state'] = state

            return redirect(base_url + '/anfengauth/get_code?client_id=%s&state=%s&redirect_uri=%s'
                            %(client_id, state, redirect_url))
        else:
            uid = session['uid']
            keywords = request.form['keywords']
            if keywords:
                keywords = str(keywords).replace('，', ',')
            media = request.values.getlist('media')
            media = ','.join(media) if media else ''

            insert_sql = """insert into af_config values %s
            ON DUPLICATE KEY UPDATE
            keywords = values(keywords), 
            media = values(media) 
            """ % ("('{uid}', '{keywords}','{media}')".format(uid=uid, keywords=keywords, media=media))

            res = mysql.execute(insert_sql)

        return redirect('/')
    else:
        code = request.args.get('code')
        if 'uid' not in session and not code:

            state = str(uuid.uuid1()).split('-')[0]
            session['state'] = state

            return redirect(base_url + '/anfengauth/get_code?client_id=%s&state=%s&redirect_uri=%s'
                            %(client_id, state, redirect_url))

        if code:
            token = get_token(code)
            print('response token: ', token, type(token))
            if not isinstance(token, str):
                return redirect('/config')

            ucuser = get_user(token)
            if ucuser.__contains__('status') and ucuser.get('status') == 0:
                pass
            else:
                session['user'] = ucuser
                session['uid'] = ucuser.get('uid')
            return redirect('/config')
        else:
            sql = "select * from af_media where status='normal'"
            result = mysql.query(sql)
            dataList = []
            for item in result:
                dataList.append({
                    'id': item['id'],
                    'name': item['name']
                })

            config = get_user_config(session['uid'])
            return render_template('config.html', dataList=dataList, config=config)


@app.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html'), 404


def page_data(key, current_id):
    if ('uid_where_%s' % key) in session:
        ids = str(session['uid_where_%s' % key]).split(',')
        total = len(ids)
        current_index = 0
        for i in range(total):
            if str(ids[i]) == str(current_id):
                current_index = i
                break
        if current_index == 0:
            prev = ids[current_index + 1]
            next = 0
        elif current_index == (total - 1):
            prev = 0
            next = ids[current_index - 1]
        else:
            prev = ids[current_index + 1]
            next = ids[current_index - 1]
        return prev, next
    else:
        return 0,0


def get_data_list(where, offset=0, limit=20, order='create_time desc', select='*'):

    _where = 'where 1=1 %s' % where

    sql = "select %s,m.name as mname from af_articles a " \
          "left join af_media m on m.id = a.media %s order by %s limit %s, %s" \
          % (select, _where, order, offset, limit if limit else limit_size)
    print(_where)
    res = mysql.query(sql)
    return res


def get_user_config(uid):
    sql = "select * from af_config where uid = %s limit 1" % uid
    data_list = mysql.query(sql)
    result = {}
    if data_list and data_list[0]:
        result['uid'] = data_list[0]['uid']
        result['keywords'] = data_list[0]['keywords']
        rs = str(data_list[0]['media']).split(',') if data_list[0]['media'] else []
        result['media'] = list(map(int, rs))
    return result


def get_token(code):
    if not code:
        return {'status': 0, 'msg': 'code为空'}
    res = post_reuqest('/anfengauth/get_token', {'code': code, 'client_id': client_id,
                                                 'state': session['state'], 'redirect_uri': redirect_url})
    res = res[1]
    if res and res.get('status') == 1:
         return dict(res.get('data')).get('access_token')
    else:
        return {'status': 0, 'msg': res.get('info')}


def get_user(token):
    if not token:
        return {'status': 0, 'msg': 'token为空'}
    res = post_reuqest('/anfengauth/get_user_info', {'access_token': token})

    res = res[1]
    user = {}
    if res and res.get('status') == 1:
        user = res.get('data')
    else:
        return {'status': 0, 'msg': res.get('info')}

    return user


def post_reuqest(url=None, data=None):
    url = base_url + url
    data_str = ""
    for key in data.keys():
        k = urllib.parse.quote(key)
        v = urllib.parse.quote(str(data[key]))
        data_str += "%s=%s&" % (k, v)

    print('请求API: ', url, ' data: ', data_str)
    r = requests.get(url + '?' + data_str)
    return r.status_code, r.json()


def http_response(code=1, msg='success', data=None, http_code=200):
    response_data = {
        'code': code,
        'msg': msg,
        'data': data
    }
    return jsonify(response_data), http_code

if __name__ == '__main__':
    app.run(host=host, port=port, debug=True)








