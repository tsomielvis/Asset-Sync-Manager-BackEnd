from flask import Flask,session
from flask_restful import Api
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_session import Session
from datetime import timedelta
app = Flask(__name__)
import os
CORS(app,support_credentials=True)
app.secret_key = 'Asset-Sync-Manager'

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['SECURITY_REGISTERABLE'] = True
app.config['SECURITY_PASSWORD_SALT'] = 'somesalt'
app.config['SECURITY_SEND_REGISTER_EMAIL'] = False
app.config['SECURITY_CONFIRMABLE'] = True
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SECRET_KEY'] = 'authtests'
app.config['JSONIFY_PRETTYPRINT_REGULAR']= True
app.config['SESSION_PERMANENT'] = True
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_FILE_THRESHOLD'] = 100
app.config['SESSION_COOKIE_SECURE'] = True
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=7)
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

app.json.compact = False

app.permanent_session_lifetime = timedelta(minutes=60)

db = SQLAlchemy()
migrate = Migrate(app, db)
db.init_app(app)

Session(app)
bcrypt = Bcrypt(app)
api = Api(app)

