# -*- coding: utf-8 -*-
import sys
if sys.getdefaultencoding() != 'utf-8':
    reload(sys)
    sys.setdefaultencoding('utf-8')

import cv2
import numpy as np,sys

import json,requests
# all the imports
import sqlite3 , string , os , logging , Colorer
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash,jsonify
from contextlib import closing
from logging.handlers import RotatingFileHandler
from werkzeug.contrib.fixers import ProxyFix
from werkzeug import secure_filename

import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# for creating gcode
from multiprocessing import Process
import time

import catchu

# configuration
DEMO=0
DATABASE = './pt_tab.db'
DEBUG = True
SECRET_KEY = '987654321'
USERNAME = 'admin'
PASSWORD = '123456'
SU_CON = None
HOSTWEB = 'http://120.117.73.74'
UPLOAD_FOLDER = './static/upload_pic/'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
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
    # recoding user ip
    # app.logger.warn('[Hello] Welcome user '+request.remote_addr)
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
        # Get form text
        stu_id = request.form['stu_id'].strip()
        name = request.form['name'].strip()
        phone = request.form['phone'].strip()
        user_file = request.files['file']

        if not stu_id or not name or not phone or not user_file or not allowed_file(user_file.filename):
            error=''
            if not stu_id:
                error+='學號 錯誤或未填寫。<br>'
            if not name:
                error+='姓名 錯誤或未填寫。<br>'
            if not phone:
                error+='手機 錯誤或未填寫。<br>'
            if not user_file or not allowed_file(user_file.filename):
                error+='檔案 錯誤。(限png,jpg,jpeg,gif)'

        else:

            totalmax = g.db.execute("select count(*) from prints")
            totalmax = totalmax.fetchone()
            totalmax = "%03d" %(totalmax[0]+1)
            print_id = totalmax + request.form['stu_id'][-3:]

            # Uploading Picture
            if user_file and allowed_file(user_file.filename):
                filename = secure_filename(user_file.filename)
                user_file.save(os.path.join(app.config['UPLOAD_FOLDER'], print_id+'_tmp.'+user_file.filename.rsplit('.', 1)[1]))
                # Resize image
                image_resize( print_id+'_tmp.'+user_file.filename.rsplit('.', 1)[1] )
                os.system('rm -rf '+app.config['UPLOAD_FOLDER']+print_id+'_tmp.'+user_file.filename.rsplit('.', 1)[1])

            # Creating Data
            g.db.execute('insert into prints (print_id, stu_id, name, phone, status) values (?,?,?,?,?)',
                         [print_id, request.form['stu_id'], request.form['name'],request.form['phone'],0])
            g.db.commit()

            # Information for html
            flash('請記下您的列印件號： '+print_id,'alert-success btn-lg flash-bg')
            app.logger.info('[Print] Add Printing <PID:'+print_id+'>')

            # Background creating gcode
            gcode = Process(target=gcode_done, args=(print_id,))
            gcode.start()

            return redirect(url_for('show_entries'))

    title="新增列印"
    return render_template('add.html',title=title,error=error,printnow=get_print_now_id())


@app.route('/edit', methods=['GET', 'POST'])
def resize():
    if request.method == 'POST':
        pass
    return render_template('resize.html')



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

        search_pid=g.db.execute('select print_id from prints where print_id="'+request.form['print_id']+'"')
        search_pid=search_pid.fetchone()

        if search_pid == None :
            flash('執行動作失敗，請聯絡管理者。','alert-danger')
            return redirect(url_for('show_entries'))

        # which button press down
        if request.form['submit'] == "修改":
            return redirect(url_for('edit_pid_entry',print_id=str(request.form['print_id'])))
        elif request.form['submit'] == "刪除":
            g.db.execute('delete from prints where print_id="'+search_pid[0]+'"')
            g.db.commit()
            os.system('rm -rf '+app.config['UPLOAD_FOLDER']+search_pid[0]+'.jpg')
            flash('刪除成功。','alert-danger')

            app.logger.error('[Print] Delete Printing <PID:'+search_pid[0]+'>')
            return redirect(url_for('show_entries'))
        elif request.form['submit'] == "列印":
            print_now_pid=g.db.execute('select print_id from prints where status="3"')
            print_now_pid=print_now_pid.fetchone()

            if not print_now_pid:

                # 處理列印程序
                g.db.execute('update prints set status="3" where print_id="'+search_pid[0]+'"')
                g.db.commit()
                app.logger.error('[Print] Start Printing <PID:'+search_pid[0]+'>')

                val=compilegcode(search_pid[0])
                sendgd = Process(target=sendgcode, args=(search_pid[0],val,))
                sendgd.start()

                return redirect(app.config['HOSTWEB']+':8080')

            else:
                flash('尚有列印工作進行中。','alert-danger')
                return redirect(url_for('show_entries'))

        elif request.form['submit'] == "停止":

            stop_pid=g.db.execute('select print_id from prints where status="3" and print_id="'+request.form['print_id']+'"')
            stop_pid=stop_pid.fetchone()

            if stop_pid == None :
                flash('執行動作失敗，請聯絡管理者。','alert-danger')
                return redirect(url_for('show_entries'))

            g.db.execute('update prints set status="1" where print_id="'+search_pid[0]+'"')
            g.db.commit()
            app.logger.error('[Print] Stop Printing <PID:'+search_pid[0]+'>')
            return redirect(url_for('show_entries'))
        elif request.form['submit'] == "領取":

            done_pid=g.db.execute('select print_id from prints where status="2" and print_id="'+request.form['print_id']+'"')
            done_pid=done_pid.fetchone()

            if done_pid == None :
                flash('執行動作失敗，請聯絡管理者。','alert-danger')
                return redirect(url_for('show_entries'))


            g.db.execute('update prints set status="4" where print_id="'+search_pid[0]+'"')
            g.db.commit()
            app.logger.info('[Print] Receive Printing <PID:'+search_pid[0]+'>')
            return redirect(url_for('show_entries'))
        else:
            abort(401)


# 列印完畢
@app.route('/show_print/done/')
def print_done():
    if not session.get('logged_in'):
        abort(401)

    done_pid=g.db.execute('select print_id from prints where status="3"')
    done_pid=done_pid.fetchone()

    if done_pid == None :
        flash('執行動作失敗，請聯絡管理者。','alert-danger')
        return redirect(url_for('show_entries'))

    g.db.execute('update prints set status="2" where status="3"')
    g.db.commit()
    return redirect(url_for('show_entries'))


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

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(405)
def page_not_found(e):
    return render_template('404.html'), 405

@app.errorhandler(401)
def page_not_found(e):
    return render_template('404.html'), 401



###################################
## █████████████████████████████ ##
## █████████████████████████████ ##
## █████████████████████████████ ##
## █████████████████████████████ ##
###################################

### Test if file is allowed ###
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

### Creating Gcode ###
def gcode_done(print_id):
    catchu.Gcode_Creater(print_id)
    g.db = connect_db()
    g.db.execute('update prints set status="1" where print_id="'+print_id+'"')
    g.db.commit()
    app.logger.info('[Gcode] Creating Done <PID:'+print_id+'>')
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()

### Compile Gcode ###
def compilegcode(print_id):
    with open ('./static/gcodes/' + print_id + '.nc',"r") as myfile:
        val=myfile.read().replace('\n', '')
    return val

### Sending Gcode Module ###
def sendgcode(print_id,val):
    time.sleep(0.5)
    url = app.config['HOSTWEB']+':8080/api/uploadGcode'
    payload = {'val': val}
    headers = {'content-type': 'application/json'}
    r = requests.post(url, data=payload, headers=headers)

def image_resize(file_name):
    gimg = cv2.imread('./static/upload_pic/'+file_name,cv2.IMREAD_GRAYSCALE)
    width , height = gimg.shape
    width_max = 500
    height_max = 400
    if (height > height_max):
        width = int(width * float(height_max) / height)
        height = height_max

    if (width > width_max):
        height = int(height * float(width_max) / width)
        width = width_max
    image = cv2.resize(gimg,(height,width))
    cv2.imwrite('./static/upload_pic/'+file_name.rsplit('_', 1)[0]+'.jpg',image)



# app.wsgi_app = ProxyFix(app.wsgi_app)

if __name__ == '__main__':
    ###### for demo ######
    if app.config['DEMO'] :
        os.system('cat ./demo_tab.db > ./pt_tab.db')
    ###### for demo ######

    ###### for LOG ######
    handler = RotatingFileHandler('foo.log', maxBytes=10000, backupCount=1)
    formatter = logging.Formatter("%(asctime)s - %(message)s")
    handler.setLevel(logging.INFO)
    handler.setFormatter(formatter)
    app.logger.addHandler(handler)
    ###### for LOG ######

    app.logger.error('[Main] Starting server .....')
    app.run(host='0.0.0.0',port=80)
    # app.run(threaded=True)

