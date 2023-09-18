from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from flask import Flask, render_template, request, redirect, url_for


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']= 'sqlite:///example.db'
# create the database interface
db = SQLAlchemy(app)

# a model of a user for the database
class User(db.Model, UserMixin):
    __tablename__='users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True)
    password = db.Column(db.String(20))

    def __init__(self, username, password):  
        self.username=username
        self.password=password #i added

# a model of a list for the database
# it refers to a user
class List(db.Model):
    __tablename__='lists'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text())
    user_id = db.Column(db.Integer)  # this ought to be a "foreign key"

    def __init__(self, name, user_id):
        self.name=name
        self.user_id = user_id

# a model of a list item for the database
# it refers to a list
class ListItem(db.Model):
    __tablename__='items'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text())
    list_id = db.Column(db.Integer)  # this ought to be a "foreign key"

    def __init__(self, name, list_id):
        self.name=name
        self.list_id=list_id

# put some data into the tables
def dbinit():
    user_list = [
        User("Felicia", 'them'), 
        User("Petra", 'any'),
        User("Manpreet", 'myself')
        ]
    db.session.add_all(user_list)
    

    # find the id of the user Felicia
    felicia_id = User.query.filter_by(username="Felicia").first().id
    manpreet_id = User.query.filter_by(username="Manpreet").first().id
     

    all_lists = [
        List("Shopping",felicia_id), 
        List("Chores",felicia_id),
        List("Things", manpreet_id),
        #add a comment here that a comma wasnt present in second line i inserted it
        List("Work",manpreet_id)
        ]
    db.session.add(List("cwks",3)) # it displays cwks at the top of the list.
    db.session.add_all(all_lists)

    # find the ids of the lists Chores and Shopping

    chores_id = List.query.filter_by(name="Chores").first().id
    shopping_id= List.query.filter_by(name="Shopping").first().id
    work_id=List.query.filter_by(name="Work").first().id
    things_id=List.query.filter_by(name="Things").first().id

    all_items = [
        ListItem("Potatoes",shopping_id), 
        ListItem("Shampoo", shopping_id),
        ListItem("Wash up",chores_id), 
        ListItem("Vacuum bedroom",chores_id),
        ListItem("CS139",work_id),
        ListItem("CWKs", things_id)
        ]

    db.session.add_all(all_items)

    # commit all the changes to the database file
    db.session.commit()
