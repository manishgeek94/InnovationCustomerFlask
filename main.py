from flask import Flask,render_template,request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json
from flask_mail import Mail


app = Flask(__name__)
# Flask App initialize here



# open config.json file here so we can import content to main.py file
with open("config.json",'r') as c:
    params = json.load(c)["params"]

local_server = params["local_server"]

if (local_server):
    app.config['SQLALCHEMY_DATABASE_URI'] = params["local_uri"]
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params["prod_uri"]


db = SQLAlchemy(app) #Intialize the db variable


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
        phone1 = request.form.get('phone')
        country1 = request.form.get('country')
        services1 = request.form.get('services')
        entry = Registration(Name=name1,email=email1,Phone=phone1,Country=country1,Services=services1,Date=datetime.now())
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


@app.route("/services")
def services():

    services_items = Services.query.filter_by().all()

    return render_template('services.html',params =params,services_items=services_items)


@app.route("/admin")
def admin():
    return render_template('admin.html',params =params)



app.run(debug=True)