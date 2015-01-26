# -*- coding: utf-8 -*-
import sys
if sys.getdefaultencoding() != 'utf-8':
    reload(sys)
    sys.setdefaultencoding('utf-8')

import json,requests
# all the imports
import sqlite3 , string , os , logging , Colorer
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash,jsonify
from contextlib import closing
from logging.handlers import RotatingFileHandler
from werkzeug.contrib.fixers import ProxyFix

from datetime import timedelta
from flask import make_response , current_app
from functools import update_wrapper

# for creating gcode
from multiprocessing import Process
import time

# configuration
DATABASE = './pt_tab.db'
DEBUG = True
SECRET_KEY = '987654321'
USERNAME = 'admin'
PASSWORD = '123456'
SU_CON = None

app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('FLASKR_SETTINGS', silent=True)


def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

def get_print_now_id():
    pt = g.db.execute('select print_id from prints where status=3')
    printnow=pt.fetchall()
    return printnow[0][0] if printnow else None


def crossdomain(origin=None, methods=None, headers=None,
                max_age=21600, attach_to_all=True,
                automatic_options=True):
    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    if headers is not None and not isinstance(headers, basestring):
        headers = ', '.join(x.upper() for x in headers)
    if not isinstance(origin, basestring):
        origin = ', '.join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        if methods is not None:
            return methods

        options_resp = current_app.make_default_options_response()
        return options_resp.headers['allow']

    def decorator(f):
        def wrapped_function(*args, **kwargs):
            if automatic_options and request.method == 'OPTIONS':
                resp = current_app.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != 'OPTIONS':
                return resp

            h = resp.headers

            h['Access-Control-Allow-Origin'] = origin
            h['Access-Control-Allow-Methods'] = get_methods()
            h['Access-Control-Max-Age'] = str(max_age)
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            return resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)
    return decorator


@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()

# 首頁
@app.route('/')
def show_index():
    title="歡迎來到 CatchU"
    # app.logger.info('User at index')
    # app.logger.warn('yyyy')
    # app.logger.error('zzzz')
    app.logger.warn('[Hello] Welcome user '+request.remote_addr)
    return render_template('index.html',title=title,printnow=get_print_now_id())


# 列印進度
@app.route('/show_print')
def show_entries(grbl=0):
    title="列印進度"

    if not session.get('logged_in'):
        cur = g.db.execute('select create_time, print_id, stu_id, status from prints where status<>"4" order by status desc,create_time asc')
        entries = [dict(create_time=row[0],print_id=row[1],stu_id=row[2],status=row[3]) for row in cur.fetchall()]
    else:
        cur = g.db.execute('select create_time, print_id, stu_id, name, phone, status from prints where status<>"4" order by status desc,create_time asc')
        entries = [dict(create_time=row[0],print_id=row[1],stu_id=row[2],name=row[3],phone=row[4],status=row[5]) for row in cur.fetchall()]
    # return render_template('show_entries.html', entries=entries,printnow=printnow)
    return render_template('show_entries.html', entries=entries,printnow=get_print_now_id(),title=title,grbl=grbl)


# 新增頁面
@app.route('/add', methods=['GET','POST'])
def add_entry():
    error=None
    if request.method == 'POST':
        if request.form['stu_id'] != "" or request.form['name'] != "" or request.form['phone'] != "" :
            totalmax = g.db.execute("select count(*) from prints")
            totalmax = totalmax.fetchone()
            totalmax = "%03d" %(totalmax[0]+1)

            g.db.execute('insert into prints (print_id, stu_id, name, phone, status) values (?,?,?,?,?)',
                         [totalmax + request.form['stu_id'][-3:], request.form['stu_id'], request.form['name'],request.form['phone'],0])
            g.db.commit()

            # Information for html
            flash('請記下您的列印件號： '+totalmax + request.form['stu_id'][-3:],'alert-success btn-lg flash-bg')
            app.logger.info('[Print] Add Printing <PID:'+totalmax + request.form['stu_id'][-3:]+'>')

            # Background creating gcode
            print_id=totalmax + request.form['stu_id'][-3:]
            gcode = Process(target=my_function, args=(print_id,))
            gcode.start()

            return redirect(url_for('show_entries'))
        else:
            error='您輸入的資料有誤。'
    title="新增列印"
    return render_template('add.html',title=title,error=error,printnow=get_print_now_id())

# 搜尋/修改單
@app.route('/pid', methods=['GET', 'POST'])
def search_entry():
    error=None
    app.config['SU_CON'] = None

    if request.method == 'POST':
        if request.form['phone'] != "" or request.form['print_id'] != "" :

            search_pid=g.db.execute('select print_id, phone from prints where print_id="'+request.form['print_id']+'" and phone="'+request.form['phone']+'"')
            search_pid=search_pid.fetchone()

            # 顯示列印單讓User修改
            if search_pid :
                app.config['SU_CON'] = "SU"
                return redirect(url_for('edit_pid_entry',print_id=str(request.form['print_id'])))
            error='您輸入的資料有誤。'
        else:
            error='您輸入的資料有誤。'

    title="請輸入列印單號"
    return render_template('search.html',error=error,title=title,printnow=get_print_now_id())


@app.route('/pid/<print_id>', methods=['GET', 'POST'])
def edit_pid_entry(print_id):
    if session.get('logged_in') or app.config['SU_CON'] == "SU" :

        if request.method == 'POST':
            g.db.execute('update prints set stu_id="'+request.form['stu_id']+'", name="'+request.form['name']+'", phone="'+request.form['phone']+'" where print_id="'+print_id+'"')
            g.db.commit()
            flash('資料更新完畢！')
            return redirect(url_for('show_entries'))

        title="修改列印單"
        search_pid = g.db.execute('select create_time, print_id, stu_id, name, phone, status  from prints where print_id="'+print_id+'"')
        entries = [dict(create_time=row[0],print_id=row[1],stu_id=row[2],name=row[3],phone=row[4],status=row[5]) for row in search_pid.fetchall()]
        app.config['SU_CON'] = None
        return render_template('show.html',entries=entries,title=title,printnow=get_print_now_id())
    else:
        abort(401)


# POST修改列印單
@app.route('/manage',methods=['POST'])
def manage_entry():
    if request.method == 'POST':

        # for hack
        search_pid=g.db.execute('select print_id from prints where print_id="'+request.form['print_id']+'"')
        search_pid=search_pid.fetchone()
        if not search_pid :
            abort(401)

        # which button press down
        if request.form['submit'] == "修改":
            return redirect(url_for('edit_pid_entry',print_id=str(request.form['print_id'])))
        elif request.form['submit'] == "刪除":
            # delete from prints where print_id="002011";
            g.db.execute('delete from prints where print_id="'+search_pid[0]+'"')
            g.db.commit()
            flash('刪除成功。','alert-danger')

            app.logger.error('[Print] Delete Printing <PID:'+search_pid[0]+'>')
            return redirect(url_for('show_entries'))
        elif request.form['submit'] == "列印":
            print_now_pid=g.db.execute('select print_id from prints where status="3"')
            print_now_pid=print_now_pid.fetchone()

            if not print_now_pid:
                g.db.execute('update prints set status="3" where print_id="'+search_pid[0]+'"')
                g.db.commit()
                app.logger.warn('[Print] Start Printing <PID:'+search_pid[0]+'>')
                return redirect(url_for('sendgcode',print_id=search_pid[0]))
            else:
                flash('尚有列印工作進行中。','alert-danger')
                return redirect(url_for('show_entries'))
        elif request.form['submit'] == "停止":
            g.db.execute('update prints set status="1" where print_id="'+search_pid[0]+'"')
            g.db.commit()
            app.logger.error('[Print] Stop Printing <PID:'+search_pid[0]+'>')
            return redirect(url_for('show_entries'))
        elif request.form['submit'] == "領取":
            g.db.execute('update prints set status="4" where print_id="'+search_pid[0]+'"')
            g.db.commit()
            app.logger.info('[Print] Receive Printing <PID:'+search_pid[0]+'>')
            return redirect(url_for('show_entries'))
        else:
            abort(401)


# 登入/出
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME'] or request.form['password'] != app.config['PASSWORD']:
            error = '您輸入的資料有誤。'
            app.logger.error('[Login] Permission denied ('+request.remote_addr+')')
        else:
            session['logged_in'] = True
            flash('您已經成功登入。')
            return redirect(url_for('show_entries'))

    title="登入後台"
    if session.get('logged_in'):
        flash('您已經登入，請勿重新登入。','alert-danger')
        return redirect(url_for('show_entries'))
    return render_template('login.html', error=error, title=title,printnow=get_print_now_id())



@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('您已經成功登出。')
    return redirect(url_for('show_index'))

### Creating Gcode ###
def gcode_created(print_id):
    time.sleep(5)
    print print_id

    g.db = connect_db()

    g.db.execute('update prints set status="1" where print_id="'+print_id+'"')
    g.db.commit()
    app.logger.info('[Gcode] Creating Done <PID:'+print_id+'>')

    db = getattr(g, 'db', None)
    if db is not None:
        db.close()


###################################
## ████   █████  ██   ██   █████ ##
## █   █  █      █ █ █ █   █   █ ##
## █    █ ████   █  █  █   █   █ ##
## █   █  █      █  █  █   █   █ ##
## ████   █████  █     █   █████ ##
###################################

######### for demo #########
@app.route('/show_print/demo/')
def set_demo():
    if not session.get('logged_in'):
        abort(401)
    g.db.execute('update prints set status="2" where status="3"')
    g.db.commit()
    return redirect(url_for('show_entries'))
######### for demo #########

#======== for test ========#
@app.route('/sendgcode/<print_id>')
@crossdomain(origin="*")
def sendgcode(print_id):
    if not session.get('logged_in'):
        abort(401)

    val="G0 X0 \nG0 X1"
    # url = 'http://192.168.0.102:8080/api/uploadGcode'
    payload = {'val': val}
    # headers = {'content-type': 'application/json'}
    # r = requests.post(url, data=payload, headers=headers)
    # flash('列印資訊已傳送!'+print_id)
    return render_template('sendgcode.html', data=payload)

#======== for test ========#

# app.wsgi_app = ProxyFix(app.wsgi_app)

if __name__ == '__main__':

    ###### for demo ######
    os.system('cat ./demo_tab.db > ./pt_tab.db')
    # os.system('open http://127.0.0.1:5000/')
    ###### for demo ######

    ###### for LOG ######
    handler = RotatingFileHandler('foo.log', maxBytes=10000, backupCount=1)
    formatter = logging.Formatter("%(asctime)s - %(message)s")
    handler.setLevel(logging.INFO)
    handler.setFormatter(formatter)
    app.logger.addHandler(handler)
    ###### for LOG ######

    app.run(host='0.0.0.0',port=80)
    # app.run()

