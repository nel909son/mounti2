from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail 

DB_NAME = "site.db"


def create_database(app):
    
    db.create_all(app=app)
    print('Created Database!')


app = Flask(__name__)
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'


db.init_app(app)
from .models import User

create_database(app)


login_manager.init_app(app)

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))




from website import routes