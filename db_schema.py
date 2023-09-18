from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, current_user, logout_user, login_required, UserMixin
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']= 'sqlite:///example.db'
# create the database interface
db = SQLAlchemy(app)

# a model of a user for the database
class UserAttendee(db.Model, UserMixin):
    __tablename__='usersa'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True)
    #password = db.Column(db.String(20))
    password_hash=db.Column(db.String(50))
    email = db.Column(db.String(50), unique=True)
    userType = db.Column(db.String(10))
    is_organiser = db.Column(db.Boolean, default=False)
    confirmed= db.Column(db.Boolean, default=False)



    def __init__(self, username, password_hash, email, userType):  
        self.username=username
        self.password_hash=password_hash #i added
        self.email=email
        self.userType=userType

    def get_id(self):
        return self.id
    
    @staticmethod
    def getUser(id):
        return UserAttendee.allUsers[id]
    

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False
    
    def is_organiser(self):
        return self.userType == 'organiser'
    
    @staticmethod
    def loginUser(username, password):
        userRecord = UserAttendee.query.filter_by(username=username).first()

        if not userRecord:
            return None
        #print(user)
        isValid = check_password_hash(userRecord.password_hash, password)
        if isValid:
            user = UserAttendee(userRecord.id, userRecord.username, userRecord.password_hash)
            UserAttendee[userRecord.id] = user
            return user

# a model of a user for the database
class UserOrganiser(db.Model, UserMixin):
    __tablename__='userso'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True)
    #password = db.Column(db.String(20))
    password_hash=db.Column(db.String(50))
    email = db.Column(db.String(50), unique=True)
    userType = db.Column(db.String(10))
    is_organiser = db.Column(db.Boolean, default=True)  # set default value to True
    confirmed= db.Column(db.Boolean, default=False)#is the user's email confirmed?


    def __init__(self, username, password_hash, email, userType):  
        self.username=username
        self.password_hash=password_hash #i added
        self.email=email
        self.userType=userType
        ##self.is_authenticated = True
        ##self.is_active = True
        ##self.is_anonymous = False

    def get_id(self):
        return self.id
    
    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False
    
    def is_organiser(self):
        return self.userType == 'organiser'
    
    @staticmethod
    def getUser(id):
        return UserOrganiser.allUsers[id]
    
    @staticmethod
    def loginUser(username, password):
        userRecord = UserOrganiser.query.filter_by(username=username).first()

        if not userRecord:
            return None
        #print(user)
        isValid = check_password_hash(userRecord.password_hash, password)
        if isValid:
            user = UserOrganiser(userRecord.id, userRecord.username, userRecord.password_hash)
            UserOrganiser[userRecord.id] = user
            return user
        
# a model of a event for the database
class Event(db.Model):
    __tablename__ = 'events'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500))
    start_time = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(100))
    organiser_id = db.Column(db.Integer, db.ForeignKey('userso.id'))
    organiser = db.relationship('UserOrganiser', backref='events')
    capacity = db.Column(db.Integer, nullable =False)
    availableTickets = db.Column(db.Integer, nullable =False)
    is_cancelled = db.Column(db.Boolean, default=False)
    duration = db.Column(db.Integer)
    #with backref relationship I can access all the events associated with that organizer by accessing organiser.events.


    def __init__(self, title, description, start_time, location, organiser_id, capacity, availableTickets, is_cancelled, duration):
        self.title = title
        self.description = description
        self.start_time = start_time
        self.location = location
        self.organiser_id = organiser_id
        self.capacity = capacity
        self.availableTickets = availableTickets
        self.is_cancelled = is_cancelled
        self.duration = duration


class Ticket(db.Model):
    __tablename__ = 'tickets'
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'))
    event = db.relationship('Event', backref='tickets')
    usernameO = db.Column(db.String, db.ForeignKey('userso.username'))
    userO = db.relationship('UserOrganiser', backref='tickets')
    username = db.Column(db.String, db.ForeignKey('usersa.username'))
    userA = db.relationship('UserAttendee', backref='tickets')
    email = db.Column(db.String(120))
    ticketsBought = db.Column(db.Integer, nullable =False)
    #with backref relationship I can access all the events associated with that organizer by accessing organiser.events.


    def __init__(self, event_id, usernameO, username, email, ticketsBought):
        self.event_id = event_id
        self.usernameO=usernameO
        self.username=username
        self.email=email
        self.ticketsBought = ticketsBought


db.create_all()
# put some data into the tables
def dbinit():
    user_list = [
        ]
    db.session.add_all(user_list)

    # commit all the changes to the database file
    db.session.commit()
