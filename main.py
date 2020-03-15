from flask import Flask,render_template,request,session,redirect,flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug import secure_filename
from datetime import datetime
import json
import os
from flask_mail import Mail
import math


app = Flask(__name__)
# Flask App initialize here
app.secret_key = 'Man365man'

# open config.json file here so we can import content to main.py file
with open("config.json",'r') as c:
    params = json.load(c)["params"]

local_server = params["local_server"]

if (local_server):
    app.config['SQLALCHEMY_DATABASE_URI'] = params["local_uri"]
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params["prod_uri"]


db = SQLAlchemy(app) #Intialize the db variable

app.config["upload_file"] = params["uploader_location"]

app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT='465',
    MAIL_USE_SSL=True,
    MAIL_DEBUG=app.debug,
    MAIL_USERNAME=params["gmail-user"],
    MAIL_PASSWORD=params["gmail-password"]
)

mail = Mail(app)
# initialize the mail app

class Registration(db.Model):
    reg_id = db.Column(db.Integer,primary_key=True)
    Name = db.Column(db.String(50),unique=False, nullable=False)
    email = db.Column(db.String(50),unique=True,nullable=False)
    Password = db.Column(db.String(50),unique=True,nullable=True)
    Phone = db.Column(db.String(50), unique=True, nullable=False)
    Country = db.Column(db.String(50), unique=True, nullable=False)
    Services = db.Column(db.String(50), unique=True, nullable=False)
    Date = db.Column(db.String(50), unique=True, nullable=True)

class Services(db.Model):
    ser_no = db.Column(db.Integer, primary_key=True)
    ser_title = db.Column(db.String(50), unique=False, nullable=False)
    slug = db.Column(db.String(50), unique=True, nullable=False)
    content = db.Column(db.String(50), unique=True, nullable=False)
    img_file = db.Column(db.String(50),unique=True,nullable=False)





@app.route("/")
def home():
    return render_template('index.html',params=params)


@app.route("/registration",methods=['GET','POST'])
def registration():

    if request.method == 'POST':
        name1 = request.form.get('name')
        email1 = request.form.get('email')
        password1 = request.form.get('pass')
        phone1 = request.form.get('phone')
        country1 = request.form.get('country')
        services1 = request.form.get('services')
        entry = Registration(Name=name1,email=email1,Password = password1,Phone=phone1,Country=country1,Services=services1,Date=datetime.now())
        db.session.add(entry)
        db.session.commit()
        mail.send_message("Message from username:" + name1,
                    sender = email1,
                    recipients  = [params["gmail-user"]],
                    body = services1 + "\n" + email1
                  )


    return render_template('registration.html',params =params)


# slug creation
@app.route("/services/<string:service_item>",methods=['GET'])
def service_route(service_item):
    # this is process to fetch all data from database
    services = Services.query.filter_by(slug = service_item).first()



    return render_template('services_slug.html',params =params,services=services)


@app.route("/services", methods=['GET'])
def services():
    services_items = Services.query.filter_by().all()

    # print(len(services_items))
    # [0:params['no_of_services']]
    last = math.ceil(len(services_items)/int(params['no_of_services']))
    print(last)
    page = request.args.get('page')
    print(page)
    if (not str(page).isnumeric()):
        page = 1
    page = int(page)
    services_items = services_items[(page-1)*int(params['no_of_services']): (page-1)*int(params['no_of_services']) + int(params['no_of_services'])]
    # print(len(services_items))
    # print(type(page))
    if(page == 1):
        prev = "#"
        next1 = "/services?page=" + str(page+1)
        # return render_template('services.html', params=params, services_items=services_items, prev=prev, next=next)
    elif (page == last):
        prev = "/services?page=" + str(page-1)
        next1 = "#"
        # return render_template('services.html', params=params, services_items=services_items, prev=prev, next=next)
    else:
        prev = "/services?page=" + str(page-1)
        next1 = "/services?page=" + str(page+1)
    return render_template('services.html',params=params,services_items=services_items,prev = prev,next1 = next1)


@app.route("/admin",methods = ['GET','POST'])
def admin():
    services_items = Services.query.filter_by().all()
    if ('user' in session and session['user']==params['admin_user']):
        return render_template('dashboard.html', params=params,services_items=services_items)

    if request.method == 'POST':
        username = request.form.get("uname")
        userpass = request.form.get("pass")
        if username == params['admin_user'] and userpass == params['admin_password']:
            session['user']= username
            return render_template('dashboard.html', params=params,services_items=services_items)
        else:
            flash("Wrong password or user")



    return render_template('admin.html',params =params,services_items=services_items)

@app.route("/edit/<string:serviceno>",methods = ['GET','POST'])
def edit(serviceno):
    if ('user' in session and session['user'] == params['admin_user']):
        if request.method == 'POST':
            service_title = request.form.get('ser_title')
            service_content = request.form.get('ser_content')
            service_slug = request.form.get('ser_slug')
            service_image = request.form.get('ser_img')

            if serviceno == '0':
                services_add = Services(ser_title=service_title,content=service_content,slug=service_slug,img_file=service_image)
                db.session.add(services_add)
                db.session.commit()
            else:
                services_modify=Services.query.filter_by(ser_no=serviceno).first()
                services_modify.ser_title = service_title
                services_modify.content = service_content
                services_modify.slug = service_slug
                services_modify.img_file = service_image
                db.session.commit()
                return redirect('/edit/'+serviceno)
        services_modify = Services.query.filter_by(ser_no=serviceno).first()

        return render_template('edit.html', params=params,serviceno=serviceno,services_modify=services_modify)


@app.route("/delete/<string:serviceno>",methods = ['GET','POST'])
def delete(serviceno):
    if ('user' in session and session['user'] == params['admin_user']):
        services = Services.query.filter_by(ser_no=serviceno).first()
        db.session.delete(services)
        db.session.commit()
        return redirect('/admin')


@app.route("/uploader", methods = ['GET','POST'])
def uploader():
    if ('user' in session and session['user'] == params['admin_user']):
        if request.method == 'POST':
            f = request.files["file1"]
            f.save(os.path.join(app.config["upload_file"], secure_filename(f.filename)))
            return "Uploaded successfully"





@app.route("/logout",methods = ['GET','POST'])
def logout():
    session.pop('user')

    return render_template('admin.html', params=params)


@app.route("/users",methods = ['GET','POST'])
def all_users():

    all_user = Registration.query.filter_by().all()
    if ('user' in session and session['user'] == params['admin_user']):
        return render_template('users.html', params=params,all_user=all_user)



@app.route("/login",methods = ['GET','POST'])
def login():
    # registered_user = Registration.query.filter_by().all()


    if request.method == 'POST':
        username = request.form.get('rname')
        userpass = request.form.get('rpass')
        registered_user = Registration.query.all()
        registered_email = Registration.query.get(1)
        print(registered_email.email)
        # print(registered_user.Password)
    #     entry = Registration(email=username, Passwprd=userpass)
    #
    #     if username == registered_user['email'] and userpass == registered_user['Password']:
    #         return render_template('users.html', params=params, all_user=all_user)
    #
        return render_template('loginuser.html', params=params,registered_user=registered_user)

    return render_template('loginuser.html', params=params)



if __name__ == '__main__':
    app.run(debug=True)